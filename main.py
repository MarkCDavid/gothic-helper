from ctypes import windll
import struct
from g2.memory.objectsUtils import sortList_iterator, zstring_value
from g2.memory.resolver import Resolver
from g2.npc import Npc
from g2.world import World
from pointer_paths import ITEM_LIST_PATH
from process.process import Process
import numpy as np
import time
import math
import win32gui
import sys

import threading

from PyQt5 import QtGui, QtCore, uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication

from process.process_constants import USER32 

HERO_OBJECT_NAME = "PC_HERO"

def distance(x1, y1, z1, x2, y2, z2):
    return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2) + math.pow(z1 - z2, 2))

def get_hero(world: World) -> "Npc":
    for npc in sortList_iterator(world.npcList):
        if zstring_value(npc.objectName) == HERO_OBJECT_NAME:
            return npc
    return None
    
def get_items(hero: Npc, world: World) -> "Npc":
    items = []
    hx, hy, hz, xq = hero.transform.get_coordinates()
    for item in sortList_iterator(world.itemList):
        ix, iy, iz, iq = item.transform.get_coordinates()
        if abs(ix) < 0.00001 and abs(iy) < 0.00001 and abs(iz) < 0.00001:
            continue
        items.append((distance(hx, hy, hz, ix, iy, iz), item))
    
    return list(sorted(items, key=lambda i: i[0]))

def world_to_screen_space2(world_matrix, view_matrix, projection_matrix, width, height):
    p = np.array([0, 0, 0, 1])
    world_matrix = np.mat(world_matrix.as_list())
    view_matrix = np.mat(view_matrix.as_list())
    projection_matrix = np.mat(projection_matrix.as_list())

    p = np.squeeze(np.asarray(np.dot(world_matrix, p)))
    p = np.squeeze(np.asarray(np.dot(view_matrix, p)))
    p = np.squeeze(np.asarray(np.dot(projection_matrix, p)))
    x, y, z, w = p[0], p[1], p[2], p[3]

    xp, yp = x / z, y / z
    
    # p2 = np.matmul(projection_matrix, np.matmul(view_matrix, world_matrix))
    # print(p2)
    
    x = ((xp + 1) / 2) * width
    y = ((1 - yp) / 2) * height
    return (int(x), int(y), w < 0)

def find_window(parent, names):
    if not names:
        return parent
    name = names[0]
    child = 0
    while True:
        child = USER32.FindWindowExW(parent, child, name, 0)
        if not child:
            return 0
        result = find_window(child, names[1:])
        if result:
            return result

class MainWindow(QMainWindow):
    def __init__(self, g2, x, y, w, h):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )
        self.setGeometry(x, y, w, h)
        self.x = 0
        self.y = 0
        self.name = "<>"
        self.visible = False
        self.processThread = G2ProcessThread(g2)
        self.processThread.processing_finished.connect(self.draw)
        self.processThread.start()

    def draw(self, data):
        x, y, visible, name = data.split('|')
        self.x, self.y, self.visible, self.name = float(x), float(y), bool(int(visible)), str(name)
        self.update()
      

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.visible:
            painter.setPen(QPen(Qt.green, 2, Qt.DashLine))
            painter.drawEllipse(int(self.x), int(self.y), 4, 4)
            painter.drawText(int(self.x) - 50,  int(self.y) - 20, 100, 20, 0, f"<{self.name}>")

    def mousePressEvent(self, event):
        QtWidgets.qApp.quit()
    


class G2ProcessThread(QtCore.QThread):

    processing_finished = QtCore.pyqtSignal(object)
    def __init__(self, g2):
        QtCore.QThread.__init__(self)
        self.g2 = g2

    def run(self):
        world_address = self.g2.follow_pointer_path([0x393240, 0x80, 0xB8, 0x10, 0xB8])
        world = World(self.g2, world_address)

        start = time.time_ns()

        resolver = Resolver(self.g2, world)
        resolver.resolve_root()

        end = time.time_ns()
        duration = end - start
        print(f"Resolving took: {duration/1000000000}s")

        hero = get_hero(world)
        camera = world.session.camera

        while True:

            closest_items = get_items(hero, world)
    #     print('\n\n\n\n\n\n\n\n')
    #     for closest_item in closest_items[:10]:
    #         dst, item = closest_item
    #         print(f"Distance: {dst} - {zstring_value(item.description)}")
    #         resolver.resolve(item)


    #     resolver.resolve(hero)
    #     time.sleep(1)
            closest_item = closest_items[0][1]
            ss = world_to_screen_space2(closest_item.transform, camera.viewMatrix, camera.projectionMatrix, 800, 600)
            x, y, visible = ss
            resolver.resolve(hero)
            resolver.resolve(camera)
            resolver.resolve(world.itemList)


            self.processing_finished.emit("%i|%i|%i|%s" % (x, y, 1 if visible else 0, zstring_value(closest_item.description)))
            time.sleep(0.01)


with Process("Gothic2.exe") as g2:

    # def window_enumeration_handler(window_handle, top_windows):
    #     rect = win32gui.GetWindowRect(window_handle)
    #     x = rect[0]
    #     y = rect[1]
    #     w = rect[2] - x
    #     h = rect[3] - y
    #     top_windows.append((window_handle, win32gui.GetWindowText(window_handle), (x, y, w, h)))


    # top_windows = []
    # win32gui.EnumWindows(window_enumeration_handler, top_windows)
    # window = None
    # handle = None
    # for w in top_windows:
    #     if "Gothic II" in w[1]: 
    #         window = w
    #         break
    
    # x, y, w, h = window[2]
    # app = QApplication(sys.argv)
    # mywindow = MainWindow(g2, x, y, w, h)
    # mywindow.show()
    # app.exec()

    item_pointers = []
    item_list_address = g2.follow_pointer_path(ITEM_LIST_PATH)
    
    dataAddress = None
    next = item_list_address
    while next != 0:
        memory = g2.read_memory(next, 0x0C)
        _, dataAddress, next = struct.unpack("@iii", memory)
        item_pointers.append(hex(dataAddress))
    
    print(item_pointers[:10])

    # world = World(g2, world_address)
    # resolver = Resolver(g2, world)
    # i = 0
    # while i < 5:
    #     resolver.resolve_root()
    #     i += 1


   