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
from processingthread import ProcessingThread
from repaintthread import RepaintThread




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
    
    x = ((xp + 1) / 2) * width
    y = ((1 - yp) / 2) * height
    return (int(x), int(y), w < 0)


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
        self.data = []
        self.repaint_thread = RepaintThread(g2)
        self.repaint_thread.trigger.connect(self.repaint)
        self.repaint_thread.start()
        self.processing_thread = ProcessingThread(g2)
        self.processing_thread.trigger.connect(self.after_processing)
        self.processing_thread.start()

    def repaint(self, data):
        self.viewProjectionMatrix = data 
        self.update()

    def after_processing(self, data):
        self.data = data

    def paintEvent(self, event):
        painter = QPainter(self)
        for item in self.data:
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

        # item_pointers = []
        # item_list_address = g2.follow_pointer_path(ITEM_LIST_PATH)
            
            # dataAddress = None
            # next = item_list_address
            # while next != 0:
            #     memory = g2.read_memory(next, 0x0C)
            #     _, dataAddress, next = struct.unpack("@iii", memory)
            #     item_pointers.append(hex(dataAddress))
            
            # print(item_pointers[:10])
            # world_address = g2.follow_pointer_path(WORLD_PATH)
            # world = World(g2, world_address)
            # resolver = Resolver(g2, world)
            # i = 0
            # while i < 5:
            #     start = time.time_ns()
            #     resolver.resolve_root()
            #     i += 1
            #     end = time.time_ns()
            #     print((end - start) / (10**9))
