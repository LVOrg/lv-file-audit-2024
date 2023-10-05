#!/bin/bash
rpm -ivh https://repo.mongodb.org/redhat/mongo/mongodb-org-4.2.repo
yum install mongodb-org-4.2
systemctl start mongod
systemctl status mongod
sudo mount -t cifs //192.168.18.36/mongodb-nodes /mnt/mongodb-nodes -o username=Administrator,password=l/\cviet2022

cp -r data /home/db