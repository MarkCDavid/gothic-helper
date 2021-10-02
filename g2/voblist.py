from g2.G2MemoryObject import G2MemoryObject
from g2.item import Item
from g2.npc import Npc
from handlers.base_handlers import custom_handler_factory, default_handler, uint32_handler

class VOBListItem(G2MemoryObject):
    def __init__(self, process, address):
        super().__init__(process, address)
        self.fields = {
            "compare": (0x0000, default_handler),
            "data": (0x0004, custom_handler_factory(Item)),
            "next": (0x0008, custom_handler_factory(VOBListItem)),
        }

class VOBListNpc(G2MemoryObject):
    def __init__(self, process, address):
        super().__init__(process, address)
        self.fields = {
            "compare": (0x0000, default_handler),
            "data": (0x0004, custom_handler_factory(Npc)),
            "next": (0x0008, custom_handler_factory(VOBListNpc)),
        }

    