from g2.memory.objects import Object, ObjectField, PointerField
from g2.memory.objectSize import SIZE_ITEM


class Item(Object):
    def __init__(self, process, address, size=SIZE_ITEM):
        super().__init__(process, address, size)

        self.objectName = ObjectField(self, 0x0018)
        self.name = ObjectField(self, 0x012C)
        self.transform = ObjectField(self, 0x003C)


class ItemField(PointerField):
    def create_object(self):
        return Item(self.parent.process, self.address)
