from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build, Resource
import typing
import datetime
def get_service(token, client_id, client_secret, g_service_name: str = "v3/drive") -> Resource:
    credentials = OAuth2Credentials(
        token=token,
        refresh_token=token,  # Assuming you have a refresh token (optional)
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    if not isinstance(g_service_name, str):
        return None
    version, service_name = tuple(g_service_name.split('/'))
    service = build(service_name, version, credentials=credentials)
    return service


def get_all_folders(service: Resource):
    """
    This method get all directories in Google Driver of tenant was embody by app_name
    return folder_tree,folder_hash, error
    :param app_name: tenant name
    :return: folder_tree,folder_hash, error
    """

    page_token = None
    all_folders = []

    root = service.files().get(fileId="root").execute()

    folders_in_trash = list_trashed_folders(service)
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


def list_trashed_folders(service, parent_id=None):
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
                    lst = check_folder_id(service, root_node.get("parents"))
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
                lst = list_trashed_folders(service, parent_id=p_id)
                check[p_id] = p_id
                ext_list += lst
    return trashed_folders + ext_list


def check_folder_id(service, folder_id):
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
def check_folder(service: Resource, name: str, parent_id=None):
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
def create_folder(service: Resource, name: str, parent_id=None):
    id, _ = check_folder(service, name, parent_id)
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

def do_validate(service,directory: str, file_name) -> typing.Tuple[
    bool | None, str | None, dict | None]:
    """
    Check folder in google if it is existing return True, google Folder Id, error is None
    :param app_name:
    :param directory:
    :param file_name:
    :return: IsExit: bool, Folder_id:str ,error: dict
    """
    t = datetime.datetime.utcnow()
    folder_tree, folder_list, error = get_all_folders(service)
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
            ret_id = create_folder(service, x, ret_id)

    # folder_id = self.__do_create_folder__(service, app_name, directory)
    #
    data = service.files().list(q=f"name ='{file_name}' and parents='{ret_id}' and trashed=false").execute()[
        "files"]
    if len(data) > 0:
        return True, ret_id, None
    return False, ret_id, None