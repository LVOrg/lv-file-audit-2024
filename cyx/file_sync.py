import datetime
import os.path
import pathlib
import shutil
import threading
import time

import PIL
from fitz import fitz

import cy_docs
import cy_kit
from cyx.common.msg import MessageInfo, MessageService
from cyx.common.base import DbConnect
from cyx.common.file_storage_mongodb import MongoDbFileService
from cyx.models import FsFile, FsChunks
from cyx.media.image_extractor import ImageExtractorService
import bson
from typing import List
import cyx.common.temp_file

class FilesSync:
    def __init__(
            self,
            db_connect: DbConnect = cy_kit.singleton(DbConnect),
            temp_file: cyx.common.temp_file.TempFiles = cy_kit.singleton(cyx.common.temp_file.TempFiles),
            message_service: MessageService = cy_kit.singleton(MessageService),
            file_storage_service:MongoDbFileService = cy_kit.singleton(MongoDbFileService)
    ):
        self.temp_file : cyx.common.temp_file.TempFiles= temp_file
        self.file_storage_service =file_storage_service
        self.message_service = message_service
        self.db_connect: DbConnect = db_connect
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        self.file_dir = os.path.join(self.working_dir, "background_service_files", "file")
        self.logs_dir = os.path.join(self.working_dir, "background_service_files", "logs")
        if not os.path.isdir(self.file_dir):
            os.makedirs(self.file_dir, exist_ok=True)
        if not os.path.isdir(self.logs_dir):
            os.makedirs(self.logs_dir, exist_ok=True)
        self.logs = cy_kit.create_logs(self.logs_dir, FilesSync.__name__)
        self.logs.info(
            f"start service {FilesSync.__name__}"
        )

    def sync_file(self, item: MessageInfo,delete_if_exist=False):
        if self.temp_file.is_use:
            app_name = item.AppName
            file_ext = item.Data["FileExt"]
            upload_id = item.Data["_id"]
            full_file_path = self.temp_file.get_path(
                app_name=app_name,
                file_ext=file_ext,
                upload_id=upload_id
            )
            return full_file_path
        upload_id = item.Data.get("_id")
        upload_item = cy_docs.DocumentObject(item.Data)

        if not upload_item:
            return
        file_ext = upload_item.FileExt
        full_file_path = os.path.join(self.file_dir, f"{upload_id}.{file_ext}")
        if delete_if_exist:
            if os.path.isfile(full_file_path):
                os.remove(full_file_path)
        log_dir = os.path.join(self.file_dir,"logs",pathlib.Path(full_file_path).stem)
        log_sync_file = cy_kit.create_logs(
            log_dir,
            name="log-info"
        )
        if os.path.isfile(full_file_path):
            return full_file_path
        file_id = upload_item.MainFileId
        file_info = self.file_storage_service.get_file_info_by_id(
            app_name=item.AppName,
            id=file_id
        )
        if file_info is None:
            self.message_service.delete(item)
            return None
        sync_chunks = 0

        num_of_chunks = file_info.numOfChunks
        log_sync_file.info(
            f"start_sync at {datetime.datetime.utcnow()}"
        )
        timeout_in_seconds = 0
        fail_count =0
        delay_insecond_if_fail = 1
        max_fail_count, _ =divmod(30*60,delay_insecond_if_fail)
        while sync_chunks<num_of_chunks:
            try:
                reader = self.file_storage_service.get_reader_of_file(
                    app_name=item.AppName,
                    id=file_info.id,
                    from_chunk=sync_chunks
                )
                t = datetime.datetime.utcnow()
                chunk_data = reader.next()
                if chunk_data.__len__() ==0:
                    if isinstance(item.Data.get("RegisterOn"),datetime.datetime):
                        fx = (datetime.datetime.utcnow() - item.Data["RegisterOn"]).total_seconds()
                        if fx>4*60*60:
                            self.message_service.delete(item)
                            return None
                    time.sleep(delay_insecond_if_fail)
                    fail_count = fail_count + 1
                    print(f"sync file {item.AppName} {item.Data.get('FullFileNameLower')} {fail_count}")
                    if fail_count > max_fail_count:
                        log_sync_file.info(
                            f"sync chunks {sync_chunks} is error"
                        )

                        self.message_service.delete(item)
                        return None
                while chunk_data.__len__()>0:
                    try:
                        if not os.path.isfile(full_file_path):
                            with open(full_file_path, "wb") as f:
                                f.write(chunk_data)

                        else:
                            with open(full_file_path, "ab") as f:
                                f.write(chunk_data)

                        n = (datetime.datetime.utcnow()-t).total_seconds()*1000
                        log_sync_file.info(
                            f"sync chunks {sync_chunks} size {chunk_data.__len__()} in {n} ms"
                        )
                        del chunk_data
                        t = datetime.datetime.utcnow()
                        chunk_data = reader.next()
                        sync_chunks +=1
                    except TimeoutError as e:
                        time.sleep(delay_insecond_if_fail)
                        fail_count = fail_count + 1
                        if fail_count > max_fail_count:
                            log_sync_file.info(
                                f"sync chunks {sync_chunks} is error"
                            )
                            log_sync_file.exception(e)
                            self.message_service.delete(item)
                            return None

                    except Exception as e:
                        log_sync_file.info(
                            f"sync chunks {sync_chunks} is error"
                        )
                        log_sync_file.exception(e)
                        time.sleep(delay_insecond_if_fail)
                        chunk_data = reader.next()
            except TimeoutError as e:
                time.sleep(delay_insecond_if_fail)
                fail_count =fail_count+1
                if fail_count>max_fail_count:
                    log_sync_file.info(
                        f"sync chunks {sync_chunks} is error"
                    )
                    log_sync_file.exception(e)
                    self.message_service.delete(item)
                    return None

            except Exception as e:
                log_sync_file.info(
                    f"sync chunks {sync_chunks} is error"
                )
                log_sync_file.exception(e)
                self.message_service.delete(item)
                return None



            time.sleep(0.5)
            timeout_in_seconds+=0.5
            if timeout_in_seconds>3*60:
                log_sync_file.info(
                    f"sync chunks {sync_chunks} is timeout"
                )
                return None
        shutil.rmtree(log_dir)
        return full_file_path






    def sync_file_in_thread(self, item: MessageInfo, handler_service, output: dict, use_thread = True):
        output = dict()
        def run(_output: dict):
            _output = {}
            try:
                full_file_path = self.sync_file(item)
                if full_file_path is not None:
                    handler_service.resolve(item,full_file_path)
                    self.message_service.delete(item)
                    os.remove(full_file_path)
            except PIL.UnidentifiedImageError as e:
                output["error"] = e
                self.logs.exception(e)
                self.message_service.delete(item)
                if os.path.isfile(full_file_path):
                    os.remove(full_file_path)
            except fitz.fitz.FileDataError as e:
                output["error"] = e
                self.logs.exception(e)
                self.message_service.delete(item)
                if os.path.isfile(full_file_path):
                    os.remove(full_file_path)
            except Exception as e:
                output["error"] =e
                self.logs.exception(e)
                self.message_service.unlock(item)
                if os.path.isfile(full_file_path):
                    os.remove(full_file_path)


        if use_thread:
            th_run = threading.Thread(target=run, args=(output,)).start()
            return th_run
        else:
            run(output)
