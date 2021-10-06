from ctypes import windll
from process.process import Process

import numpy as np
import win32gui
import sys


from PyQt5 import QtGui, QtCore, uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication

from process.process_constants import USER32
from processing.threads import ProcessingThread, RepaintThread
from processing.types import VOB_TYPE_ITEM, VOB_TYPE_MOB, VOB_TYPE_NPC


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

clrs = { VOB_TYPE_MOB: Qt.green, VOB_TYPE_ITEM: Qt.red, VOB_TYPE_NPC: Qt.yellow}

class MainWindow(QMainWindow):
    def __init__(self, g2, x, y, w, h):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint
        )
        self.setGeometry(x, y, w, h)
        self.vobs = []
        self.repaint_thread = RepaintThread(g2)
        self.repaint_thread.trigger.connect(self.repaint)
        self.repaint_thread.start()
        self.processing_thread = ProcessingThread(g2)
        self.processing_thread.trigger.connect(self.after_processing)
        self.processing_thread.start()

    def repaint(self, data):
        self.viewProjectionMatrix = data 
        self.update()

    def after_processing(self, vobs):
        self.vobs = vobs

    def paintEvent(self, event):
        painter = QPainter(self)
        for vobd in self.vobs:
            position, name, type = vobd.vob.transform, vobd.vob.getName(), vobd.vob.vobType
            x, y, visible = world_to_screen_space3(position.npmatrix(), self.viewProjectionMatrix, 800, 600)
            if visible:
                color = clrs[type]
                painter.setPen(QPen(color, 2, Qt.DashLine))
                painter.drawEllipse(int(x + 10), int(y + 35), 2, 2)
                painter.drawText(int(x) - 50,  int(y) - 20, 100, 20, 0, f"<{name}>")
   
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