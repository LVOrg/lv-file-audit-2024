# import requests
# import json
# import urllib
# URL = 'https://graph.microsoft.com/v1.0/'
#
# def ms_method(method:str,rel_url:str):
#     def wrapper(**kwargs):
#         token= kwargs.get("token")
#         if not token:
#             raise Exception("Call https://graph.microsoft.com/v1.0 require token")
#         body_keys = [for k in list(kwargs.keys()) if k!="token"]
#         data=None
#         if len(body_keys)>0:
#             if data is None:
#                 data ={}
#             for k in body_keys:
#                 data[k] = kwargs[k]
#
#         def exex_func(*a,**k):
#             _method_ = method.lower()
#             fn_method = getattr(requests,_method_)
#             HEADERS = {'Authorization': 'Bearer ' + token}
#             if data:
#                 response = fn_method(URL + rel_url, headers=HEADERS,data=data)
#             else:
#                 response = fn_method(URL + rel_url, headers=HEADERS)
#             if (response.status_code >= 200 and response.status_code<300):
#                 response = json.loads(response.text)
#                 return response
#             elif (response.status_code == 401):
#                 response = json.loads(response.text)
#                 raise Exception('API Error! : ', response['error']['code'], \
#                       '\nSee response for more details.')
#             else:
#                 raise Exception(f'Unknown error! See response for more details. {response.text}')
#
#     return wrapper