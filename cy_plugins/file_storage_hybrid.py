class HybridFileStorage:
    def seek(self, position):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def read(self, size) -> bytes:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_cursor(self, from_index, num_of_element, cursor):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def push(self, content: bytes, chunk_index):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_id(self) -> str:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def push_async(self, content: bytes, chunk_index):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def tell(self):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def close(self):
        """
            some how to implement thy source here ...
                """
        raise NotImplemented

    def get_size(self):
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented

    def get_id_async(self) -> str:
        """
        somehow to implement thy source here ...
        """
        raise NotImplemented