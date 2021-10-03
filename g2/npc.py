from g2.base import Int32Field
from g2.mat4 import Mat4, Mat4Field
from g2.memory.objects import Object, PointerField
from g2.memory.objectSize import SIZE_NPC
from g2.zstring import zStringField


class Npc(Object):
    def __init__(self, process, address, size=SIZE_NPC):
        super().__init__(process, address, size)
        
        self.transform: Mat4 = Mat4Field(self, 0x003C, "transform")
        self.homeWorld: int = Int32Field(self, 0x00B8, "homeWorld")

        self.objectName = zStringField(self, 0x0010, "objectName")
        self.name = zStringField(self, 0x0124, "name")


class NpcField(PointerField):
    def create_object(self):
        return Npc(self.parent.process, self.address)
