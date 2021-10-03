from ctypes import c_int32, sizeof
import struct
from typing import Any
from process.process import Process


class Object:
    def __init__(self, process, address, size):
        self.process: Process = process
        self.address: int = address
        self.size: int = size
        self.blob: bytes = None

    def get_fields(self):
        fields = []
        for _, field in self.__dict__.items():
            if isinstance(field, ObjectField):
                fields.append(field)
        return list(sorted(fields, key=lambda f: f.priority, reverse=True))

    def load_memory(self):
        self.blob = self.process.read_memory(self.address, self.size)

    def __getattribute__(self, name: str) -> "Any":
        attribute = super().__getattribute__(name)
        if isinstance(attribute, ObjectField):
            return attribute.get_value()
        return attribute
        
    def __getitem__(self, index):
        if isinstance(index, tuple):
            return None
        return self.values[index]

    def _get_repr_values(self):
        values = []
        for name, field in self.__dict__.items():
            if isinstance(field, ObjectField):
                values.append((name, field))
        return values

    def __str__(self) -> str:
        values = "\n\t".join([f"{name}: {value}" for (name, value) in self._get_repr_values()])
        return f"<{type(self).__name__}> at {hex(self.address)}\n\t{values}"


class ObjectField:
    def __init__(self, parent, offset, name, priority=0):
        self.parent: "Object" = parent
        self.offset: int = offset
        self.priority: int = priority
        self.name: str = name

    def resolve(self, fieldsToResolve, pointerMap, forceUpdatePointerMap = False):
        self.pointerMap = pointerMap

    def get_value(self):
        return None

    def __str__(self) -> str:
        return f"<{type(self).__name__}> {self.name}"

class InlineObjectField(ObjectField):
    def resolve(self, fieldsToResolve, pointerMap, forceUpdatePointerMap = False):
        super().resolve(fieldsToResolve, pointerMap, forceUpdatePointerMap)
       
        address = self.parent.address + self.offset
        if not forceUpdatePointerMap and address in pointerMap:
            return

        self.object = self.pointerMap[address] if address in self.pointerMap else self.create_object() 
        self.load_blob()
        self.pointerMap[address] = self.object

        for field in self.object.get_fields():
            fieldsToResolve.put(field)

    def load_blob(self):
        pass

    def get_value(self):
        return self.object

    def create_object(self):
        raise NotImplementedError()


class PointerField(ObjectField):

    def get_value(self):
        if self.address is None or self.address == 0:
            return None
        elif self.address in self.pointerMap:
            return self.pointerMap[self.address]
        else:
            return self.get_address()

    def get_address(self):
        return self.address

    def resolve(self, fieldsToResolve, pointerMap, forceUpdatePointerMap = False):
        super().resolve(fieldsToResolve, pointerMap, forceUpdatePointerMap)
        
        fieldSlice = slice(self.offset, self.offset + sizeof(c_int32))
        (self.address, ) = struct.unpack("@i", self.parent.blob[fieldSlice])

        if self.address == 0:
            return

        if not forceUpdatePointerMap and self.address in pointerMap:
            return

        object = self.pointerMap[self.address] if self.address in self.pointerMap else self.create_object()
        object.load_memory()
        self.pointerMap[self.address] = object

        for field in object.get_fields():
            fieldsToResolve.put(field)
    
    def create_object(self):
        raise NotImplementedError()
