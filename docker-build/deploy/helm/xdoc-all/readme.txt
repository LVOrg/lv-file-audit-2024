Thou!!!!
Please, read carefully to avoid mistake.
Thou will pay extremely cost if thou just glance this.
-------------------------------------------------------
In this directory thou just care about bellow list, no more..
------------------------------------------------------
data
├── aws.yml                             # AWS deployment-value
├── lacviet.yml                         # Lac Viet deployment-value
├── dev.yml                             # Dev and QC deployment-value
├── jobs.app.yml                        # List of File-Job values
└── job.cron.yml                        # List of Cron-Job values, all Cron Job POD run one time
templates
├── web.apps.yml                        # Web API pod deployment
├── web.config.yml                      # All config for Web API
├── web.namespace.yml                   # Namespace for Web API, wrong namespace will make chain of error,  through and through all PODs
├── web.service.yml                     # Make a service link to web app. The service allow another POD can access to Web Api app
├── jobs.config.yml                     # All configuration infor serve for JOB and cron job
├── jobs.apps.yml                       # All apps in which File-Processing run
├── jobs.cron.yml                       # All dataset deployment
├── jobs.namespace.yml                  # Namespace for Job and cron job deploy
├── long.horn.namespace.yml             # Longhorn namespace.Till now, Longhorn is unofficially volume (pilot test)
└── long.horn.yml                       # Longhorn claim

In directory data at helm chart directory, thera a fews of YAML files in which is data of template render
In order to deploy with a new environment (environment is a collect of Mongo Database server, ElasticSearch, RabbitMQ ,..)
Thou should clone /data/dev.yml into new file in /data with a new name.
Example: cp /data/dev/yml /data/my-data.yml
The run command looks like helm --set name=<data file name only in /data directory> install <release name> <path to helm chart directory>
Example: helm --set name=dev-job-only install xdoc-job-17 xdoc-all


Use ssh copy to copy

scp -r root@172.16.13.72:/home/vmadmin/python/v6/file-service-02/docker-cy/xdoc-all /nttlong/helm/xdoc-job
helm repo add --username xdoc --password Lacviet#123 xdoc https://docker.lacviet.vn/chartrepo/xdoc
helm registry login -u codx docker.lacviet.vn
helm cm-push ./xdoc-all xdoc
helm cm-push ./deploy/helm/xdoc-all xdoc
ssh -o StrictHostKeyChecking=no -i "lv_keyPair.pem" ec2-user@13.212.181.67
helm --set name=aws-web-qc install aws-web-qc xdoc/xdoc-all
helm --set name=lv-job upgrade --install ???? xdoc/xdoc-all
helm --set name=lv-web upgrade --install ??? xdoc/xdoc-all
helm --set name=dev-job-only upgrade --install xdoc-job-18 xdoc/xdoc-all
helm --set name=dev-web-only upgrade --install xdoc-web-1 xdoc/xdoc-all
helm --set name=dev-web-only template xdoc-all
helm --set name=aws-web-qc template xdoc-all
helm --set name=dev-web-99 template xdoc-all
helm --set name=dev-web-99 upgrade --install xdoc xdoc-all
helm --set name=dev-job-99 upgrade --install xdoc-job xdoc-all

helm --set name=lv-job template xdoc-all>>lv-job-test.yml
helm --set name=dev-job-99 template xdoc-all>>test.yml
helm --set name=aws-web template xdoc-all>>test.yml
helm --set name=dev-web-only upgrade --install xdoc-web-1 xdoc/xdoc-all
helm --set name=dev-web-only upgrade --install xdoc-web-1 xdoc/xdoc-all
helm --set name=qtsc-web upgrade --install xdoc-web-1 xdoc/xdoc-all
helm --set name=digipro-web install xdoc xdoc/xdoc-all
helm --set name=digipro-job install xdoc-job xdoc/xdoc-all
eyJhbGciOiJSUzI1NiIsImtpZCI6IlU3RWRfUWNIZXJ4ejVHZGh6LVFOWWFTeWFadTlvbDRrOUtwcjk2WG10aW8ifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzI3NDkzODU4LCJpYXQiOjE2OTU5NTc4NTgsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJhZG1pbi11c2VyIiwidWlkIjoiNzE3MWMwYjEtZTc2Yi00NDMzLTg5M2EtYmMwODI5MWJlMWJkIn19LCJuYmYiOjE2OTU5NTc4NTgsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDphZG1pbi11c2VyIn0.vW64Vj5BMBnba0XOkcQ3XucEcRN1qncoDf1fE5HZbn1yHbgRG2YcRdVt2HoUNLn9-KhBuQx-fcHzsCw70A_YkqD4ig6g6MwjaIZyCWNaxKfxlIrhYVGYbOpsJYOCcGeUKmOvMYU4mVnobcaClYjxpmCD_OUiR-AOpcLyJAeyEb21XbwAVrAty8TiP2O6tD1plUqQz8ngZk5iNLtvLr5_2NicjxhLl2YSzol_CaMWjuebMUvzBdqRhE_wZf7AcmLudWbCCTl8m_3JU7J7HqqXMLppKTrDBbvaiLb6PqIwmT0TKH_PoxtPy46WpwNG6jX_bS83r3E4RyV8ipku84cgiQ



