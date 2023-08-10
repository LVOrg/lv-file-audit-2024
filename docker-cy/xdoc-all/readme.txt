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
ssh -o StrictHostKeyChecking=no -i "lv_keyPair.pem" ec2-user@13.212.181.67
helm --set name=lv-job upgrade --install ???? xdoc/xdoc-all
helm --set name=lv-web upgrade --install ??? xdoc/xdoc-all
helm --set name=dev-job-only upgrade --install xdoc-job-18 xdoc/xdoc-all
helm --set name=dev-web-only template xdoc-all
helm --set name=dev-web-only upgrade --install xdoc-web-1 xdoc/xdoc-all