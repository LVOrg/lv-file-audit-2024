import datetime
import io
import threading
import time
import typing
from googleapiclient.discovery import build, Resource
from functools import cache
import cy_docs
import cy_kit
from cyx.g_drive_services import GDriveService
from cyx.cache_service.memcache_service import MemcacheServices
import hashlib
from cyx.repository import Repository
from cyx.distribute_locking.distribute_lock_services import DistributeLockService

from cyx.common import config
import threading

my_lock = threading.Lock()

GOOGLE_DIRECTORIES_PRE_FIX=f"{__file__}.directories"

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

    def get_all_folders(self, app_name) -> typing.Tuple[dict | None, dict | None, dict | None]:
        """
        This method get all directories in Google Driver of tenant was embody by app_name
        return folder_tree,folder_hash, error
        :param app_name: tenant name
        :return: folder_tree,folder_hash, error
        """
        service, error = self.g_drive_service.get_service_by_app_name(app_name)
        if error:
            return None, None, error
        return self.__get_all_folders__(service)

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

    def get_all_folder_info(self, app_name: str,from_cache:bool=True) -> typing.Tuple[GoogleDriveInfo | None, dict | None]:
        """
        Get all directories in Google Drive of app
        :param app_name:
        :return: google_drive_info, error
        """
        key = f"{type(self).__module__}/{type(self).__name__}/get_all_folder_info/{app_name}"
        ret = None
        if from_cache:
            ret = self.memcache_service.get_object(key,GoogleDriveInfo)
            if isinstance(ret,GoogleDriveInfo):
                return ret, None


        service, error = self.g_drive_service.get_service_by_app_name(app_name,from_cache=from_cache)
        folder_tree, folder_list, error = self.__get_all_folders__(service)
        if error:
            return None, error
        else:
            ret = GoogleDriveInfo()
            ret.neast = folder_tree
            ret.hash = folder_list
            self.memcache_service.set_object(key,ret)
            return ret, None

    def check_before_upload(self, app_name, directory: str, file_name) -> typing.Tuple[
        bool | None, str | None, dict | None]:
        """
        Check folder in google if it is existing return True, google Folder Id, error is None
        :param app_name:
        :param directory:
        :param file_name:
        :return: IsExit: bool, Folder_id:str ,error: dict
        """

        service, error = self.g_drive_service.get_service_by_app_name(app_name)
        if error:
            return None, None, error
        t = datetime.datetime.utcnow()
        folder_tree, folder_list, error = self.__get_all_folders__(service)
        n = (datetime.datetime.utcnow() - t)
        print(n.total_seconds())
        root = folder_tree
        ret_id = None
        is_continue = True
        check_key = f"my drive"
        for x in directory.split('/'):
            check_key = check_key + "/" + x.lower()
            if folder_list.get(check_key):
                ret_id = folder_list[check_key]['id']
            else:
                ret_id = self.__create_folder__(service, x, ret_id)

        # folder_id = self.__do_create_folder__(service, app_name, directory)
        #
        data = service.files().list(q=f"name ='{file_name}' and parents='{ret_id}' and trashed=false").execute()[
            "files"]
        if len(data) > 0:
            return True, ret_id, None
        return False, ret_id, None

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

    def __get_all_folders__(self, service: Resource):

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
            results = service.files().list(q="mimeType = 'application/vnd.google-apps.folder'",
                                           fields="nextPageToken, files(id, name,parents,kind)",
                                           pageSize=100,  # Adjust page size as needed
                                           pageToken=page_token).execute()
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
