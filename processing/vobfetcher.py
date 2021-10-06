import struct

from time import time
from processing.types import VOB_TYPE_ITEM, VOB_TYPE_MOB, VOB_TYPE_NPC, Item, Mob, Npc, Vob


class VobFetcher:
    def __init__(self, process, address, traversalInterval, loadInterval) -> None:
        self.process = process
        self.address = address

        self.traversalInterval = traversalInterval
        self.lastTraversal = 0

        self.loadInterval = loadInterval
        self.lastLoad = 0
        self.dirty = False

        self.vobsDict = {}
        self.vobs = []

    def getVobs(self):
        return self.vobs

    def needsLoading(self):
        return self._intervalDelta(self.lastLoad) > self.loadInterval

    def needsTraversal(self):
        return self._intervalDelta(self.lastTraversal) > self.traversalInterval

    def load(self):
        needsTraversal = self.needsTraversal()
        needsLoading = self.needsLoading()
        if needsTraversal:
            self._traverse()

        if (needsTraversal and self.dirty) or needsLoading:
            self._load()

    def _load(self):
        self.dirty = False
        self.lastLoad = time()
        for vob in self.getVobs():
            vob.load()

    def _traverse(self):
        self.lastTraversal = time()
        for address in self._followList():
            if address != 0 and address not in self.vobsDict:
                type = Vob.getVobType(self.process, address)
                vob = self._createVob(address, type)
                if vob is not None:
                    self.dirty = True
                    self.vobsDict[address] = vob
                    self.vobs.append(vob)

    def _followList(self):
        next = self.address
        while next != 0:
            memory_packed = self.process.read_memory(next + 0x04, 0x08)
            address, next = struct.unpack("@II", memory_packed)
            yield address

    def _createVob(self, address, type):
        if type == VOB_TYPE_ITEM:
            return Item(self.process, address)
        elif type == VOB_TYPE_MOB:
            return Mob(self.process, address)
        elif type == VOB_TYPE_NPC:
            return Npc(self.process, address)
        else:
            return None

    def _intervalDelta(self, interval):
        return time() - interval


class MobFetcher(VobFetcher):
    def _createVob(self, address, type):
        return Mob(self.process, address) if type == VOB_TYPE_MOB else None


class NpcFetcher(VobFetcher):

    HERO_OBJECT_NAME = "PC_HERO"

    def __init__(self, process, address, traversalInterval, loadInterval) -> None:
        super().__init__(process, address, traversalInterval, loadInterval)
        self.hero = None

    def _createVob(self, address, type):
        return Npc(self.process, address) if type == VOB_TYPE_NPC else None

    def fetchHero(self):
        if self.hero is None:
            self._traverse()
            self._load()
            for npc in self.vobs:
                if npc.objectName == NpcFetcher.HERO_OBJECT_NAME:
                    self.hero = npc

        return self.hero


class ItemFetcher(VobFetcher):
    def _createVob(self, address, type):
        return Item(self.process, address) if type == VOB_TYPE_ITEM else None
