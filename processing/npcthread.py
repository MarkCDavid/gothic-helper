from PyQt5 import QtCore

from pointer_paths import NPC_LIST_PATH
from processing.procedures import getHero, getVobDistance

from processing.vobfetcher import VobFetcher


class NpcThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(str, object)

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.process = process
        self.address = self.process.follow_pointer_path(NPC_LIST_PATH)
        self.fetcher = VobFetcher(self.process, self.address)

    def run(self):
        hero = getHero(self.process)

        while True:
            hero.load()
            self.fetcher.load()
            vobs = []
            for vob in self.fetcher.getVobs():
                vobs.append(getVobDistance(vob, hero))
            vobs.sort(key=lambda v: v[0])

            toSend = []
            for distance, vob in vobs[:20]:
                toSend.append((vob.transform, f"N{vob.name}"))
            self.trigger.emit("npc", toSend)
