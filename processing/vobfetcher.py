import struct

from time import time
from processing.types import Item, Npc, Vob


class VobFetcher:

    TRAVERSAL_INTERVAL = 60
    
    def __init__(self, process, address) -> None:
        self.process = process
        self.address = address
        self.vobs = {}
        self.lastTraversal = 0

    def getVobs(self):
        for address in self.vobs:
            yield self.vobs[address]

    def load(self):
        if self._traversalDelta() > self.TRAVERSAL_INTERVAL:
            self.traverse()

        for vob in self.getVobs():
            vob.load()
    
    def traverse(self):
        self.lastTraversal = time()
        for address in self._followList():
            if address != 0 and address not in self.vobs:
                (type,) = struct.unpack("@I", self.process.read_memory(address + 0x00B0, 0x04))
                vob = self._createVob(address, type)
                if vob is not None:
                    self.vobs[address] = vob

    def _followList(self):
        next = self.address
        while next != 0:
            memory_packed = self.process.read_memory(next + 0x04, 0x08)
            address, next = struct.unpack("@II", memory_packed)
            yield address

    def _createVob(self, address, type):
        if type == 129:
            return Item(self.process, address)
        elif type == 128:
            return Vob(self.process, address)
        elif type == 130:
            return Npc(self.process, address)
        else:
            return None

    def _traversalDelta(self):
        return time() - self.lastTraversal