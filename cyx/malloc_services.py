class MallocService:
    def  reduce_memory(self):
        import ctypes
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)