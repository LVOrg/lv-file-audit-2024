import gc
import ctypes
import asyncio
import sys
import threading


class MallocService:
    def reduce_memory(self):
        gc.collect()
        if not sys.platform in ["win32","win64"]:
            libc = ctypes.CDLL("libc.so.6")
            libc.malloc_trim(0)

    async def async_reduce_memory(self):
        self.reduce_memory()