# from PyQt5 import QtCore

# from pointer_paths import ITEM_LIST_PATH
# from processing.procedures import getHero, getVobs
# import time

# class ItemThread(QtCore.QThread):
#     trigger = QtCore.pyqtSignal(str, object)
#     period = 10.0

#     def __init__(self, process):
#         QtCore.QThread.__init__(self)
#         self.process = process

#     def run(self):
#         npcListAddress = self.process.follow_pointer_path(ITEM_LIST_PATH)
#         hero = getHero(self.process)
#         while True:
#             time.sleep(self.period)
#             hero.load()
#             vobs = getVobs(npcListAddress, self.process, hero)
#             toSend = []
#             for distance, object in vobs[:10]:
#                 toSend.append((object.position, f"N{object.name}"))
#             self.trigger.emit("item", toSend)
