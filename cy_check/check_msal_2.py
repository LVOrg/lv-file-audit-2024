# import msal
# scopes = ["https://graph.microsoft.com/files.ReadWrite.All"]
# tenant_id = "13a53f39-4b4d-4268-8c5e-ae6260178923"
# client_id = "72ea309b-170a-41a1-b399-af323d58ca35"
# client_secret = "OIO8Q~fTKOaot_lHDpQPHrsC51VCGjjGqDbnualT"
# def check_args(*args,**kwargs):
#     print(args)
#
# auth_provider = msal.PublicClientApplication(
#     client_id,
#     authority=f"https://login.microsoftonline.com/{tenant_id}"
# )
# auth_provider.
# result =auth_provider.acquire_token_by_auth_code_flow(
#             scopes=scopes,
#             redirect_uri="https://172.16.13.72:8012/lvfile/api/lv-docs/azure/after_login",
#             auth_code_flow=dict(
#                 claims_challenge=None,
#                 state=123,
#
#                 scope=scopes+['openid', 'offline_access', 'profile']
#             ),
#             auth_response=dict(
#                 client_info={},
#                 state=123
#             )
#         )
#
# access_token = result["access_token"]