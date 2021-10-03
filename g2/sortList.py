from ctypes import c_int32, sizeof
import struct
from g2.memory.Objects import Object, ObjectField

# class VOBListItem(G2MemoryObject):
#     def __init__(self, process, address):
#         super().__init__(process, address)
#         self.fields = {
#             "compare": (0x0000, default_handler),
#             "data": (0x0004, custom_handler_factory(Item)),
#             "next": (0x0008, custom_handler_factory(VOBListItem)),
#         }

class SortList(Object):
    def __init__(self, process, address, type, size=0x000C):
        super().__init__(process, address, size)

        self.compare = ObjectField(self, 0x0000)
        self.data = type(self, 0x0004)
        self.next = SortListField(self, 0x0008, type)

class SortListField(ObjectField):

    def __init__(self, parent, offset, type):
        super().__init__(parent, offset)
        self.type = type

    def resolve(self, fieldsToResolve, pointerMap):
        super().resolve(fieldsToResolve, pointerMap)

        fieldSlice = slice(self.offset, self.offset + sizeof(c_int32))
        (self.value, ) = struct.unpack("@i", self.parent.blob[fieldSlice])
        address = self.value

        if address == 0:
            return

        if address in pointerMap:
            return

        sortList = SortList(self.parent.process, self.value, self.type)
        sortList.load_memory()
        self.pointerMap[address] = sortList


