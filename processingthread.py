import math
import struct
from PyQt5 import QtCore
import numpy as np

from g2.memory.objectSize import SIZE_MAT4, SIZE_POINTER
from pointer_paths import NPC_LIST_PATH, WORLD_OBJECT_LIST_PATH

HERO_OBJECT_NAME = "PC_HERO"

class Item:
    OFFSET_TRANSFORM = 0x003C
    OFFSET_DESCRIPTION = 0x0274

    def __init__(self, address, process):
        self.address = address
        self.process = process

    def load(self):
        mat4 = self.process.read_memory(self.address + self.OFFSET_TRANSFORM, SIZE_MAT4)
        zstrptr_packed = self.process.read_memory(self.address + self.OFFSET_DESCRIPTION + 0x08, 2 * SIZE_POINTER)
        (  strprt, strlen ) = struct.unpack("@Ii", zstrptr_packed)
        self.name = self.process.read_memory(strprt, strlen).decode("ascii")
        self.position = Mat4(mat4)

class WorldObject:
    OFFSET_TRANSFORM = 0x0038
    OFFSET_NAME = 0x0120

    def __init__(self, address, process):
        self.address = address
        self.process = process

    def load(self):
        mat4 = self.process.read_memory(self.address + self.OFFSET_TRANSFORM, SIZE_MAT4)
        zstrptr_packed = self.process.read_memory(self.address + self.OFFSET_NAME + 0x08, 2 * SIZE_POINTER)
        (  strprt, strlen ) = struct.unpack("@Ii", zstrptr_packed)
        self.name = self.process.read_memory(strprt, strlen).decode("ascii")
        self.position = Mat4(mat4)


class Camera:
    OFFSET_VIEW_MATRIX = 0x0148
    OFFSET_PROJECTION_MATRIX = 0x0814

    def __init__(self, address, process):
        self.address = address
        self.process = process

    def load(self):
        self.viewMatrix = Mat4(self.process.read_memory(self.address + self.OFFSET_VIEW_MATRIX, SIZE_MAT4))
        self.projectionMatrix = Mat4(self.process.read_memory(self.address + self.OFFSET_PROJECTION_MATRIX, SIZE_MAT4))

class Npc:

    OFFSET_TRANSFORM = 0x003C
    OFFSET_OBJECT_NAME = 0x0010
    OFFSET_NAME = 0x0124

    def __init__(self, address, process):
        self.address = address
        self.process = process

    def load(self):
        zstrptr_packed = self.process.read_memory(self.address + self.OFFSET_OBJECT_NAME + 0x08, 2 * SIZE_POINTER)
        ( strprt, strlen ) = struct.unpack("@Ii", zstrptr_packed)
        self.position = Mat4(self.process.read_memory(self.address + self.OFFSET_TRANSFORM, SIZE_MAT4))
        self.objectName = self.process.read_memory(strprt, strlen).decode("ascii")
        zstrptr_packed = self.process.read_memory(self.address + self.OFFSET_NAME + 0x08, 2 * SIZE_POINTER)
        (  strprt, strlen ) = struct.unpack("@Ii", zstrptr_packed)
        self.name = self.process.read_memory(strprt, strlen).decode("ascii")

class Mat4:
    def __init__(self, binary):

        (self.m11,
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
        self.m44) = struct.unpack("@ffffffffffffffff", binary)
    
    def get_coordinates(self):
        return (self.m14, self.m24, self.m34, self.m44)

    def as_list(self):
        return [[self.m11, self.m12, self.m13, self.m14],
                [self.m21, self.m22, self.m23, self.m24],
                [self.m31, self.m32, self.m33, self.m34], 
                [self.m41, self.m42, self.m43, self.m44]]

    def npmatrix(self):
        return np.mat(self.as_list())



def followList(address, process):
    next = address
    while next != 0:
        if next == 0x2C369620:
            print("ROOT")
        memory_packed = process.read_memory(next + 0x04, 0x08)
        address, next = struct.unpack("@II", memory_packed)
        yield address


def distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2) + math.pow(z1 - z2, 2))

def getHero(process):
    baseAddress = process.follow_pointer_path(NPC_LIST_PATH)
    for address in followList(baseAddress, process):
        if address != 0:
            npc = Npc(address, process)
            npc.load()
            if npc.objectName == HERO_OBJECT_NAME:
                return npc

zTVobType = {	
	0: "VOB_TYPE_VOB",
	1: "VOB_TYPE_LIGHT",
	2: "VOB_TYPE_SOUND",
	6: "VOB_TYPE_STARTPOINT",
	7: "VOB_TYPE_WAYPOINT",
	128: "VOB_TYPE_MOB",
	129: "VOB_TYPE_ITEM",
	130: "VOB_TYPE_NPC"
}

def getVobs(process, hero):
    baseAddress = process.follow_pointer_path(WORLD_OBJECT_LIST_PATH)
    items = []
    hx, hy, hz, gw = hero.position.get_coordinates()
    for address in followList(baseAddress, process):
        if address == 0:
            continue
        (type,) = struct.unpack("@I", process.read_memory(address + 0x00B0, 0x04))
        if type == 129:
            vob = Item(address, process)
        elif type == 128:
            vob = WorldObject(address, process)
        elif type == 130:
            vob = Npc(address, process)
        else:
            continue
        vob.load()
        ix, iy, iz, iw = vob.position.get_coordinates()
        if (abs(ix) < 0.00001 and abs(iy) < 0.00001 and abs(iz) < 0.00001):
            continue
        items.append((distance(hx, hy, hz, ix, iy, iz), vob))
    
    return list(sorted(items, key=lambda i: i[0]))

class ProcessingThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(object)
    period = 1.0/30.0

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.process = process

    def run(self):

        hero = getHero(self.process)
        while True:
            hero.load()

            vobs = getVobs(self.process, hero)
            toSend = []
            for distance, object in vobs[:10]:
                toSend.append((object.position, f"W{object.name}"))
            self.trigger.emit(toSend)
