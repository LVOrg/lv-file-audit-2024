import pathlib
import sys

wk= pathlib.Path(__file__).parent.parent.__str__()
print(wk)
sys.path.append(wk)
url = ""
user="mannhi1601@gmail.com"
passwors="admin"
from locust import HttpUser, task
from locust_check.keys import key_43,key_aws
from locust_check.datas import congty_csc,lacviet_demo,congty_csc_2,get_data,data_get_folder
tenant="lacvietdemo"
#https://apps.codx.vn/api/Auth/exec52
data_test_list=[
    get_data(data_get_folder,"congtycsc","admin")
]
assemblyName=["FileBussiness"]

class CongTyCSCUser(HttpUser):
    #http://172.16.7.34:8011/api/WP/exec71
    #https://apps.codx.vn/api/WP/exec30"
    @task
    def login(self):
        # self.client.verify = False
        #http://172.16.7.34:8011/api/Auth/exec23
        print("/api/WP/exec71")
        #http://172.16.7.34:8011/api/WP/exec19
        for x in data_test_list:
            self.client.post("/api/TM/exec23", json= x,headers= {
                "lvtk":key_43
            })

    # @task
    # def home(self):
    #     self.client.verify = False
    #     print("/congtycsc/wp/portal/WP")
    #     self.client.get("/congtycsc/wp/portal/WP")
#
if __name__ == "__main__":
    import locust

    locust.main()