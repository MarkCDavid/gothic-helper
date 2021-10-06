import struct
import numpy as np
from collections import namedtuple
from process.sizes import SIZE_UINT32, SIZE_ZSTRING, SIZE_MAT4

VOB_TYPE_VOB        = 0
VOB_TYPE_LIGHT		= 1
VOB_TYPE_SOUND		= 2
VOB_TYPE_STARTPOINT = 6
VOB_TYPE_WAYPOINT	= 7
VOB_TYPE_MOB		= 128
VOB_TYPE_ITEM		= 129
VOB_TYPE_NPC		= 130

FieldData = namedtuple("FieldData", ["offset", "size"])

class Core:
    def __init__(self, process, address):
        self.process = process
        self.address = address

    def load(self):
        pass

    def _read(self, fieldData):
        return self.process.read_memory(self.address + fieldData.offset, fieldData.size)

    def _read_string(self, fieldData):
        memory = self.process.read_memory(self.address + fieldData.offset, fieldData.size)
        (address, length) = struct.unpack("@Ii", memory)
        if address == 0:
            return None
        return self.process.read_memory(address, length).decode("ascii")

class Object(Core):
    FD_OBJECT_NAME = FieldData(0x0018, SIZE_ZSTRING)
    def __init__(self, process, address):
        super().__init__(process, address)
        self.objectName = None

    def load(self):
        super().load()
        self.objectName = self._read_string(Object.FD_OBJECT_NAME)

class Vob(Object):
    FD_TRANSFORM = FieldData(0x003C, SIZE_MAT4)
    FD_VOB_TYPE = FieldData(0x00B0, SIZE_UINT32)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.transform = None
        self.vobType = None

    def load(self):
        super().load()
        self.transform = Mat4(self._read(Vob.FD_TRANSFORM))
        self.vobType = self.getVobType(self.process, self.address)

    @staticmethod
    def getVobType(process, address):
        memory = process.read_memory(address + Vob.FD_VOB_TYPE.offset, Vob.FD_VOB_TYPE.size)
        return struct.unpack("@I", memory)[0]

class Item(Vob):
    FD_NAME = FieldData(0x012C, SIZE_ZSTRING)
    FD_DESCRIPTION = FieldData(0x027C, SIZE_ZSTRING)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.name = None
        self.description = None

    def load(self):
        super().load()
        self.name = self._read_string(Item.FD_NAME)
        self.description = self._read_string(Item.FD_DESCRIPTION)

class Npc(Vob):
    FD_NAME = FieldData(0x012C, SIZE_ZSTRING)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.name = None

    def load(self):
        super().load()
        self.name = self._read_string(Npc.FD_NAME)

class Mob(Vob):
    FD_NAME = FieldData(0x0128, SIZE_ZSTRING)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.name = None

    def load(self):
        super().load()
        self.name = self._read_string(Mob.FD_NAME)

class Camera(Core):
    FD_VIEW_MATRIX = FieldData(0x0148, SIZE_MAT4)
    FD_PROJECTION_MATRIX = FieldData(0x0814, SIZE_MAT4)

    def __init__(self, process, address):
        super().__init__(process, address)
        self.viewMatrix = None
        self.projectionMatrix = None

    def load(self):
        self.viewMatrix = Mat4(self._read(Camera.FD_VIEW_MATRIX))
        self.projectionMatrix = Mat4(self._read(Camera.FD_PROJECTION_MATRIX))

class Mat4:
    def __init__(self, binary):
        (self.m11, self.m12, self.m13, self.m14,
         self.m21, self.m22, self.m23, self.m24,
         self.m31, self.m32, self.m33, self.m34,
         self.m41, self.m42, self.m43, self.m44) = struct.unpack("@ffffffffffffffff", binary)
    
    def get_coordinates(self):
        return (self.m14, self.m24, self.m34, self.m44)

    def as_list(self):
        return [[self.m11, self.m12, self.m13, self.m14],
                [self.m21, self.m22, self.m23, self.m24],
                [self.m31, self.m32, self.m33, self.m34], 
                [self.m41, self.m42, self.m43, self.m44]]

    def npmatrix(self):
        return np.mat(self.as_list())

