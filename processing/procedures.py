import math
import struct

from pointer_paths import NPC_LIST_PATH
from processing.types import Item, Npc, Vob

HERO_OBJECT_NAME = "PC_HERO"

def followList(address, process):
    next = address
    while next != 0:
        memory_packed = process.read_memory(next + 0x04, 0x08)
        address, next = struct.unpack("@II", memory_packed)
        yield address


def distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt(sqDistance(x1, y1, z1, x2, y2, z2))

def sqDistance(x1, y1, z1, x2, y2, z2):
    x = x1 - x2
    y = y1 - y2
    z = z1 - z2
    return x * x + y * y + z * z

def getHero(process):
    baseAddress = process.follow_pointer_path(NPC_LIST_PATH)
    for address in followList(baseAddress, process):
        if address != 0:
            npc = Npc(process, address)
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

def getVobs(baseAddress, process, hero):
    
    items = []
    hx, hy, hz, gw = hero.position.get_coordinates()
    for address in followList(baseAddress, process):
        if address == 0:
            continue
        (type,) = struct.unpack("@I", process.read_memory(address + 0x00B0, 0x04))
        if type == 129:
            vob = Item(process, address)
        elif type == 128:
            vob = Vob(process, address)
        elif type == 130:
            vob = Npc(process, address)
        else:
            continue
        vob.load()
        ix, iy, iz, iw = vob.position.get_coordinates()
        if (abs(ix) < 0.00001 and abs(iy) < 0.00001 and abs(iz) < 0.00001):
            continue
        items.append((sqDistance(hx, hy, hz, ix, iy, iz), vob))
    
    return list(sorted(items, key=lambda i: i[0]))

epsilon = 0.0001
def getVobDistance(vob: Vob, hero: Npc):
    hx, hy, hz, _ = hero.transform.get_coordinates()
    ix, iy, iz, _ = vob.transform.get_coordinates()
    if (abs(ix) < epsilon and abs(iy) < epsilon and abs(iz) < epsilon):
        return (math.inf, vob)
    return (sqDistance(hx, hy, hz, ix, iy, iz), vob)
    