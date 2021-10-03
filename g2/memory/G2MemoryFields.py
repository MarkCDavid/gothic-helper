from ctypes import c_int32, sizeof
import struct
from g2.memory.Objects import ObjectField

class G2MemoryInt32Field(ObjectField):
    def resolve(self, fieldsToResolve, pointerMap):
        super().resolve(fieldsToResolve, pointerMap)
        field_slice = slice(self.offset, self.offset + sizeof(c_int32))
        (self.value,) = struct.unpack("@i", self.parent.blob[field_slice])