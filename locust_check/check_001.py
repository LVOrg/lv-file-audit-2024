url = ""
user="mannhi1601@gmail.com"
passwors="admin"
from locust import HttpUser, task
#https://apps.codx.vn/api/Auth/exec52
"""
{
    "isJson": true,
    "service": "Auth",
    "assemblyName": "ERM.Business.AD",
    "className": "UsersBusiness",
    "methodName": "LoginAsync",
    "msgBodyData": [
        "q3Wxl9xUTRv4v+8uP7dDaA==",
        "q3Wxl9xUTRv4v+8uP7dDaA==",
        "",
        "AIzaSyC1SKqppxpxwT7i3qEdUjJjn-J_SMoUBic",
        "",
        "{\"name\":\"Chrome\",\"os\":\"Windows 10\",\"ip\":\"\",\"imei\":null,\"id\":null,\"trust\":false,\"tenantID\":\"congtycsc\",\"times\":\"1\"}"
    ],
    "saas": 1,
    "tenant": "congtycsc"
}
"""
key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IjIzMDMxMTAwMDEiLCJuYW1laWQiOiIyMzAzMTEwMDAxIiwiZW1haWwiOiJtYW5uaGkxNjAxQGdtYWlsLmNvbSIsIkZ1bGxOYW1lIjoiUGhhbiBN4bqrbiBOaGkiLCJFbWFpbCI6Im1hbm5oaTE2MDFAZ21haWwuY29tIiwiTW9iaWxlIjoiMDk3NDY2Mzc1OCIsImp0aSI6IjA4OTEwYzM1LWQzNzQtNGY0MC04MDU3LTU2NDBiNWIzOWEyYyIsInNrIjoiMGFmMTljN2EtZjA1MS00ODAyLWI1N2MtOWY1OTFjNDIyMmE5IiwibmJmIjoxNjk4NjU2MTAwLCJleHAiOjE3MzAxOTIxMDAsImlhdCI6MTY5ODY1NjEwMCwiaXNzIjoiZXJtLmxhY3ZpZXQudm4iLCJhdWQiOiJlcm0ubGFjdmlldC52biJ9.nx64gcrCoVOVtCd0uJ73hz-Vu9JwKME10W_kFWOD-vY"
class CongTyCSCUser(HttpUser):

    @task
    def login(self):
        self.client.verify = False
        print("/api/Auth/exec52")

        self.client.post("/api/Auth/exec36", json= {
    "isJson": True,
    "service": "SYS",
    "assemblyName": "Core",
    "className": "CMBusiness",
    "methodName": "GetCacheAsync",
    "msgBodyData": [
        "TranslateLabel",
        "Notes"
    ],
    "saas": 1,
    "userID": "2303110001",
    "tenant": "congtycsc",
    "functionID": "WP"
},headers= {
            "Lvtk":key
        })

    @task
    def home(self):
        self.client.verify = False
        print("/congtycsc/wp/portal/WP")
        self.client.get("/congtycsc/wp/portal/WP")
#
# if __name__ == "__main__":
#     import locust
#
#     locust.main()