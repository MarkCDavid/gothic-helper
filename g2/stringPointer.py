from g2.base import Int32Field, StringField
from g2.memory.objectSize import SIZE_POINTER
from g2.memory.objects import Object, ObjectField, PointerField

class StringPointer(Object):
    def __init__(self, process, address, size=SIZE_POINTER):
        super().__init__(process, address, size)
        self.string = StringField(self, 0x0000, size)

class StringPointerField(PointerField):
    def __init__(self, parent, offset):
        super().__init__(parent, offset)
        self.type = type

    def create_object(self):
        return StringPointer(self.parent.process, self.address, self.parent.length)