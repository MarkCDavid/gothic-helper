from g2.G2MemoryObject import G2MemoryObject
from handlers.base_handlers import default_handler, int32_handler, mat4_handler, string_handler, uint32_handler

class Item(G2MemoryObject):
    def __init__(self, process, address):
        super().__init__(process, address)
        self.fields = {
            "objectName": (0x0018, string_handler),
            "name": (0x012C, string_handler),
            "transform": (0x003C, mat4_handler),
        }
