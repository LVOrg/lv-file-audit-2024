import cy_kit
from cyx.cloud.azure.azure_utils_services import AzureUtilsServices
s = cy_kit.singleton(AzureUtilsServices)
s.get_driver_id(app_name="lv-docs")
tree,hast_tree,error =s.get_all_folders(app_name="lv-docs")
print(hast_tree)