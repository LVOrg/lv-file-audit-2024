# from msal import ClientApplication
#
# cid = "d6f95a88-7785-4c0b-8c06-3bef17176ae9"
# csecret = "jin8Q~tM3SLKCt6o2UzoZrzPktbCfyz9z4311bdP"
# tid = "13d23acb-69f3-4651-98fe-76e95992f779"
# auth = f"https://login.microsoftonline.com/{tid}"
#
# app = ClientApplication(
#     client_id=cid,
#     client_credential=csecret,
#     authority=auth
# )
# __scope__ = [
#     'openid',
#     'offline_access',
#     # 'https://contoso.com/.default',
#     'https://graph.microsoft.com/user.read',
#     "https://graph.microsoft.com/.default",
#
# ]
# _S_=[
#     "User.Read"
# ]
# _S_ =[
#                         'Files.ReadWrite',
#                         'Files.ReadWrite.All']
# s = "https://graph.microsoft.com/.default"
# result = app.client.(scopes=[
#     "https://graph.microsoft.com/.default",
#     "https://graph.microsoft.com/.files.read"
# ])
# a = result.get("access_token")
# print(a)