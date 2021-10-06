from ctypes import windll
from process.process import Process
import multiprocessing
import struct
from g2.memory.objectsUtils import sortList_iterator, zstring_value
from g2.memory.resolver import Resolver
from g2.npc import Npc
from g2.world import World

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
from processing.npcthread import NpcThread
# from processing.itemthread import ItemThread
# from processing.mobthread import MobThread
from processing.repaintthread import RepaintThread


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


def world_to_screen_space3(worldMatrix, viewProjectionMatrix, width, height):
    screenSpaceMatrix = np.matmul(viewProjectionMatrix, worldMatrix)
    x, y, z, w = screenSpaceMatrix[0, 3], screenSpaceMatrix[1, 3], screenSpaceMatrix[2, 3], screenSpaceMatrix[3, 3]
    xp, yp = x / z, y / z
    x = ((xp + 1) / 2) * width
    y = ((1 - yp) / 2) * height
    return (int(x), int(y), w < 0)

clrs = { "I": Qt.green, "N": Qt.red, "W": Qt.yellow}

class MainWindow(QMainWindow):
    def __init__(self, g2, x, y, w, h):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )
        self.setGeometry(x, y, w, h)
        self.data = {}
        self.repaint_thread = RepaintThread(g2)
        self.repaint_thread.trigger.connect(self.repaint)
        self.repaint_thread.start()
        self.npc_thread = NpcThread(g2)
        self.npc_thread.trigger.connect(self.after_processing)
        self.npc_thread.start()
        # self.item_thread = ItemThread(g2)
        # self.item_thread.trigger.connect(self.after_processing)
        # self.item_thread.start()
        # self.mob_thread = MobThread(g2)
        # self.mob_thread.trigger.connect(self.after_processing)
        # self.mob_thread.start()

    def repaint(self, data):
        self.viewProjectionMatrix = data 
        self.update()

    def after_processing(self, key, value):
        self.data[key] = value

    def paintEvent(self, event):
        painter = QPainter(self)
        for key in self.data:
            for item in self.data[key]:
                position, name = item 
                x, y, visible = world_to_screen_space3(position.npmatrix(), self.viewProjectionMatrix, 800, 600)
                if visible:
                    color = clrs[name[0]]
                    painter.setPen(QPen(color, 2, Qt.DashLine))
                    painter.drawEllipse(int(x), int(y), 2, 2)
                    painter.drawText(int(x) - 50,  int(y) - 20, 100, 20, 0, f"<{name[1:]}>")

   
if __name__ == '__main__':
    with Process("Gothic2.exe") as g2:
        def window_enumeration_handler(window_handle, top_windows):
            rect = win32gui.GetWindowRect(window_handle)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            top_windows.append((window_handle, win32gui.GetWindowText(window_handle), (x, y, w, h)))


        top_windows = []
        win32gui.EnumWindows(window_enumeration_handler, top_windows)
        window = None
        handle = None
        for w in top_windows:
            if "Gothic II" in w[1]: 
                window = w
                break
    
        x, y, w, h = window[2]
        app = QApplication(sys.argv)
        mywindow = MainWindow(g2, x, y, w, h)
        mywindow.show()
        app.exec()