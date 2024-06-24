import gc
import ctypes
import asyncio
class MallocService:
    def reduce_memory(self):

        gc.collect()
        libc = ctypes.CDLL("libc.so.6")
        libc.malloc_trim(0)

    async def async_reduce_memory(self):
        await asyncio.to_thread(lambda: gc.collect())  # Collect garbage asynchronously

        libc = ctypes.CDLL("libc.so.6")
        await self.run_in_executor(libc.malloc_trim, 0)  # Run malloc_trim asynchronously