from g2.memory.objectSize import SIZE_SORTLIST
from g2.memory.objects import Object, ObjectField, PointerField


class SortList(Object):
    def __init__(self, process, address, type, size=SIZE_SORTLIST):
        super().__init__(process, address, size)

        self.compare = ObjectField(self, 0x0000, "compare")
        self.data = type(self, 0x0004, "data")
        self.next = SortListField(self, 0x0008, "next", type)


class SortListField(PointerField):
    def __init__(self, parent, offset, name, type):
        super().__init__(parent, offset, name)
        self.type = type

    def create_object(self):
        return SortList(self.parent.process, self.address, self.type)
