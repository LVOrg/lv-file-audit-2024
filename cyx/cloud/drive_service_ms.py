import typing

import cy_kit
from cyx.cloud.azure.azure_utils import call_ms_func
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
class DriveServiceMS:
    def __init__(self ,
                 azure_utils_services:AzureUtilsServices = cy_kit.singleton(AzureUtilsServices)
                 ):
        self.azure_utils_services=azure_utils_services
        """
        All azure utils here
        """
    def get_available_space(self, app_name):
        raise NotImplemented()

    def remove_upload(self, app_name, file_id)-> typing.Tuple[bool,dict|None]:
        """
        Delete resource form MS Azure (particularly, Resource is File_Id on onedrive)
        :param app_name: 
        :param file_id: 
        :return: 
        """"""
        # Replace with your access token
          url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}"
          headers = {"Authorization": f"Bearer {access_token}"}
        
          response = requests.delete(url, headers=headers)
        
          if response.status_code == 204:
            print("File deleted and sent to recycle bin.")
          else:
            print(f"Error deleting file: {response.text}")
        """
        acquire_token_info, error = self.azure_utils_services.acquire_token(app_name)
        if error:
            return  False,error

        res,error = call_ms_func(
            method="delete",
            api_url=f"me/drive/items/{file_id}",
            token=acquire_token_info.access_token,
            body=None
        )
        if error:
            return False,error
        return True,None