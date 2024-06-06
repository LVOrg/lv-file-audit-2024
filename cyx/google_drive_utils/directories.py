import datetime
import gc
import io
import os.path
import pathlib
import shutil
import threading
import time
import typing

import requests
from googleapiclient.discovery import build, Resource
from functools import cache
import cy_docs
import cy_kit
import pymongo.errors
from cyx.g_drive_services import GDriveService
from cyx.cache_service.memcache_service import MemcacheServices
import hashlib
from cyx.repository import Repository
from cyx.distribute_locking.distribute_lock_services import DistributeLockService

from cyx.common import config
import threading

my_lock = threading.Lock()

GOOGLE_DIRECTORIES_PRE_FIX = f"{__file__}.directories"
import pymongo.errors

class GoogleDriveInfo:
    hash: dict
    """
    lis of all folder in hash
    """
    neast: dict
    """
    {id:str,children:[{id:str,..},...{}]
    """


class GoogleDirectoryService:
    def __init__(self,
                 g_drive_service=cy_kit.singleton(GDriveService),
                 memcache_service=cy_kit.singleton(MemcacheServices),
                 distribute_lock_service=cy_kit.singleton(DistributeLockService)
                 ):
        self.g_drive_service = g_drive_service
        self.memcache_service = memcache_service
        self.cache_key = f"{type(GoogleDirectoryService).__module__}"
        self.distribute_lock_service = distribute_lock_service
        self.local_cache = {}

    def check_folder_structure(self, app_name: str, directory_path: typing.List[str]) -> typing.Tuple[
        typing.Any, dict | None]:
        """
        Checks if folders exist recursively based on path segments.
        """
        tree, tree_hash, error = self.get_all_folders(app_name)
        if error:
            return None, error
        else:
            full_path = f"my drive/{directory_path}".lower()
            return tree_hash.get(full_path) is not None, None

    def __check_folder__(self, service: Resource, name: str, parent_id=None):
        if parent_id is None:
            q = f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder'  and trashed=false"
        else:
            q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{name}'  and parents = '{parent_id}' and trashed=false"
        results = service.files().list(q=q, fields="nextPageToken, files(id, name)", spaces="drive").execute()
        items = results.get('files', [])
        if len(items) == 0:
            return None, None
        else:
            return items[0]['id'], items[0]['name']

    def __check_folder_id__(self, service, folder_id):
        try:
            folder = service.files().get(fileId=folder_id).execute()
            # Check if 'mimeType' is 'application/vnd.google-apps.folder' to confirm it's a folder
            if folder['mimeType'] == 'application/vnd.google-apps.folder':
                return True
            else:
                return False
        except Exception as e:
            # Handle potential errors like invalid ID or non-existent folder
            if e.resp.status == 404:
                return False
            else:
                return False

    def __create_folder__(self, service: Resource, name: str, parent_id=None):
        id, _ = self.__check_folder__(service, name, parent_id)
        if id is None:
            folder_metadata = {
                'name': name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_id:
                folder_metadata['parents'] = [parent_id]
            try:
                folder = service.files().create(body=folder_metadata).execute()
                return folder["id"]
            except Exception as ex:
                raise ex

        return id

    def __create_folders_list__(self, service: Resource, folders, db_context, parent_id=None):
        if len(folders) == 1:
            item = db_context.context.find_one(Repository.google_folders.fields.Location == folders[0] + "/")
            if item is None:
                try:
                    db_context.context.insert_one(
                        Repository.google_folders.fields.Location << folders[0] + "/",
                        Repository.google_folders.fields.CloudId << "."
                    )
                except:
                    db_context.context.update(
                        Repository.google_folders.fields.Location == folders[0] + "/",
                        Repository.google_folders.fields.CloudId << "."
                    )

            else:
                qr = f"name = '{folders[0]}' and trashed=false"
                data_check = service.files().list(q=qr).execute()["files"]
                if any([x for x in data_check if x['id'] == item.CloudId]) and len(data_check) > 0:
                    return item.CloudId
                else:

                    folder_id = self.__create_folder__(service, folders[0], parent_id)
                    db_context.context.update(
                        Repository.google_folders.fields.Location == folders[0] + "/",
                        Repository.google_folders.fields.CloudId << folder_id
                    )
                    return folder_id
        else:
            parent_id = self.__create_folders_list__(service, folders[0:-1], db_context, parent_id)
            if folders[-1] == "26":
                print("OK")
            ret = self.__create_folders_list__(service, [folders[-1]], db_context, parent_id)
            return ret

    def __do_create_folder__(self, service, app_name, directory_path):
        directories = [x for x in directory_path.split('/') if len(x) > 0]
        parent_id = None
        current_paths = []
        check_paths = []
        for x in directories:

            check_paths += [x]
            # directory_id = self.get_from_cache(app_name, check_paths)
            # if directory_id is not None:
            #     parent_id = directory_id
            #     continue
            qr = f"name='{x}' and trashed=false and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                qr = f"name='{x}' and trashed=false and mimeType='application/vnd.google-apps.folder' and parents='{parent_id}'"
            resources = service.files().list(q=qr).execute()["files"]

            if len(resources) > 0:
                parent_id = resources[0]["id"]
                self.set_to_cache(app_name, check_paths, parent_id)
                current_paths += [x]
            else:
                folder_id = self.__create_folder__(service, x, parent_id)
                qr_check = f"name='{x}' and trashed=false and mimeType='application/vnd.google-apps.folder'"
                if parent_id:
                    qr_check = f"name='{x}' and trashed=false and mimeType='application/vnd.google-apps.folder' and parents='{parent_id}'"
                check_resources = service.files().list(q=qr_check).execute()["files"]
                if len(check_resources) == 0:
                    parent_location = "/".join(check_paths[:-1])

                    parent_id = self.__do_create_folder__(service=service, app_name=app_name,
                                                          directory_path=parent_location)
                    parent_id = self.__create_folder__(service, x, parent_id)
                else:
                    parent_id = folder_id
                self.set_to_cache(app_name, check_paths, parent_id)
                current_paths += [x]

        return parent_id

    def create_folders(self, app_name: str, directory_path: str) -> typing.Tuple[str | None, dict | None]:
        """

        :param app_name:
        :param directory_path:
        :return: folder_id, error
        """
        # folders = self.get_all_folders(app_name)

        # folder_id = self.get_from_cache(app_name,directory_path)
        # if folder_id:
        #     return folder_id

        # lock = RedisSpinLock(self.redis_client, lock_path)
        parent_path = "/".join(directory_path.split('/')[0:1])
        lock_path = f'{type(self).__module__}_{type(self).__name__}'
        try:
            if self.distribute_lock_service.acquire_lock(app_name):
                service, error = self.g_drive_service.get_service_by_app_name(app_name)
                if error:
                    return None, error
                parent_id = self.__do_create_folder__(
                    service=service,
                    app_name=app_name,
                    directory_path=directory_path
                )
                return parent_id, None
        except Exception as ex:
            raise ex
        finally:
            self.distribute_lock_service.release_lock(lock_path)

        # with self.distribute_lock_service.accquire(lock_path):
        #     service = self.g_drive_service.get_service_by_app_name(app_name)
        #     parent_id = self.__do_create_folder__(
        #         service=service,
        #         app_name=app_name,
        #         directory_path=directory_path
        #     )
        #     return parent_id
        # try:
        #     if self.distribute_lock_service.acquire_lock(lock_path):
        #         service = self.g_drive_service.get_service_by_app_name(app_name)
        #         parent_id = self.__do_create_folder__(
        #             service=service,
        #             app_name=app_name,
        #             directory_path=directory_path
        #         )
        #         return parent_id
        #     else:
        #         print("Failed to acquire lock, retrying...")
        # finally:
        #     self.distribute_lock_service.release_lock(lock_path)

    def get_cache_id_delete(self, app_name, directory_path):
        key = f"{self.cache_key}/{app_name}/{directory_path}"
        id = self.local_cache.get(key)
        if id is None:
            id = hashlib.sha256(key.encode()).hexdigest()
            self.local_cache[key] = id
        return id

    def __list_trashed_folders__(self, service, parent_id=None):
        """Retrieves a list of all trashed folders using pagination.

        Args:
            service: The authorized Google Drive service object.

        Returns:
            A list of dictionaries containing information about trashed folders.
        """

        trashed_folders = []
        page_token = None
        while True:
            # Retrieve a page of trashed items
            if parent_id is None:
                result = service.files().list(
                    q="trashed=true",
                    fields="nextPageToken, files(id, name, parents, kind)",
                    pageToken=page_token
                ).execute()
                trashed_items = result.get('files', [])

                # Filter for folders
                trashed_folders.extend([item for item in trashed_items])

                # Check for next page
                page_token = result.get('nextPageToken')
                if not page_token:
                    break
            else:
                try:
                    root_node = service.files().get(fileId=parent_id).execute()
                    if root_node.get("name") == "My Drive":
                        print("XX")
                    fxx = service.files().list(q=f"name='{root_node['name']}' and trashed=true").execute()
                    if fxx["files"].__contains__(root_node):
                        ret = [root_node]
                        return ret
                    elif root_node.get("parents") and len(root_node.get("parents")) > 0:
                        lst = self.__check_folder_id__(service, root_node.get("parents"))
                        return lst
                    else:
                        return []

                except Exception as ex:
                    print(ex)

        ext_list = []
        check = {}
        for x in trashed_folders:
            if x.get("parents") and len(x.get("parents")) > 0:
                p_id = x["parents"][0]
                if check.get(p_id) is None:
                    lst = self.__list_trashed_folders__(service, parent_id=p_id)
                    check[p_id] = p_id
                    ext_list += lst
        return trashed_folders + ext_list

    def get_all_folders(self, app_name,include_file=True) -> typing.Tuple[dict | None, dict | None, dict | None]:
        """
        This method get all directories in Google Driver of tenant was embody by app_name
        return folder_tree,folder_hash, error
        :param app_name: tenant name
        :return: folder_tree,folder_hash, error
        """
        service, error = self.g_drive_service.get_service_by_app_name(app_name)
        if error:
            return None, None, error
        return self.__get_all_folders__(service,include_file)

    def __resync_folders__(self, app_name):
        Repository.google_folders.app(app_name).context.delete({})
        total, _, lst = self.get_all_folders(app_name)
        for x in lst:
            Repository.google_folders.app(app_name).context.insert_one(
                Repository.google_folders.fields.Location << x["location"] + "/",
                Repository.google_folders.fields.CloudId << x["id"]
            )

    def get_from_cache(self, app_name, directories: typing.List[str]):
        cache_key = self.get_cache_id(app_name, "/".join(directories))
        return self.memcache_service.get_str(cache_key)

    def set_to_cache(self, app_name, directories: typing.List[str], resource_id):
        cache_key = self.get_cache_id(app_name, "/".join(directories))
        return self.memcache_service.set_str(cache_key, resource_id, expiration=60 * 24 * 30)

    def remove_cache(self, app_name, directory_path):
        cache_key = self.get_cache_id(app_name, directory_path)
        self.memcache_service.remove(cache_key)

    @cache
    def get_cache_id(self, app_name, path: str):
        ret = hashlib.sha256(f"{app_name}/{path}".encode()).hexdigest()
        return ret

    def get_all_folder_info(self, app_name: str, from_cache: bool = True) -> typing.Tuple[
        GoogleDriveInfo | None, dict | None]:
        """
        Get all directories in Google Drive of app
        :param app_name:
        :return: google_drive_info, error
        """
        key = f"{type(self).__module__}/{type(self).__name__}/get_all_folder_info/{app_name}"
        ret = None
        if from_cache:
            ret = self.memcache_service.get_object(key, GoogleDriveInfo)
            if isinstance(ret, GoogleDriveInfo):
                return ret, None

        service, error = self.g_drive_service.get_service_by_app_name(app_name, from_cache=from_cache)
        if error:
            return None, error
        folder_tree, folder_list, error = self.__get_all_folders__(service)
        if error:
            return None, error
        else:
            ret = GoogleDriveInfo()
            ret.neast = folder_tree
            ret.hash = folder_list
            self.memcache_service.set_object(key, ret)
            return ret, None

    def make_map_file(self, app_name, directory, filename, google_file_id: str):
        full_check_dir = os.path.join(config.file_storage_path, "__cloud_directories_sync__", app_name, directory,
                                      filename)
        id_file_of_full_check_dir = f"{hashlib.sha256(full_check_dir.encode()).hexdigest()}.txt"
        if os.path.isfile(id_file_of_full_check_dir):
            return
        else:
            os.makedirs(full_check_dir, exist_ok=True)
            if os.path.isfile(id_file_of_full_check_dir):
                return
            try:
                with open(id_file_of_full_check_dir, "wb") as fs:
                    fs.write(google_file_id.encode())
            except FileExistsError:
                return

    def make_map_folder(self, app_name, folder_path, folder_id):
        full_check_dir = os.path.join(config.file_storage_path, "__cloud_directories_sync__", app_name, folder_path)
        id_file_of_full_check_dir = f"{hashlib.sha256(full_check_dir.encode()).hexdigest()}.txt"
        full_mark_path = os.path.join(full_check_dir, id_file_of_full_check_dir)
        if os.path.isfile(full_mark_path):
            return
        else:
            os.makedirs(full_check_dir, exist_ok=True)
            if os.path.isfile(full_mark_path):
                return
            try:
                with open(full_mark_path, "wb") as fs:
                    fs.write(folder_id.encode())
            except FileExistsError:
                return

    def delete_file(self, app_name, folder_path, filename):
        full_check_dir = os.path.join(config.file_storage_path, "__cloud_directories_sync__", app_name, folder_path,
                                      filename)
        if os.path.isdir(full_check_dir):
            try:
                shutil.rmtree(full_check_dir)
            except:
                pass

    def get_remote_folder_id(self, service, app_name, directory, parent_id=None)->typing.Tuple[str|None,dict|None]:
        """

        :param service:
        :param app_name:
        :param directory:
        :param parent_id:
        :return: cloud_folder_id, error
        """
        if directory == "" or directory is None:
            return None, None
        folder_id = None
        data = Repository.cloud_path_track.app(app_name).context.find_one(
            Repository.cloud_path_track.fields.CloudPath == f"Google/my drive/{directory}"
        )
        if data is not None:
            data=data.to_json_convertable()
        if data is None:
            folder_tree,folder_hash, error =self.get_all_folders(app_name)

            if error:
                return None,error
            if folder_hash.get(f"my drive/{directory}"):
                folder_id = folder_hash.get(f"my drive/{directory}").get("id")
                try:
                    Repository.cloud_path_track.app(app_name).context.insert_one(
                        Repository.cloud_path_track.fields.CloudPath<<f"Google/my drive/{directory}",
                        Repository.cloud_path_track.fields.CloudPathId<<folder_hash.get(f"my drive/{directory}")
                    )
                except pymongo.errors.DuplicateKeyError as ex:
                    if (hasattr(ex, "details") and
                            isinstance(ex.details, dict) and
                            ex.details.get('keyPattern', {}).get('CloudPath')):

                        data = Repository.cloud_path_track.app(app_name).context.find_one(
                            Repository.cloud_path_track.fields.CloudPath == f"Google/my drive/{directory}"
                        )
                        if data:
                            data = data.to_json_convertable()
                            if folder_id != data["CloudPathId"]['id']:
                                service.files().delete(fileId=folder_id).execute()
                            folder_id = data["CloudPathId"]['id']
                            return folder_id,None
                return folder_id, None
            else:
                parent_of_folder_id, error = self.get_remote_folder_id(service,app_name,"/".join(directory.split('/')[0:-1]),parent_id)
                if error:
                    return None,error
                else:
                    folder_id = self.__create_folder__(service,directory.split('/')[-1],parent_of_folder_id)
                    try:
                        Repository.cloud_path_track.app(app_name).context.insert_one(
                            Repository.cloud_path_track.fields.CloudPath << f"Google/my drive/{directory}",
                            Repository.cloud_path_track.fields.CloudPathId << dict(id=folder_id)
                        )
                    except pymongo.errors.DuplicateKeyError as ex:
                        if (hasattr(ex, "details")
                                and isinstance(ex.details, dict)
                                and ex.details.get('keyPattern',{}).get('CloudPath')):
                            data = Repository.cloud_path_track.app(app_name).context.find_one(
                                Repository.cloud_path_track.fields.CloudPath == f"Google/my drive/{directory}"
                            )
                            if data:
                                data=data.to_json_convertable()
                                if folder_id != data["CloudPathId"]['id']:
                                    service.files().delete(fileId=folder_id).execute()
                                folder_id = data["CloudPathId"]['id']
                                del data
                                gc.collect()
                                return folder_id, None

                    return folder_id, None
        else:
            folder_id= data["CloudPathId"]['id']
            del data
            gc.collect()
            return folder_id, None


        # full_check_dir = os.path.join(config.file_storage_path, "__cloud_directories_sync__", app_name, directory)
        # id_file_of_full_check_dir = f"{hashlib.sha256(full_check_dir.encode()).hexdigest()}.txt"
        # path_to_get_folder_id = os.path.join(full_check_dir, id_file_of_full_check_dir)
        # ret_id = None
        # if os.path.isfile(path_to_get_folder_id):
        #     re_update = False
        #     with open(path_to_get_folder_id, "rb") as fs:
        #         ret_id = fs.read().decode()
        #         if len(ret_id) == 0 or ret_id is None:
        #             re_update = True
        #             ret_id = self.__create_folder__(service, directory.split('/')[-1], parent_id=parent_id)
        #     if re_update:
        #         with open(path_to_get_folder_id, "wb") as fs:
        #             fs.write(ret_id.encode())
        #     return ret_id, None
        #
        # else:
        #     folders = directory.split('/')
        #     folder_id, error = self.get_remote_folder_id(service, app_name, "/".join(folders[0:-1]))
        #     if error:
        #         return None, error
        #     new_folder_id = self.__create_folder__(service, folders[-1], parent_id=folder_id)
        #     self.make_map_folder(app_name=app_name, folder_path="/".join(folders), folder_id=new_folder_id)
        #     return new_folder_id, None

    def check_before_upload(self, app_name, directory: str, file_name) -> typing.Tuple[
        bool | None, str | None, dict | None]:
        """
        Check folder in google if it is existing return True, google Folder Id, error is None
        :param app_name:
        :param directory:
        :param file_name:
        :return: IsExit: bool, Folder_id:str ,error: dict
        """
        full_check_path = os.path.join(config.file_storage_path, "__cloud_directories_sync__", app_name, directory,
                                       file_name)
        try:
            os.makedirs(full_check_path)
        except FileExistsError:
            return True, None, None

        # token, error = self.g_drive_service.get_access_token_from_refresh_token(app_name, from_cache=True)
        service, error = self.g_drive_service.get_service_by_app_name(app_name, from_cache=False)
        if isinstance(error, dict):
            return None, None, error

        # client_id, client_secret, _, error = self.g_drive_service.get_id_and_secret(app_name, from_cache=True)
        folder_id, error = self.get_remote_folder_id(service=service, app_name=app_name, directory=directory)
        if isinstance(error, dict):
            return None, None, error
        return False, folder_id, None

        data = res.json()
        if data.get("error"):
            return None, None, data.get("error")
        elif isinstance(data.get("result"), dict):
            return data.get("result").get("is_exist"), data.get("result").get("folder_id"), None

    def register_upload_file(self, app_name, directory_id, file_name: str, file_size) -> typing.Tuple[
        str | None, str | None, dict | None]:
        """
        Register upload file and return file_id,upload_location,error
        :param app_name:
        :param directory_id:
        :param file_name:
        :param file_size:
        :return:
        """
        token, error = self.g_drive_service.get_access_token_from_refresh_token(app_name)
        if error:
            return None, None, error
        import requests
        import json
        headers = {"Authorization": f"Bearer " + token, "Content-Type": "application/json"}
        import mimetypes
        t, _ = mimetypes.guess_type(file_name)
        params = {
            "name": f"{file_name}",
            "mimeType": t,
            "parents": [directory_id]
        }
        r = requests.post(
            f"https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
            headers=headers,
            data=json.dumps(params)
        )
        fs = io.BytesIO()
        # fs.write(1)
        location = r.headers['Location']
        r = requests.put(
            location,
            headers=headers,
            data=fs
        )
        return r.json()["id"], location, None

    def __get_all_folders__(self, service: Resource,include_file=True):

        """
        This method get all directories in Google Driver of tenant was embody by app_name
        return folder_tree,folder_hash, error
        :param app_name: tenant name
        :return: folder_tree,folder_hash, error
        """

        page_token = None
        all_folders = []

        root = service.files().get(fileId="root").execute()

        folders_in_trash = self.__list_trashed_folders__(service)
        # trash_node,_ = self.extract_to_struct(folders_in_trash)
        # trash_list = self.extract_to_list(trash_node)
        while True:
            # Use files().list() with filter for folders
            if not include_file:
                results = service.files().list(q="mimeType = 'application/vnd.google-apps.folder'",
                                               fields="nextPageToken, files(id, name,parents,kind)",
                                               pageSize=100,  # Adjust page size as needed
                                               pageToken=page_token).execute()
            else:
                results = service.files().list(
                    fields="nextPageToken, files(id, name, parents, kind)",
                    pageSize=100,  # Adjust page size as needed
                    pageToken=page_token
                ).execute()
            folders = results.get('files', [])
            all_folders.extend(folders)
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        root_folder = None
        for x in folders_in_trash:
            if all_folders.__contains__(x):
                all_folders.remove(x)
        totals = len(all_folders)
        if totals == 0:
            return {}, {}, None
        cal_folders = []

        def get_tree(folders_list, root_folder, parent_path: str = None):
            ret = dict(
                id=root_folder["id"],
                name=root_folder["name"]
            )
            key = f"{parent_path.lower() + '/' if parent_path else ''}{root_folder['name'].lower()}"

            ret_list = {key: root_folder}
            children = [x for x in folders_list if x["parents"][0] == root_folder["id"]]
            ret["children"] = []
            while len(children) > 0:
                c = children.pop()
                ret["children"] += [c]
                folders_list.remove(c)
            for x in ret["children"]:
                n_children, n_list, sub_list = get_tree(folders_list, x, key)
                ret_list = {**ret_list, **sub_list}
                x["children"] = n_children

            return ret, folders_list, ret_list

        ret, _, tabular_list = get_tree(all_folders, root)
        return ret, tabular_list, None

    def get_thumbnail_url_by_file_id(self, app_name, file_id) -> typing.Tuple[str | None, dict | None]:
        service, error = self.g_drive_service.get_service_by_app_name(app_name)
        if error:
            return None, error
        ret, error = self.get_thumbnail_url_by_file_id_with_service(service, file_id)

    def get_thumbnail_url_by_file_id_with_service(self, service: Resource, file_id) -> typing.Tuple[
        str | None, dict | None]:
        file_metadata = service.files().get(fileId=file_id, fields="thumbnailLink").execute()
        if file_metadata.get('thumbnailLink'):
            # Construct potential thumbnail URL pattern (replace with actual domain if different)
            return file_metadata.get('thumbnailLink'), None
        else:
            return None, None

#export HUGGINGFACE_HUB_CACHE=/mnt/files/__dataset__/cache
#export HUGGINGFACE_ASSETS_CACHE=/mnt/files/__dataset__/asset
#HUGGINGFACE_HUB_CACHE = os.getenv("HUGGINGFACE_HUB_CACHE", default_cache_path)
#HUGGINGFACE_ASSETS_CACHE = os.getenv("HUGGINGFACE_ASSETS_CACHE", default_assets_cache_path)
