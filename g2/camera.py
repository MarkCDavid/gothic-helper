from g2.mat4 import Mat4Field
from g2.memory.objects import Object, PointerField


class Camera(Object):
    def __init__(self, process, address, size=0x0A00):
        super().__init__(process, address, size)

        self.viewMatrix = Mat4Field(self, 0x0148, "viewMatrix")
        self.projectionMatrix = Mat4Field(self, 0x0814, "projectionMatrix")


class CameraField(PointerField):
    def __init__(self, parent, offset, name):
        super().__init__(parent, offset, name)

    def create_object(self):
        return Camera(self.parent.process, self.address)
