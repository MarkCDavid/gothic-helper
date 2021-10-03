from g2.base import Int32Field
from g2.memory.objectSize import SIZE_ZSTRING
from g2.stringPointer import StringPointerField
from g2.memory.objects import InlineObjectField, Object, ObjectField, PointerField

class zString(Object):
    def __init__(self, process, address, size=SIZE_ZSTRING):
        super().__init__(process, address, size)

        self.unknown1 = ObjectField(self, 0x0000)
        self.unknown2 = ObjectField(self, 0x0004)
        self.string = StringPointerField(self, 0x0008)
        self.length = Int32Field(self, 0x000C, 1)
        self.allocated = Int32Field(self, 0x0010)

class zStringField(InlineObjectField):
    def __init__(self, parent, offset):
        super().__init__(parent, offset)

    def load_blob(self, object):
        blob_slice = slice(self.offset, self.offset + SIZE_ZSTRING)
        object.blob = self.parent.blob[blob_slice]
    
    def create_object(self):
        return zString(self.parent.process, self.parent.address)


class zStringPointerField(PointerField):
    def __init__(self, parent, offset):
        super().__init__(parent, offset)

    def create_object(self):
        return zString(self.parent.process, self.address)
