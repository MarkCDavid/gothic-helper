from ctypes import c_int32, sizeof
import struct
from g2.memory.Objects import Object, ObjectField
from handlers.base_handlers import default_handler, int32_handler, mat4_handler, string_handler, uint32_handler

class Item(Object):
    def __init__(self, process, address):
        super().__init__(process, address)

        self.objectName = ObjectField(self, 0x0018)
        self.name = ObjectField(self, 0x012C)
        self.transform = ObjectField(self, 0x003C)

class ItemField(ObjectField):

    def resolve(self, fieldsToResolve, pointerMap):
        super().resolve(fieldsToResolve, pointerMap)

        fieldSlice = slice(self.offset, self.offset + sizeof(c_int32))
        (self.value, ) = struct.unpack("@i", self.parent.blob[fieldSlice])
        address = self.value

        if address == 0:
            return

        if address in pointerMap:
            return

        item = Item(self.parent.process, self.value)
        item.load_memory()
        self.pointerMap[address] = item
