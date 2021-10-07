from collections import defaultdict, namedtuple
from ctypes import windll
from typing import List
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
from processing.threads import ProcessingThread, RepaintThread, VobMetaData
from processing.types import VOB_TYPE_ITEM, VOB_TYPE_MOB, VOB_TYPE_NPC
import widget
from window import Window, WindowInfo

class OverlayWindow(QMainWindow):
    def __init__(self, process: Process, windowInfo: WindowInfo):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setGeometry(windowInfo.x, windowInfo.y, windowInfo.width, windowInfo.height)
        self.windowInfo: WindowInfo = windowInfo
        self.vobs : List[VobMetaData] = []
        self.vobWidgets = widget.WidgetCollection({ VOB_TYPE_MOB: widget.MobWidget(), VOB_TYPE_ITEM: widget.ItemWidget(), VOB_TYPE_NPC: widget.NpcWidget() })
        self.repaint_thread = RepaintThread(process)
        self.repaint_thread.trigger.connect(self.repaint)
        self.repaint_thread.start()
        self.processing_thread = ProcessingThread(process)
        self.processing_thread.trigger.connect(self.after_processing)
        self.processing_thread.start()

    def repaint(self, data):
        self.viewProjectionMatrix = data 
        self.update()

    def after_processing(self, vobs: List[VobMetaData]):
        self.vobs = vobs

    def paintEvent(self, event):
        painter = QPainter(self)
        for vobMetaData in self.vobs:
            x, y, visible = self._world_to_screen_space(vobMetaData.vob.transform.npmatrix())
            widget = self.vobWidgets.get(vobMetaData.vob.vobType)
            if visible:
                widget.paint(painter, x, y, vobMetaData)

    def _world_to_screen_space(self, worldMatrix):
        screenSpaceMatrix = np.matmul(self.viewProjectionMatrix, worldMatrix)
        x, y, z, w = screenSpaceMatrix[0, 3], screenSpaceMatrix[1, 3], screenSpaceMatrix[2, 3], screenSpaceMatrix[3, 3]
        xp, yp = x / z, y / z
        x = ((xp + 1) / 2) * self.windowInfo.width
        y = ((1 - yp) / 2) * self.windowInfo.height
        return (int(x), int(y), w < 0)

   
if __name__ == '__main__':
    with Process("Gothic2.exe") as process:
        window = Window(process)
        window.findWindow()

        overlayApplication = QApplication(sys.argv)
        overlayWindow = OverlayWindow(process, window.windowInfo())
        overlayWindow.show()
        overlayApplication.exec()