from g2.G2MemoryObject import G2MemoryObject
from g2.voblist import VOBList
from handlers.base_handlers import custom_handler_factory, default_handler, int32_handler, string_handler

class World(G2MemoryObject):
    def __init__(self, process, address):
        super().__init__(process, address)
        self.fields = {
            "hashIndex": (0x0008, int32_handler),
            "worldName": (0x6274, string_handler),
            "voblist_npcs": (0x6284, default_handler),
            "voblist_items": (0x6288, custom_handler_factory(VOBList))
        }
    