import functools
import os

@functools.cache
def get_folder_size(folder_path):
    """
    Calculates the total size of a folder and its subfolders recursively.

    Args:
        folder_path (str): The path to the folder for which to calculate the size.

    Returns:
        int: The total size of the folder and its subfolders in bytes.
    """

    total_size = 0


    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            try:
                # Use os.stat to get file size, avoiding potential errors
                file_size = os.stat(file_path).st_size
            except OSError as e:
                continue  # Skip to the next file if there's an error
            total_size += file_size
    return total_size
class ReadChunksIO:
    def __init__(self,dir_path,original_open_file):
        self.dir_path = dir_path
        self.original_open_file = original_open_file
        self.pos=0

    @functools.cache
    def get_chunk_size(self):
        return os.stat(os.path.join(self.dir_path,"0")).st_size
    @functools.cache
    def get_size(self):
        return get_folder_size(self.dir_path)
    def seek(self,*args,**kwargs):
        if args:
            self.pos = args[0]
        else:
            raise NotImplementedError(f"{type(self)}.seek")
    def tell(self,*args,**kwargs):
        if not args and not kwargs:
            return self.pos
        else:
            raise NotImplementedError(f"{type(self)}.tell")
    def read(self,*args,**kwargs):
        if args:
            if len(args)==1:
                read_size=args[0]
                read_from = self.pos
                read_to = read_from+read_size
                file_start = read_from // self.get_chunk_size()
                offset_start = self.pos - file_start * self.get_chunk_size()
                file_end = read_to // self.get_chunk_size() +1 if read_to % self.get_chunk_size()>0 else 0
                offset_end = self.get_chunk_size() - file_end * self.get_chunk_size()
                i= file_start
                ret = bytes([])
                fs_read_size=0
                current_file= file_start
                while len(ret)<read_size:

                    # print(f"{self.dir_path}/{i}")
                    if not os.path.isfile(f"{self.dir_path}/{current_file}"):
                        return ret
                    #     print(f"{self.dir_path}/{i}")
                    with self.original_open_file(f"{self.dir_path}/{current_file}","rb") as fs:
                        fs.seek(offset_start)
                        remain_size =min( read_size-len(ret),self.get_chunk_size())
                        data = fs.read(remain_size)
                        while data:
                            ret+=data
                            if len(ret)>=read_size:
                                break
                            remain_size = min(len(ret) - fs_read_size, self.get_chunk_size())
                            data = fs.read(remain_size)
                        current_file+=1
                        offset_start=0

                    i+=1
                self.pos+=len(ret)
                return  ret



                # if rea_size>=self.get_size():
                #     with self.original_open_file(os.path.join(self.dir_path,"0")) as fs:
                #         return fs.read()

        print(args)
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return self
