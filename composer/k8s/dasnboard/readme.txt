
1- kubectl -f node-port-20036.yml apply
2- kubectl -f service-account.yml apply
3- get token by using: kubectl -n kubernetes-dashboard create token admin-user --duration=8760h
-----------------------------------------------------------------------------------
eyJhbGciOiJSUzI1NiIsImtpZCI6IlU3RWRfUWNIZXJ4ejVHZGh6LVFOWWFTeWFadTlvbDRrOUtwcjk2WG10aW8ifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzExMTYyOTA2LCJpYXQiOjE2Nzk2MjY5MDYsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJhZG1pbi11c2VyIiwidWlkIjoiNzE3MWMwYjEtZTc2Yi00NDMzLTg5M2EtYmMwODI5MWJlMWJkIn19LCJuYmYiOjE2Nzk2MjY5MDYsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDphZG1pbi11c2VyIn0.bN2TwDzTynRF3s2At8gzRiF6q-CXcQDhQ31CR7aMskq7oqNyWw8MV_w2BJotCN_gdHIKzbgHG7cKyJRIr4woU6-pumwa8V-FWmO9OM0mhQ4qAB4WzhOyboTl7zVQ6ja_-XJtty9aDpe8-XM_1nMGne3cyiDJibuwMDwUQno5UgW-YqpnKZC7a9UG1AD0_T-C6kaagUCyo67mTtN2GmArLIvP-5qG1f1i1QsfomiqNZ-0jVss4_3ovbkjbLE0KWQ1QxaaJRKL8hJPUbkwQD-rWAC9nTLafYmN9WLHyebadMgIezgVuCljzJZVYNu6mk9s3k_ymRu8QofgFVB_1CYYuw
docker run -d \
-m 4G \
-p 7070:7070 \
-p 8088:8088 \
-p 50070:50070 \
-p 8032:8032 \
-p 8042:8042 \
-p 2181:2181 \
apachekylin/apache-kylin-standalone:4.0.0
kubectl rollout restart -n xdoc-web deployment xdoc-web
------------------------------------------------------------------------
docker run --pull always --name lakefs   -p 8001:8000 treeverse/lakefs:latest  run --local-settings
------------------------ lacviet ----------------------
eyJhbGciOiJSUzI1NiIsImtpZCI6Ik44bG5xcG1kZG1sczhGSWxPc2JnZXNMVVZydGdvUUlELW81M3pQeTN6QWcifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzA5NjkyOTEzLCJpYXQiOjE2NzgxNTY5MTMsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJhZG1pbi11c2VyIiwidWlkIjoiZWUwMmVkM2EtMjE1NC00YzBlLTk0NDYtMGQwODhiMjc5NDYzIn19LCJuYmYiOjE2NzgxNTY5MTMsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDphZG1pbi11c2VyIn0.XMk8OcqQi5n5BYFApeHh7KVQu5swR63i3PGArL5TbDiO9U87QXOGLaTsTxe-HU_lLQOk5gpCsVHiTehx6gQ8rxS0t8PX9fzbO62zsMCDiNFkqkIaBER7YNAoxsesVpOVKnBWiwf4Nz3bZl0Bu9yXW4SK_1oP0PTLiPq1LgEpt1YGAVEI-nmAaEMkrZK22YymOv_FORjr_B9zn3iIU1C8NbjSnyYtAdoEAatDoeIljXJ5TVukKROQShtWYHogMz-883DFlvTFawZ17lPuBy0XpAdUBM6tMU1D9D43PJwI3xD6-86SctHrizYMUow0gl8MPFqzpeRLPQYb1a8TUTQi2g