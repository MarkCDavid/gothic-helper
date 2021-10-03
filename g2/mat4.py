from g2.base import FloatField
from g2.memory.objects import InlineObjectField, Object, PointerField
from g2.memory.objectSize import SIZE_MAT4

class Mat4(Object):
    def __init__(self, process, address, size=SIZE_MAT4):
        super().__init__(process, address, size)

        self.m11 = FloatField(self, 0x0000)
        self.m12 = FloatField(self, 0x0004)
        self.m13 = FloatField(self, 0x0008)
        self.m14 = FloatField(self, 0x000C)
        self.m21 = FloatField(self, 0x0010)
        self.m22 = FloatField(self, 0x0014)
        self.m23 = FloatField(self, 0x0018)
        self.m24 = FloatField(self, 0x001C)
        self.m31 = FloatField(self, 0x0020)
        self.m32 = FloatField(self, 0x0024)
        self.m33 = FloatField(self, 0x0028)
        self.m34 = FloatField(self, 0x002C)
        self.m41 = FloatField(self, 0x0030)
        self.m42 = FloatField(self, 0x0034)
        self.m43 = FloatField(self, 0x0038)
        self.m44 = FloatField(self, 0x003C)
    
    def get_coordinates(self):
        return (self.m14, self.m24, self.m34)
        
class Mat4Field(InlineObjectField):
    def __init__(self, parent, offset):
        super().__init__(parent, offset)

    def load_blob(self,):
        blob_slice = slice(self.offset, self.offset + SIZE_MAT4)
        self.object.blob = self.parent.blob[blob_slice]
    
    def create_object(self):
        return Mat4(self.parent.process, self.parent.address)


class Mat4PointerField(PointerField):
    def __init__(self, parent, offset):
        super().__init__(parent, offset)

    def create_object(self):
        return Mat4(self.parent.process, self.address)