import threading
import time
import typing
from googleapiclient.discovery import build, Resource

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

    def check_folder_structure(self, app_name: str, directory_path: typing.List[str], parent_id=None):
        """
        Checks if folders exist recursively based on path segments.
        """
        # Get child files/folders within the current folder
        q = f"mimeType = 'application/vnd.google-apps.folder' and name = '{directory_path[0]}' in parents"
        q = f"name = '{directory_path[0]}' and mimeType = 'application/vnd.google-apps.folder'"
        #  results = service.files().list(q=f"'{parent_id}' in parents", fields="nextPageToken, files(id, name)").execute()

        service = self.g_drive_service.get_service_by_app_name(app_name)
        results = service.files().list(q=q, fields="nextPageToken, files(id, name)", spaces="drive").execute()
        items = results.get('files', [])

        # Check each child item
        for item in items:
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                # Check if folder name matches current path segment
                if item['name'] == directory_path[0]:
                    # If it matches, continue checking subfolders recursively
                    remaining_path = directory_path[1:]
                    if remaining_path:
                        self.check_folder_structure(service, item['id'], remaining_path)

                else:
                    return

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
        directories = directory_path.split('/')
        parent_id = None
        current_paths = []
        check_paths = []
        for x in directories:

            check_paths += [x]
            qr = f"name='{x}' and trashed=false and mimeType='application/vnd.google-apps.folder'"
            if parent_id:
                qr = f"name='{x}' and trashed=false and mimeType='application/vnd.google-apps.folder' and parents='{parent_id}'"
            resources = service.files().list(q=qr).execute()["files"]

            if len(resources) > 0:
                parent_id = resources[0]["id"]
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

                current_paths += [x]

        return parent_id

    def create_folders(self, app_name: str, directory_path: str) -> str:
        # folders = self.get_all_folders(app_name)


        # folder_id = self.get_from_cache(app_name,directory_path)
        # if folder_id:
        #     return folder_id

        # lock = RedisSpinLock(self.redis_client, lock_path)
        parent_path = "/".join(directory_path.split('/')[0:1])
        lock_path = f'{type(self).__module__}_{type(self).__name__}'
        with self.distribute_lock_service.accquire(lock_path):
            service = self.g_drive_service.get_service_by_app_name(app_name)
            parent_id = self.__do_create_folder__(
                service=service,
                app_name=app_name,
                directory_path=directory_path
            )
            return parent_id
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

    def get_all_folders(self, app_name) -> typing.Tuple[int, dict, dict]:
        """
        This method get all directories in Google Driver of tenant was embody by app_name
        return total folders, nested folder structure and tabular list
        :param app_name: tenant name
        :return:
        """
        page_token = None
        all_folders = []
        service = self.g_drive_service.get_service_by_app_name(app_name)
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
            return 0, {}, []
        cal_folders = []
        for folder in all_folders:
            if folder.get("parents"):
                parent_id = folder.get("parents")[0]
                parent_list = [x for x in all_folders if x["id"] == parent_id]
                if len(parent_list) > 0:
                    cal_folders += [folder] + parent_list
                else:
                    print(folder)
            else:
                cal_folders += [folder]
        all_folders = cal_folders + [service.files().get(fileId="root").execute()]
        ret, folder_list = self.extract_to_struct(all_folders)
        folder_list = self.extract_to_list(ret)
        return totals, ret, folder_list

    def extract_to_struct(self, all_folders, parent_node=None):
        if parent_node is None:
            nodes = [x for x in all_folders if x.get("parents") is None]
            if len(nodes) > 0:
                node = nodes[0]
                all_folders.remove(node)
                children, all_folders = self.extract_to_struct(all_folders, node)
                node["children"] = children
                return node, all_folders
            else:
                return None, all_folders
        else:
            nodes = [x for x in all_folders if x.get("parents") and x.get("parents")[0] == parent_node["id"]]
            for x in nodes:
                children, all_folders = self.extract_to_struct(all_folders, x)
                x["children"] = children

                all_folders.remove(x)

            return nodes, all_folders

    def extract_to_list(self, node, parent_location=None, get_root=True):
        ret = []
        root = None
        if get_root:
            if node is None:
                return None
            if node.get("children") and len(node.get("children")) > 0:
                root = node.get("children")[0]

        else:
            root = node
        location = root.get("name")
        if parent_location is not None:
            location = f"{parent_location}/{location}"
        ret += [dict(
            location=location,
            id=root.get("id")
        )]
        for x in root.get("children"):
            if parent_location is None:
                parent_location = root.get("name")
            ret_list = self.extract_to_list(x, f"{parent_location}", get_root=False)
            ret += ret_list
        return ret

    def __resync_folders__(self, app_name):
        Repository.google_folders.app(app_name).context.delete({})
        total, _, lst = self.get_all_folders(app_name)
        for x in lst:
            Repository.google_folders.app(app_name).context.insert_one(
                Repository.google_folders.fields.Location << x["location"] + "/",
                Repository.google_folders.fields.CloudId << x["id"]
            )

    def get_from_cache(self, app_name, directory_path):
        cache_key = self.get_cache_id(app_name, directory_path)
        return self.memcache_service.get_str(cache_key)

    def set_to_cache(self, app_name, directory_path, resource_id):
        cache_key = self.get_cache_id(app_name, directory_path)
        return self.memcache_service.set_str(cache_key, resource_id, expiration=60 * 24 * 30)

    def remove_cache(self, app_name, directory_path):
        cache_key = self.get_cache_id(app_name, directory_path)
        self.memcache_service.remove(cache_key)
