import sys
sys.path.append('/app')
import os
from pymongo.mongo_client import MongoClient
if os.path.splitext(sys.modules[MongoClient.__module__].__file__)[1]!=".so":
    raise Exception(sys.modules[MongoClient.__module__].__file__)
else:
    print("MongoClient OK")
from bson import  ObjectId
from gridfs import GridIn
from elasticsearch.transport import Transport

if os.path.splitext(sys.modules[ObjectId.__module__].__file__)[1]!=".so":
    raise Exception(sys.modules[ObjectId.__module__].__file__)
else:
    print("ObjectId OK")
if os.path.splitext(sys.modules[GridIn.__module__].__file__)[1]!=".so":
    raise Exception(sys.modules[GridIn.__module__].__file__)
else:
    print("GridIn OK")
if os.path.splitext(sys.modules[Transport.__module__].__file__)[1]!=".so":
    raise Exception(sys.modules[Transport.__module__].__file__)
else:
    print("Transport OK")