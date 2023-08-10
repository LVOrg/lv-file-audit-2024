Thou!!!! </br>
Please, read carefully to avoid mistake. </br>
Thou will pay extremely cost if thou just glance this. </br>
------------------------------------------------------- </br>
In this directory thou just care about bellow list, no more.. </br>
------------------------------------------------------ </br>
data </br>
├── aws.yml                             # AWS deployment-value </br>
├── lacviet.yml                         # Lac Viet deployment-value </br>
├── dev.yml                             # Dev and QC deployment-value </br>
├── jobs.app.yml                        # List of File-Job values </br>
└── job.cron.yml                        # List of Cron-Job values, all Cron Job POD run one time </br>
templates
├── web.apps.yml                        # Web API pod deployment </br>
├── web.config.yml                      # All config for Web API </br>
├── web.namespace.yml                   # Namespace for Web API, wrong namespace will make chain of  error,  through and through all PODs </br>
├── web.service.yml                     # Make a service link to web app. The service allow another POD can access to Web Api app </br>
├── jobs.config.yml                     # All configuration infor serve for JOB and cron job </br>
├── jobs.apps.yml                       # All apps in which File-Processing run </br>
├── jobs.cron.yml                       # All dataset deployment </br>
├── jobs.namespace.yml                  # Namespace for Job and cron job deploy </br>
├── long.horn.namespace.yml             # Longhorn namespace.Till now, Longhorn is unofficially volume (pilot test) </br>
└── long.horn.yml                       # Longhorn claim </br>

In directory data at helm chart directory, thera a fews of YAML files in which is data of template render </br>
In order to deploy with a new environment (environment is a collect of Mongo Database server, ElasticSearch, RabbitMQ ,..) </br>
Thou should clone /data/dev.yml into new file in /data with a new name. </br>
Example: cp /data/dev/yml /data/my-data.yml </br>
The run command looks like helm --set name=<data file name only in /data directory> install <release name> <path to helm chart directory> </br>
Example: helm --set name=dev-job-only install xdoc-job-17 xdoc-all </br>

<div style="display:hidden">
Use ssh copy to copy </br>
scp -r root@172.16.13.72:/home/vmadmin/python/v6/file-service-02/docker-cy/xdoc-all /nttlong/helm/xdoc-job </br>
</div>
helm repo add --username xdoc --password ???? xdoc https://docker.lacviet.vn/chartrepo/xdoc </br>
helm registry login -u codx docker.lacviet.vn </br>
helm cm-push ./codxservice codx </br>

helm --set name=dev-job-only upgrade --install xdoc xdoc/xdoc-all
