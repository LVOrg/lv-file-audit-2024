#!/bin/bash
yum update
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum remove -y docker-ce
yum remove -y docker-ce-cli
yum remove -y containerd.io
yum remove -y docker-buildx-plugin
yum remove -y docker-compose-plugin

yum install -y docker-ce
yum install -y docker-ce-cli
yum install -y containerd.io
yum install -y docker-buildx-plugin
yum install -y docker-compose-plugin
systemctl start docker
sudo yum install -y docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine