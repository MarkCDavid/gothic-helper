from typing import Any
from process.process import Process


class Object:
    def __init__(self, process, address, size):
        self.process: Process = process
        self.address: int = address
        self.size: int = size
        self.blob: bytes = None
        self.values = {}

    def __getitem__(self, index):
        if isinstance(index, tuple):
            return None
        return self.values[index]

    def update(self, update_queue):
        for field in self.fields:
            offset, handler = self.fields[field]
            self.values[field] = handler(self.process, self.address + offset, update_queue)

    def get_fields(self):
        fields = []
        for _, field in self.__dict__.items():
            if isinstance(field, ObjectField):
                fields.append(field)
        return fields

    def load_memory(self):
        self.blob = self.process.read_memory(self.address, self.size)

    def __getattribute__(self, name: str) -> "Any":
        attribute = super().__getattribute__(name)
        if isinstance(attribute, ObjectField):
            return attribute.value
        return attribute

    def __str__(self) -> str:
        return f"\n{type(self)} address: {hex(self.address)}\n{self.values}\n"


class ObjectField:
    def __init__(self, parent, offset):
        self.parent: "Object" = parent
        self.offset: int = offset
        self.value = None

    def resolve(self, fieldsToResolve, pointerMap):
        self.pointerMap = pointerMap

