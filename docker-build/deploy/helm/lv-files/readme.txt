helm  template lv-file>>test.yml
helm install lv-file2 lv-files --values ./../values/99.yml
helm upgrade --install files lv-files --values ./../values/99.yml
helm template lv-files --values ./../values/99-qc.yml>>new.yml

helm upgrade --install files lv-files --values ./../values/99-qc.yml
helm upgrade --install files lv-files --values ./../values/91.yml
helm upgrade --install files-dev lv-files --values ./../values/99-dev.yml
helm cm-push ./lv-files xdoc
helm  template lv-files --values ./../values/91-filelv.yml>>test.yml
helm upgrade --install files-cloud lv-files --values ./../values/91-filelv.yml
#files
helm upgrade --install xdoc-2 xdoc/lv-files --values /tmp/qc.yml