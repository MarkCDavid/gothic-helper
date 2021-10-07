from collections import defaultdict
import math
from PyQt5 import QtGui, QtCore, uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QBrush, QPen
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication
import numpy as np
from processing.threads import VobMetaData

from processing.types import Vob

class WidgetCollection:
    def __init__(self, initialCollection):
        self._defaultWidget = Widget()
        self._collection = defaultdict(lambda: self._defaultWidget)
        for key in initialCollection:
            self._collection[key] = initialCollection[key]

    def get(self, key):
        return self._collection[key]

class Widget:

    def __init__(self) -> None:
        self.font = self._font(9)
        self.color = Qt.white
        self.width = 2
        self.size = 2
        self.halfSize = self.size // 2
       

    def paint(self, painter: QPainter, x: int, y: int, vobMetaData: VobMetaData):
        painter.setPen(QPen(self.color, self.width, Qt.SolidLine))
        painter.drawEllipse(x - self.halfSize, y - self.halfSize, self.size, self.size)

    def _text_size(self, painter: QPainter, text: str):
        fontMetrics = QFontMetrics(painter.font())
        return fontMetrics.width(text, len(text)), fontMetrics.height()

    @staticmethod
    def _font(size: int):
        font = QFont()
        font.setPointSize(size)
        return font


class MobWidget(Widget):

    def __init__(self) -> None:
        super().__init__()
        self.color = Qt.green

class ItemWidget(Widget):

    def __init__(self) -> None:
        super().__init__()
        self.color = Qt.red
        self.closeDistance = 6250000.0
        self.farDistnace = 100000000.0
        self.farFont = self._font(6)
        self.closeFont = self._font(9)
 
    def paint(self, painter: QPainter, x: int, y: int, vobMetaData: VobMetaData):
        painter.setPen(QPen(self.color, 2, Qt.SolidLine))
        painter.drawEllipse(x - self.halfSize, y - self.halfSize, self.size, self.size)

        distance = vobMetaData.distance
        if self._should_draw_name(distance):
            name = f"<{vobMetaData.vob.getName()}> ({math.sqrt(vobMetaData.distance):.2f})"
            painter.setFont(self._scaled_font(distance))
            width, height = self._text_size(painter, name)
            painter.drawText(x - width // 2, y - height - height // 2 , width, height, 0, name)

    def _should_draw_name(self, distance):
        return distance < self.farDistnace

    def _scaled_font(self, distance):
        return self.farFont if distance > self.closeDistance else self.closeFont
        

class NpcWidget(Widget):

    def __init__(self) -> None:
        super().__init__()
        self.color = Qt.yellow
        self.closeDistance = 6250000.0
        self.farDistnace = 100000000.0
        self.farFont = self._font(6)
        self.closeFont = self._font(9)
 
    def paint(self, painter: QPainter, x: int, y: int, vobMetaData: VobMetaData):
        painter.setPen(QPen(self.color, 2, Qt.SolidLine))
        painter.drawEllipse(x - self.halfSize, y - self.halfSize, self.size, self.size)

        distance = vobMetaData.distance
        if self._should_draw_name(distance):
            name = vobMetaData.vob.getName()
            painter.setFont(self._scaled_font(distance))
            width, height = self._text_size(painter, name)
            painter.drawText(x - width // 2, y - height - height // 2 , width, height, 0, name)

    def _should_draw_name(self, distance):
        return distance < self.farDistnace

    def _scaled_font(self, distance):
        return self.farFont if distance > self.closeDistance else self.closeFont
