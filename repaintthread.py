from time import sleep
from PyQt5 import QtCore
import numpy as np

from pointer_paths import CAMERA_PATH
from processingthread import Camera

class RepaintThread(QtCore.QThread):
    trigger = QtCore.pyqtSignal(object)

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.process = process

    def run(self):
        camera_pointer = self.process.follow_pointer_path(CAMERA_PATH)
        camera = Camera(camera_pointer, self.process)
        while True:
            camera.load()
            viewProjectionMatrix = np.matmul(camera.projectionMatrix.npmatrix(), camera.viewMatrix.npmatrix())
            self.trigger.emit(viewProjectionMatrix)