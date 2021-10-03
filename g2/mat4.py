from g2.base import FloatField
from g2.memory.objects import InlineObjectField, Object, PointerField
from g2.memory.objectSize import SIZE_MAT4

class Mat4(Object):
    def __init__(self, process, address, size=SIZE_MAT4):
        super().__init__(process, address, size)

        self.m11 = FloatField(self, 0x0000, "m11")
        self.m12 = FloatField(self, 0x0004, "m12")
        self.m13 = FloatField(self, 0x0008, "m13")
        self.m14 = FloatField(self, 0x000C, "m14")
        self.m21 = FloatField(self, 0x0010, "m21")
        self.m22 = FloatField(self, 0x0014, "m22")
        self.m23 = FloatField(self, 0x0018, "m23")
        self.m24 = FloatField(self, 0x001C, "m24")
        self.m31 = FloatField(self, 0x0020, "m31")
        self.m32 = FloatField(self, 0x0024, "m32")
        self.m33 = FloatField(self, 0x0028, "m33")
        self.m34 = FloatField(self, 0x002C, "m34")
        self.m41 = FloatField(self, 0x0030, "m41")
        self.m42 = FloatField(self, 0x0034, "m42")
        self.m43 = FloatField(self, 0x0038, "m43")
        self.m44 = FloatField(self, 0x003C, "m44")
    
    def get_coordinates(self):
        return (self.m14, self.m24, self.m34, self.m44)

    def as_list(self):
        return [[self.m11, self.m12, self.m13, self.m14],
                [self.m21, self.m22, self.m23, self.m24],
                [self.m31, self.m32, self.m33, self.m34], 
                [self.m41, self.m42, self.m43, self.m44]]

    def __str__(self) -> str:
        return f"{self.m11} {self.m12} {self.m13} {self.m14}\n{self.m21} {self.m22} {self.m23} {self.m24}\n{self.m31} {self.m32} {self.m33} {self.m34}\n{self.m41} {self.m42} {self.m43} {self.m44}"
        
class Mat4Field(InlineObjectField):
    def __init__(self, parent, offset, name):
        super().__init__(parent, offset, name)

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