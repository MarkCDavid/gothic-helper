from g2.item import ItemField
from g2.memory.G2MemoryFields import G2MemoryInt32Field
from g2.memory.Objects import Object, ObjectField
from g2.sortList import SortListField
# from g2.voblist import VOBListItem, VOBListNpc
# from handlers.base_handlers import custom_handler_factory, default_handler, int32_handler, string_handler

class World(Object):

    def __init__(self, process, address, size = 0x628C):
        super().__init__(process, address, size)

        self.hashIndex = G2MemoryInt32Field(self, 0x0008)
        self.itemList = SortListField(self, 0x6288, ItemField)
        # self.fields = {
            # "hashIndex": (0x0008, int32_handler),
            # "worldName": (0x6274, string_handler),
            # "voblist_npcs": (0x6284, custom_handler_factory(VOBListNpc)),
            # "voblist_items": (0x6288, custom_handler_factory(VOBListItem))
        # }
    