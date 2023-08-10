import pathlib
import sys

import datetime
import mimetypes
import os
import threading
import time
import typing

import gridfs
import pymongo.database

import cy_docs
import cy_kit
from cyx.common.base import Base
from gridfs import GridIn
import bson
from  pymongo.read_preferences import ReadPreference
from pymongo.read_concern import ReadConcern
from cyx.common.file_storage import FileStorageService, FileStorageObject

import pymongo.errors
# @cy_kit.must_imlement(FileStorageObject)
class MongoDbFileReader:
    def __init__(self,fs_cursor):
        self.fs_cursor=fs_cursor
    def next(self)->bytes:
        try:
            ret = self.fs_cursor.next()["data"]
            return ret
        except StopIteration as e:
            return b""

class MongoDbFileStorage:
    def __init__(self, fs: GridIn,db:pymongo.database.Database,buffering_len:int=9,logical_chunk_size:int=None):
        if logical_chunk_size is None:
            logical_chunk_size =fs.chunk_size
        self.fs = fs
        self.db = db
        self.is_dirty=False
        self.position = 0
        self.chunk_index =0
        self.chunk_size = fs.chunk_size
        self.remain = 0
        self.logical_chunk_size = logical_chunk_size


        self.num_of_chunks, m = divmod(fs.length,fs.chunk_size)

        if m>0:
            self.num_of_chunks+=1
        self.cursor_len = buffering_len
        self.collection = db.get_collection("fs.chunks")

    def get_cursor(self,from_index ,num_of_element,cursor=None):

        return cy_docs.file_get_iter_contents(
            client = self.db.client,
            db_name = self.db.name,
            files_id = self.fs._id,
            from_chunk_index=from_index,
            num_of_chunks = num_of_element
        )




    def seek(self, position):
        # self.position = position
        # a,b = divmod(self.position,self.chunk_size)
        # self.chunk_index = a
        # self.remain =b

        return self.fs.seek(position)

    def get_size(self):
        return self.fs.length

    def tell(self):
        # return self.position
        return self.fs.tell()

    def read(self, size) -> bytes:
        return self.fs.read(size)




    def get_id(self) -> str:
        return str(self.fs._id)

    def push(self, content: bytes, chunk_index):
        cy_docs.file_add_chunks(
            client= self.db.client,
            db_name=self.db.name,
            file_id=self.fs._id,
            data= content
        )



    def close(self):
        """
        some how to implement thy source here ...
        """
        self.fs.close()
        # pass



class MongoDbFileService(Base):
    def create(self, app_name: str, rel_file_path: str,content_type:str, chunk_size: int, size: int) -> MongoDbFileStorage:
        mongo_db_chunk_size = chunk_size
        logical_chunk_size=1
        if chunk_size>=1024*1024*2:
            a,b = divmod(chunk_size,1024*64)
            if b==0:
                mongo_db_chunk_size = 1024*32
                logical_chunk_size = a

        fs = cy_docs.create_file(
            client=self.client,
            db_name=self.db_name(app_name),
            file_name=rel_file_path,
            chunk_size=mongo_db_chunk_size,
            file_size=size,
            content_type = content_type

        )
        return MongoDbFileStorage(fs,self.client.get_database(self.db_name(app_name)),logical_chunk_size = logical_chunk_size)

    def store_file(self, app_name:str, source_file:str, rel_file_store_path:str)-> MongoDbFileStorage:
        ret = self.get_file_by_name(
            app_name= app_name,
            rel_file_path= rel_file_store_path
        )
        if ret:
            return ret
        content_type, _  = mimetypes.guess_type(source_file)
        chunk_size = 1024*1024*2
        ret = self.create(
            app_name =app_name,
            rel_file_path= rel_file_store_path,
            chunk_size = chunk_size,
            content_type= content_type,
            size= os.stat(source_file).st_size
        )
        chunk_index = 0
        with open(source_file,"rb") as f:
            data = f.read(chunk_size)
            while data.__len__()>0:
                ret.push(data,chunk_index)
                chunk_index += 1
                del data
                data = f.read(chunk_size)
        return ret

    def get_file_by_name(self, app_name, rel_file_path: str) -> MongoDbFileStorage:
        rel_file_path=rel_file_path.lower()
        fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name))).find_one(
            {
                "rel_file_path": rel_file_path
            }
        )
        if fs is None:
            fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name))).find_one(
                {
                    "filename": rel_file_path
                }
            )
            if fs is not None:
                self.client.get_database(self.db_name(app_name)).get_collection("fs.files").update_one(
                    {
                        "_id": fs._id
                    },
                    {
                        "$set": {
                            "rel_file_path": rel_file_path
                        }
                    }
                )
            else:
                return None

        ret = MongoDbFileStorage(fs,self.client.get_database(self.db_name(app_name)))
        return ret

    def get_file_by_id(self, app_name: str, id: str) -> MongoDbFileStorage:
        fs = cy_docs.file_get(self.client, self.db_name(app_name), bson.ObjectId(id))



        ret = MongoDbFileStorage(fs,self.client.get_database(self.db_name(app_name)))
        return ret

    def delete_files_by_id(self, app_name: str, ids: typing.List[str], run_in_thread: bool):
        bson_id = [id for id in ids if bson.is_valid(id.encode())]
        def run():
            fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name)))
            for x in bson_id:
                fs.delete(bson.ObjectId(x))

        if run_in_thread:
            threading.Thread(target=run, args=()).start()
        else:
            run()

    def delete_files(self, app_name, files: typing.List[str], run_in_thread: bool):
        def run():
            fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name)))
            for x in files:
                f = fs.find_one({"rel_file_path": x})
                if f:
                    fs.delete(f._id)

        if run_in_thread:
            threading.Thread(target=run, args=()).start()
        else:
            run()
    def copy_by_id(self, app_name: str, file_id_to_copy: str,rel_file_path_to:str, run_in_thread: bool) ->MongoDbFileStorage:
        """
            Copy file from id file and return new copy if successful
            :param app_name:
            :param file_id_to_copy:
            :param run_in_thread:
            :return:
                """
        source = self.get_file_by_id(
            app_name=app_name,
            id= file_id_to_copy
        )
        if not source:
            return None
        dest = self.create(
            app_name=app_name,
            rel_file_path=rel_file_path_to,
            chunk_size=source.fs.chunk_size,
            size=source.fs.length,
            content_type=source.fs.content_type
        )

        @cy_kit.thread_makeup()
        def process(s: MongoDbFileStorage, d: MongoDbFileStorage):
            data =s.fs.read(s.fs.chunk_size)
            index=0
            while data.__len__()>0:
                d.push(content=data,chunk_index=index)
                data = s.fs.read(s.fs.chunk_size)
                index+=1


        if run_in_thread:
            process(source, dest).start()
        else:
            process(source,dest).join()
        return dest
    def copy(self, app_name: str, rel_file_path_from: str, rel_file_path_to, run_in_thread: bool)->MongoDbFileStorage:
        """
            Copy file
            :param rel_file_path_to:
            :param rel_file_path_from:
            :param app_name:
            :param run_in_thread:True copy process will run in thread
            :return:
                """

        source = self.get_file_by_name(
            app_name=app_name,
            rel_file_path= rel_file_path_from
        )
        if not source:
            return None
        dest  = self.create(
            app_name=app_name,
            rel_file_path = rel_file_path_to,
            chunk_size = source.fs.chunk_size,
            size = source.fs.length,
            content_type=source.fs.content_type
        )
        @cy_kit.cy_kit_x.thread_makeup()
        def process(s:MongoDbFileStorage,d:MongoDbFileStorage):
            print(s,d)
        process(source,dest).start()
        return dest

    def get_file_info_by_id(self, app_name, id):
        return cy_docs.get_file_info_by_id(
            client = self.client,
            db_name = self.db_name(app_name),
            files_id=id
        )

    def get_reader_of_file(self, app_name:str,from_chunk, id)->MongoDbFileReader:
        if isinstance(id,str):
            id = bson.ObjectId(id)
        cursor = self.client.get_database(
            self.db_name(app_name)
        ).get_collection("fs.chunks").find(
            {
                "files_id":id,
                "n":{
                    "$gte":from_chunk
                }
            }
        )
        return MongoDbFileReader(cursor)



