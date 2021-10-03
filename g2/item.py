from g2.base import Int32Field
from g2.mat4 import Mat4Field
from g2.memory.objects import Object, ObjectField, PointerField
from g2.memory.objectSize import SIZE_ITEM
from g2.zstring import zStringField


class Item(Object):
    def __init__(self, process, address, size=SIZE_ITEM):
        super().__init__(process, address, size)
        
        self.transform = Mat4Field(self, 0x003C, "transform")
        self.homeWorld = Int32Field(self, 0x00B8, "homeWorld")

        self.objectName = zStringField(self, 0x0010, "objectName")
        self.name = zStringField(self, 0x0124, "name")
        self.visual = zStringField(self, 0x0208, "visual")
        self.visualChange = zStringField(self, 0x0220, "visualChange")
        self.effect = zStringField(self, 0x0234, "effect")
        self.schemeName = zStringField(self, 0x024C, "schemeName")
        self.description = zStringField(self, 0x0274, "description")
        
        self.text1 = zStringField(self, 0x0288, "text1")
        self.text2 = zStringField(self, 0x029C, "text2")
        self.text3 = zStringField(self, 0x02B0, "text3")
        self.text4 = zStringField(self, 0x02C4, "text4")
        self.text5 = zStringField(self, 0x02D8, "text5")
        self.text6 = zStringField(self, 0x02EC, "text6")

        self.count1 = Int32Field(self, 0x0300, "count1")
        self.count2 = Int32Field(self, 0x0304, "count2")
        self.count3 = Int32Field(self, 0x0308, "count3")
        self.count4 = Int32Field(self, 0x030C, "count4")
        self.count5 = Int32Field(self, 0x0310, "count5")
        self.count6 = Int32Field(self, 0x0314, "count6")


class ItemField(PointerField):
    def create_object(self):
        return Item(self.parent.process, self.address)
