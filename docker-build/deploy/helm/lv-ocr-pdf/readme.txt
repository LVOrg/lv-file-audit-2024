example:
helm upgrade --install lv-ocr-pdf xdoc/lv-ocr-pdf --set nfs_server=192.168.18.36,nfs_path=/codx-file-storage/files,ns=files,version=v01,db_codx=
db_codx is '' if lv file and codx is in same database
