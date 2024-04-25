import time
import typing
from googleapiclient.discovery import build, Resource
import cy_kit
from cyx.g_drive_services import GDriveService
from cyx.cache_service.memcache_service import MemcacheServices
import hashlib
from cyx.repository import Repository


class GoogleDirectoryService:
    def __init__(self,
                 g_drive_service=cy_kit.singleton(GDriveService),
                 memcache_service=cy_kit.singleton(MemcacheServices)
                 ):
        self.g_drive_service = g_drive_service
        self.memcache_service = memcache_service
        self.cache_key = f"{type(GoogleDirectoryService).__module__}"
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
                        # Reached the end of the path, folder structure exists
                        print(f"Folder structure exists: /{'/'.join(directory_path)}")
                else:
                    # Folder name mismatch, structure doesn't exist at this point
                    print(f"Folder structure doesn't exist at: /{'/'.join(directory_path[:1])}")
                    return

    # def get_folders_id(self,app_name:str,directory_path:str):
    #     cache_id= self.get_cache_id(app_name,directory_path)
    #     id= self.memcache_service.get_str(cache_id)
    #     if id is None:
    #         data = Repository.google_folders.app(app_name).context.find_one(
    #             Repository.google_folders.fields.Location==directory_path
    #         )
    #         if data:
    #             id = data.CloudId
    #             self.memcache_service.set_str(cache_id,id)
    #             return id
    #         else:

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
                print(f"Folder ID '{folder_id}' exists.")
                return True
            else:
                print(f"ID '{folder_id}' exists but isn't a folder.")
                return False
        except Exception as e:
            # Handle potential errors like invalid ID or non-existent folder
            if e.resp.status == 404:
                print(f"Folder ID '{folder_id}' not found.")
                return False
            else:
                print(f"An error occurred: {e}")
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

    def create_folders(self, app_name: str, directory_path: str)->str:
        folders = self.get_all_folders(app_name)
        import pymongo.errors
        import googleapiclient.errors
        folders = directory_path.split('/')
        service = self.g_drive_service.get_service_by_app_name(app_name)
        parent_id = None
        path_check=""
        parent_path_check=""
        for x in folders:
            path_check+=x+"/"
            item = Repository.google_folders.app(app_name=app_name).context.find_one(
                Repository.google_folders.fields.Location==path_check
            )
            if item is None:

                try:
                    if parent_id:
                        if not self.__check_folder_id__(service=service,folder_id=parent_id):
                            parent_id = self.create_folders(app_name,directory_path=parent_path_check.rstrip('/'))
                            print(parent_id)
                    Repository.google_folders.app(app_name=app_name).context.insert_one(
                        Repository.google_folders.fields.Location << path_check,
                        Repository.google_folders.fields.CloudId << "."

                    )
                    folder_id = self.__create_folder__(service=service, name=x, parent_id=parent_id)
                    Repository.google_folders.app(app_name=app_name).context.update(
                        Repository.google_folders.fields.Location == path_check,
                        Repository.google_folders.fields.CloudId << folder_id

                    )
                    parent_path_check = path_check
                except pymongo.errors.DuplicateKeyError as e:
                    item = Repository.google_folders.app(app_name=app_name).context.find_one(
                        Repository.google_folders.fields.Location == path_check
                    )
                    folder_id = item.CloudId
                except googleapiclient.errors.HttpError as ex:
                    if ex.status_code==404:
                        _parent_id=ex.error_details[0].get('message').split(':')[1].lstrip(' ').rstrip('.')
                        if parent_id==_parent_id:
                            Repository.google_folders.app(app_name).context.delete(Repository.google_folders.fields.Location==parent_path_check)
                            folder_id= self.create_folders(app_name,path_check.rstrip('/'))
                            return folder_id


                    raise ex
                except Exception as ex:
                    raise ex
            elif item.CloudId==".":
                time.sleep(0.3)
                item = Repository.google_folders.app(app_name=app_name).context.find_one(
                    Repository.google_folders.fields.Location == path_check
                )
                while item.CloudId==".":
                    time.sleep(0.3)
                    item = Repository.google_folders.app(app_name=app_name).context.find_one(
                        Repository.google_folders.fields.Location == path_check
                    )
                folder_id = item.CloudId
                # if not self.__check_folder_id__(service=service, folder_id=folder_id):
                #     Repository.google_folders.app(app_name).context.delete(
                #         Repository.google_folders.fields.Location == path_check)
                #     folder_id = self.create_folders(app_name, path_check.rstrip('/'))

                parent_path_check = path_check
            else:
                folder_id = item.CloudId
                # if not self.__check_folder_id__(service=service, folder_id=folder_id):
                #     Repository.google_folders.app(app_name).context.delete(
                #         Repository.google_folders.fields.Location == path_check)
                #     folder_id =self.create_folders(app_name,path_check.rstrip('/'))

                parent_path_check = path_check

            parent_id = folder_id
        return parent_id
    def get_cache_id(self, app_name, directory_path):
        key = f"{self.cache_key}/{app_name}/{directory_path}"
        id = self.local_cache.get(key)
        if key is None:
            id = hashlib.sha256(key.encode()).hexdigest()
            self.local_cache[key] = id
        return id

    def get_all_folders(self, app_name):
        page_token = None
        all_folders = []
        service = self.g_drive_service.get_service_by_app_name(app_name)
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

        print(f"Found a total of {len(all_folders)} folders.")
        root_folder= None

        for folder in all_folders:
            parent_id= folder.get("parents")[0]
            if any([x for x in all_folders if x["id"]==parent_id]):
                continue
            else:
                root_folder = service.files().get(fileId=parent_id).execute()
                break
        all_folders+=[root_folder]
        ret, folder_list = self.extract_to_struct(all_folders)
        folder_list = self.extract_to_list(ret)
        return folder_list

    def extract_to_struct(self, all_folders,parent_node=None):
        if parent_node is None:
            node = [x for x in all_folders if x.get("parents") is None][0]
            all_folders.remove(node)
            children,all_folders = self.extract_to_struct(all_folders,node)
            node["children"]=children
            return node,all_folders
        else:
            nodes = [x for x in all_folders if x.get("parents")[0]==parent_node["id"]]
            for x in nodes:
                children, all_folders = self.extract_to_struct(all_folders, x)
                x["children"] = children

                all_folders.remove(x)

            return nodes,all_folders

    def extract_to_list(self, node, parent_location=None, get_root= True):
        ret= []
        root = None
        if get_root:
            root = node.get("children")[0]

        else:
            root = node
        location = root.get("name")
        if parent_location is not None:
            location=f"{parent_location}/{location}"
        ret += [dict(
            location=location,
            id=root.get("id")
        )]
        for x in root.get("children"):
            if parent_location is None:
                parent_location = root.get("name")
            ret_list = self.extract_to_list(x,f"{parent_location}",get_root=False)
            ret+=ret_list
        return ret












