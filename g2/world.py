from g2.item import ItemField
from g2.base import Int32Field
from g2.memory.objectSize import SIZE_WORLD
from g2.memory.objects import Object
from g2.sortList import SortListField
from g2.zstring import zStringField

class World(Object):
    def __init__(self, process, address, size=SIZE_WORLD):
        super().__init__(process, address, size)

        self.hashIndex = Int32Field(self, 0x0008)
        self.worldName = zStringField(self, 0x626C)
        self.itemList = SortListField(self, 0x6288, ItemField)
        # self.fields = {
            # "hashIndex": (0x0008, int32_handler),
            # "worldName": (0x6274, string_handler),
            # "voblist_npcs": (0x6284, custom_handler_factory(VOBListNpc)),
            # "voblist_items": (0x6288, custom_handler_factory(VOBListItem))
        # }
    