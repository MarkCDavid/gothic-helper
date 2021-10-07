import math
import heapq
import numpy as np
from PyQt5 import QtCore
from dataclasses import dataclass, field
from processing.predicate import build_default_ignore_predicate, build_item_ignore_predicate
from processing.types import Npc, Vob, Camera
from processing.vobfetcher import ItemFetcher, MobFetcher, NpcFetcher
from pointer_paths import ITEM_LIST_PATH, NPC_LIST_PATH, VOB_LIST_PATH, CAMERA_PATH

@dataclass(order=True)
class VobMetaData:
    distance: int
    vob: Vob = field(compare=False)


class ProcessingThread(QtCore.QThread):

    EPSILON = 0.0001
    trigger = QtCore.pyqtSignal(object)

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.process = process

        vobListAddress = self.process.follow_pointer_path(VOB_LIST_PATH)
        itemListAddress = self.process.follow_pointer_path(ITEM_LIST_PATH)
        npcListAddress = self.process.follow_pointer_path(NPC_LIST_PATH)

        self.mobFetcher = MobFetcher(self.process, vobListAddress, 120, 3600)
        self.itemFetcher = ItemFetcher(self.process, itemListAddress, 30, 5)
        self.npcFetcher = NpcFetcher(self.process, npcListAddress, 30, 0.033)

        self.defaultIgnorePredicate = build_default_ignore_predicate()
        self.itemIgnorePredicate = build_item_ignore_predicate(self.npcFetcher)

    def run(self):
        hero = self.npcFetcher.fetchHero()

        while True:
            vobs = []
            vobs.extend(self._getClosestVobs(self.npcFetcher, hero, 20, self.defaultIgnorePredicate))
            vobs.extend(self._getClosestVobs(self.itemFetcher, hero, 30, self.itemIgnorePredicate))
            vobs.extend(self._getClosestVobs(self.mobFetcher, hero, 10, self.defaultIgnorePredicate))
            self.trigger.emit(vobs)

    def _getClosestVobs(self, vobFetcher, hero, count, ignorePredicate):
        vobFetcher.load()

        vobsHeap = []
        for vob in vobFetcher.getVobs():
            if ignorePredicate(vob, hero):
                continue
            heapq.heappush(vobsHeap, self._getVobDistance(vob, hero))

        vobs = []
        while vobsHeap and count > 0:
            count -= 1
            vobs.append(heapq.heappop(vobsHeap))
        return vobs

    def _getVobDistance(self, vob: Vob, hero: Npc):
        hx, hy, hz, _ = hero.transform.get_coordinates()
        ix, iy, iz, _ = vob.transform.get_coordinates()
        if abs(ix) < self.EPSILON and abs(iy) < self.EPSILON and abs(iz) < self.EPSILON:
            return VobMetaData(math.inf, vob)
        return VobMetaData(self._sqDistance(hx, hy, hz, ix, iy, iz), vob)

    def _sqDistance(self, x1, y1, z1, x2, y2, z2):
        x = x1 - x2
        y = y1 - y2
        z = z1 - z2
        return x * x + y * y + z * z


class RepaintThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(object)

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.process = process

    def run(self):
        address = self.process.follow_pointer_path(CAMERA_PATH)
        camera = Camera(self.process, address)
        while True:
            camera.load()
            viewProjectionMatrix = np.matmul(camera.projectionMatrix.npmatrix(), camera.viewMatrix.npmatrix())
            self.trigger.emit(viewProjectionMatrix)
