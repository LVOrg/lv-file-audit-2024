#!/bin/bash
#sh "/root/harbor_ssl_install.sh"
function trustHarborCA() {

    local harbor_url=$1
    sudo mkdir -p /etc/docker/certs.d
    sudo mkdir -p /etc/docker/certs.d/$harbor_url
    sudo chmod +777 /etc/docker/certs.d/$harbor_url/
    curl -sk https://$harbor_url/api/v2.0/systeminfo/getcert >~/$harbor_url-ca.crt
    echo 'Download ca.crt from' $harbor_url

    echo cp -rf ~/$harbor_url-ca.crt /etc/docker/certs.d/$harbor_url/ca.crt
    sudo cp -rf ~/$harbor_url-ca.crt /etc/docker/certs.d/$harbor_url/ca.crt

    echo cp -rf ~/$harbor_url-ca.crt /etc/pki/ca-trust/source/anchors/$harbor_url-ca.crt
    sudo cp -rf ~/$harbor_url-ca.crt /etc/pki/ca-trust/source/anchors/$harbor_url-ca.crt

    echo cp -rf ~/$harbor_url-ca.crt $HOME/.docker/tls/$harbor_url/$harbor_url-ca.crt

    sudo cp -rf ~/$harbor_url-ca.crt $HOME/.docker/tls/$harbor_url/$harbor_url-ca.crt


    echo update-ca-trust
    sudo update-ca-trust

sudo cat >>/etc/containerd/config.toml <<EOF
[registry."$harbor_url"]
http = false
insecure = false
ca=["/etc/docker/certs.d/$harbor_url/ca.crt"]
EOF
    echo Create file /etc/containerd/config.toml

    echo systemctl restart containerd
    sudo systemctl restart containerd

    #echo systemctl restart docker
    #systemctl restart docker
    echo Deleting $harbor_url-ca.crt, "$0"
    sudo rm -f ~/$harbor_url-ca.crt

    #echo docker buildx create --use --config /etc/containerd/config.toml
    #r
    # sudo rm -f "$0"
}
trustHarborCA "docker.lacviet.vn"