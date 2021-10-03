import struct
from ctypes import c_char, c_int32, sizeof
from g2.memory.objects import ObjectField


class Int32Field(ObjectField):
    def resolve(self, fieldsToResolve, pointerMap):
        super().resolve(fieldsToResolve, pointerMap)
        field_slice = slice(self.offset, self.offset + sizeof(c_int32))
        (self.value,) = struct.unpack("@i", self.parent.blob[field_slice])

    def get_value(self):
        return self.value


class StringField(ObjectField):
    def __init__(self, parent, offset, size):
        super().__init__(parent, offset)
        self.size = size

    def resolve(self, fieldsToResolve, pointerMap):
        super().resolve(fieldsToResolve, pointerMap)
        field_slice = slice(self.offset, self.offset + sizeof(c_char) * self.size)
        string_bytes = self.parent.blob[field_slice]
        self.value = string_bytes.decode("ascii")

    def get_value(self):
        return self.value