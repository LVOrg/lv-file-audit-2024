import math
import os
import uuid
from hashlib import sha256

from cyx.repository import Repository


class ContentManagerService:
    async def do_check_out_async(self, client_mac_address: str, app_name: str, upload_id: str, file_path: str):

        hash_content = await self.get_hash_contents_async(file_path)
        history = Repository.contents.app(app_name)
        history_object = await history.context.find_one_async(
            (history.fields.UploadId == upload_id) & (history.fields.MacId == client_mac_address)
        )
        if history_object is None:
            await history.context.insert_one_async(
                history.fields.id << str(uuid.uuid4()),
                history.fields.UploadId << upload_id,
                history.fields.HashContents << hash_content,
                history.fields.MacId << client_mac_address
            )
        else:
            await history.context.update_async(
                (history.fields.UploadId == upload_id) & (history.fields.MacId == client_mac_address),
                history.fields.HashContents << hash_content
            )
        return

    async def get_hash_contents_async(self, file_path: str, step: int = 3):
        if os.path.getsize(file_path) == 0:
            return []
        ret_list = []
        hash_size_skip = int(math.floor(os.path.getsize(file_path) / step))
        hash_size = 1024
        with open(file_path, "rb") as f:
            bytes_read = f.read(hash_size)
            while len(bytes_read) > 0:
                skip_to = hash_size_skip + f.tell()
                f.seek(skip_to)
                if len(bytes_read) == 0:
                    return ret_list
                ret = await self.hash_chunk_async(bytes_read)
                ret_list += [ret]
                bytes_read = f.read(hash_size)
        return ret_list

    async def hash_chunk_async(self, data: bytes):
        """
                    Calculates the SHA256 hash of a byte chunk.

                    Args:
                        data: The byte chunk to hash.

                    Returns:
                        The SHA256 hash as a hexadecimal string.
                    """
        hasher = sha256()
        hasher.update(data)
        return hasher.hexdigest()
