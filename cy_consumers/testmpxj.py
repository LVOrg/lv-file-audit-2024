import jpype
import mpxj

jpype.startJVM()
from net.sf.mpxj.sample import MpxjConvert
file=f"/home/vmadmin/python/v6/file-service-02/docker-cy/check/test.mpp"
file2=f"/home/vmadmin/python/v6/file-service-02/docker-cy/check/test.pdf"
MpxjConvert().process(file, file2)
jpype.shutdownJVM()