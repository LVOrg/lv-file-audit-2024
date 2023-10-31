lacviet_demo={
    "isJson": True,
    "service": "WP",
    "assemblyName": "ERM.Business.WP",
    "className": "CommentsBusiness",
    "methodName": "GetListPostAsync",
    "msgBodyData": [
        {
            "pageLoading": True,
            "page": 1,
            "pageSize": 10,
            "formName": "Comments",
            "gridViewName": "grvComments",
            "entityName": "WP_Comments",
            "predicate": "Category = @0 || Category = @1 || Category = @2",
            "dataValue": "1;3;4",
            "funcID": "WP",
            "entityPermission": "WP_Comments",
            "treeField": "",
            "treeIDValue": "",
            "sort": [
                {
                    "field": "CreatedOn",
                    "dir": "desc"
                }
            ],
            "predicates": None,
            "dataValues": None,
            "entryMode": "",
            "selector": ""
        }
    ],
    "saas": 1,
    "userID": "ADMIN",
    "tenant": "lacvietdemo",
    "functionID": "WP"
}
congty_csc={
    "isJson": True,
    "service": "WP",
    "assemblyName": "ERM.Business.WP",
    "className": "CommentsBusiness",
    "methodName": "GetListPostAsync",
    "msgBodyData": [
        {
            "pageLoading": True,
            "page": 1,
            "pageSize": 10,
            "formName": "Comments",
            "gridViewName": "grvComments",
            "entityName": "WP_Comments",
            "predicate": "Category = @0 || Category = @1 || Category = @2",
            "dataValue": "1;3;4",
            "funcID": "WP",
            "entityPermission": "WP_Comments",
            "treeField": "",
            "treeIDValue": "",
            "sort": [
                {
                    "field": "CreatedOn",
                    "dir": "desc"
                }
            ],
            "predicates": None,
            "dataValues": None,
            "entryMode": "",
            "selector": ""
        }
    ],
    "saas": 1,
    "userID": "2303110001",
    "tenant": "congtycsc",
    "functionID": "WP"
}
congty_csc_2={
    "isJson": True,
    "service": "DM",
    "assemblyName": "ERM.Business.DM",
    "className": "FileBussiness",
    "methodName": "GetFilesByIbjectIDAsync",
    "msgBodyData": [
        "6119958b-b335-4958-8e29-6ec037217713"
    ],
    "saas": 1,
    "userID": "2303110001",
    "tenant": "congtycsc",
    "functionID": "WP"
}
data_get_folder= {
    "isJson": True,
    "service": "DM",
    "assemblyName": "DM",
    "className": "FolderBussiness",
    "methodName": "GetFoldersAsync",
    "msgBodyData": [
        {
            "pageLoading": True,
            "page": 1,
            "pageSize": 2000,
            "entityName": "DM_FolderInfo",
            "funcID": "DMT00",
            "srtColumns": "CreatedOn",
            "srtDirections": "desc"
        },
        "64b499f2690d9860752a3aad"
    ],
    "saas": 1,
    "userID": "ADMIN",
    "tenant": "lacvietdemo",
    "functionID": "DMT00"
}
import copy

def get_data(input_data:dict,tenant:str,user_id:str):
    ret=  copy.deepcopy(input_data)
    ret["userID"]=user_id
    ret["tenant"]=tenant
    return ret
