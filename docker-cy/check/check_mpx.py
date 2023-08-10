import os.path
import pathlib
import jpype
import mpxj
working_dir = pathlib.Path(__file__).parent.__str__()
jpype.startJVM()
from net.sf.mpxj.sample import MpxjConvert
file=os.path.join(working_dir,"test.mpp")
file2=os.path.join(working_dir,"test.mpx")
MpxjConvert().process(file, file2)
jpype.shutdownJVM()