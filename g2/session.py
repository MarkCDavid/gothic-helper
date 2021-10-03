from g2.camera import Camera, CameraField
from g2.memory.objects import Object, ObjectField, PointerField


class Session(Object):
    def __init__(self, process, address, size=0x0020):
        super().__init__(process, address, size)
        self.camera: "Camera" = CameraField(self, 0x000C, "camera")


class SessionField(PointerField):
    def __init__(self, parent, offset, name):
        super().__init__(parent, offset, name)

    def create_object(self):
        return Session(self.parent.process, self.address)
