import os.path
import pathlib
import uuid

import aiofiles
from starlette.datastructures import UploadFile,Headers
import os
from cyx.common import config
upload_dir = os.path.join(config.file_storage_path, "__temp_upload__")
os.makedirs(upload_dir,exist_ok=True)
import asyncio
async def write_async(data, filename,mode):
  async with aiofiles.open(filename, mode) as f:
    await f.write(data)
    print(f"Wrote data to {filename}")
async def write(self, data: bytes) -> None:
    mode = "ab"
    if not hasattr(self,"temp_file_path"):
        file_ext = pathlib.Path(self.filename).suffix
        temp_file_path=os.path.join(upload_dir,f"{str(uuid.uuid4())}{file_ext}")
        setattr(self,"temp_file_path",temp_file_path)
        mode="wb"
    await write_async(data,filename=self.temp_file_path,mode=mode)
    # with open(self.temp_file_path,mode) as fs:
    #     fs.write(data)
old_write = getattr(UploadFile,"write")
setattr(UploadFile,"old_write",old_write)
setattr(UploadFile,"write",write)
# from fastapi import UploadFile
# import typing
# class LvUploadFile(UploadFile):
#   """Custom class for uploading files with additional features."""
#
#   def __init__( self,
#         file: typing.BinaryIO,
#         *,
#         size: int | None = None,
#         filename: str | None = None,
#         headers: Headers | None = None,):
#     super().__init__(file,size,filename,headers)
#
#   async def write(self, data: bytes) -> None:
#       if self.size is not None:
#           self.size += len(data)
#
#       if self._in_memory:
#           self.file.write(data)
#       else:
#           await run_in_threadpool(self.file.write, data)