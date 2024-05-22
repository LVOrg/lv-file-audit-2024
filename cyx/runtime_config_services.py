import os.path
import pathlib
import sys

import yaml


class RuntimeConfigService:
    def __init__(self):
        self.directory=os.path.join(pathlib.Path(__file__).parent.parent.__str__(),"runtime")
        if not os.path.isdir(self.directory):
            os.makedirs(self.directory,exist_ok=True)



    def load(self, argv):
        data_list= []
        for x in argv:
            if "=" in x:
                key = x.split('=')[0]
                val = x.split('=')[1]
                if isinstance(val,str):
                    if val.isnumeric():
                        val = int(val)
                data_list+=[(key,val)]
        ret = {}

        for k,v in data_list:
            d= {}
            p=d
            x2 = k.split('.')
            if len(x2)==1:
                ret[k]=v
                continue
            root = ret
            for k1 in x2[0:-1]:
                if root.get(k1):
                    p[k1] = root.get(k1)
                    root = root.get(k1)
                else:
                    root[k1]= {}
                    p[k1] = root.get(k1)
                    root=root.get(k1)
                p= p[k1]
            p[x2[-1]] = v
            # ret= {**ret,**d}

        with open(os.path.join(self.directory,'config.yaml'), 'w') as f:
            # Dump the dictionary to the file as YAML
            yaml.dump(ret, f)

