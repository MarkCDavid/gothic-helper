from dataclasses import field
import struct
import numpy as np
from collections import namedtuple
from process.sizes import SIZE_UINT32, SIZE_ZSTRING, SIZE_MAT4

VOB_TYPE_VOB = 0
VOB_TYPE_LIGHT = 1
VOB_TYPE_SOUND = 2
VOB_TYPE_STARTPOINT = 6
VOB_TYPE_WAYPOINT = 7
VOB_TYPE_MOB = 128
VOB_TYPE_ITEM = 129
VOB_TYPE_NPC = 130

FieldData = namedtuple("FieldData", ["offset", "format", "size"])


class Core:
    def __init__(self, process, address):
        self.process = process
        self.address = address

    def load(self):
        pass

    def _read(self, fieldData):
        return self.process.read_fd(self.address, fieldData)

    def _read_string(self, fieldData):
        (address, length) = self._read(fieldData)
        if address == 0 or length < 0 or length > 500:
            return ""
        return self.process.read_memory(address, length).decode("ascii")


class Object(Core):
    FD_OBJECT_NAME = FieldData(0x0018, "@Ii", SIZE_ZSTRING)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.objectName = None

    def getName(self) -> str:
        return self.objectName

    def load(self):
        super().load()
        self.objectName = self._read_string(Object.FD_OBJECT_NAME)


class Vob(Object):
    FD_TRANSFORM = FieldData(0x003C, "@ffffffffffffffff", SIZE_MAT4)
    FD_VOB_TYPE = FieldData(0x00B0, "@I", SIZE_UINT32)
    FD_HOME_WORLD = FieldData(0x00B8, "@I", SIZE_UINT32)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.transform = None
        self.vobType = None
        self.homeWorld = None

    def load(self):
        super().load()
        self.transform = Mat4(self._read(Vob.FD_TRANSFORM))
        self.vobType = self.getVobType(self.process, self.address)
        self.homeWorld = self._read(Vob.FD_HOME_WORLD)

    @staticmethod
    def getVobType(process, address):
        return process.read_fd(address, Vob.FD_VOB_TYPE)


class Item(Vob):
    FD_NAME = FieldData(0x012C, "@Ii", SIZE_ZSTRING)
    FD_OWNER = FieldData(0x0200, "@I", SIZE_UINT32)
    FD_DESCRIPTION = FieldData(0x027C, "@Ii", SIZE_ZSTRING)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.name = None
        self.owner = None
        self.description = None

    def getName(self):
        return self.description

    def load(self):
        super().load()
        self.name = self._read_string(Item.FD_NAME)
        self.owner = self._read(Item.FD_OWNER)
        self.description = self._read_string(Item.FD_DESCRIPTION)


class Npc(Vob):
    FD_NAME = FieldData(0x012C, "@Ii", SIZE_ZSTRING)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.name = None

    def getName(self):
        return self.name

    def load(self):
        super().load()
        self.name = self._read_string(Npc.FD_NAME)


class Mob(Vob):
    FD_NAME = FieldData(0x0128, "@Ii", SIZE_ZSTRING)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.name = None

    def getName(self):
        return self.name

    def load(self):
        super().load()
        self.name = self._read_string(Mob.FD_NAME)


class Camera(Core):
    FD_VIEW_MATRIX = FieldData(0x0148, "@ffffffffffffffff", SIZE_MAT4)
    FD_PROJECTION_MATRIX = FieldData(0x0814, "@ffffffffffffffff", SIZE_MAT4)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.viewMatrix = None
        self.projectionMatrix = None

    def load(self):
        self.viewMatrix = Mat4(self._read(Camera.FD_VIEW_MATRIX))
        self.projectionMatrix = Mat4(self._read(Camera.FD_PROJECTION_MATRIX))


class Mat4:
    def __init__(self, binary):
        (
            self.m11,
            self.m12,
            self.m13,
            self.m14,
            self.m21,
            self.m22,
            self.m23,
            self.m24,
            self.m31,
            self.m32,
            self.m33,
            self.m34,
            self.m41,
            self.m42,
            self.m43,
            self.m44,
        ) = binary

    def get_coordinates(self):
        return (self.m14, self.m24, self.m34, self.m44)

    def as_list(self):
        return [
            [self.m11, self.m12, self.m13, self.m14],
            [self.m21, self.m22, self.m23, self.m24],
            [self.m31, self.m32, self.m33, self.m34],
            [self.m41, self.m42, self.m43, self.m44],
        ]

    def npmatrix(self):
        return np.mat(self.as_list())
