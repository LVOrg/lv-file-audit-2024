kubectl drain lacviet-vm18  --delete-local-data --ignore-daemonsets --force
kubectl taint nodes lacviet-vm18 node.kubernetes.io/unschedulable:<taint-value>:<effect> --taints-field-path spec.taints[<index>]
kubectl taint nodes lacviet-vm18 node.kubernetes.io/unschedulable:NoSchedule --taints-field-path spec.taints[0]
#sudo mount -t nfs 172.16.13.72://home/vmadmin/python/cy-py /mnt/k8s
kubectl delete node lacviet-vm18
#    sudo kubeadm init  --pod-network-cidr=10.244.0.0/16