from g2.base import Int32Field
from g2.mat4 import Mat4Field
from g2.memory.objects import Object, ObjectField, PointerField
from g2.memory.objectSize import SIZE_ITEM
from g2.zstring import zStringField


class Item(Object):
    def __init__(self, process, address, size=SIZE_ITEM):
        super().__init__(process, address, size)
        
        self.transform = Mat4Field(self, 0x003C)
        self.homeWorld = Int32Field(self, 0x00B8)

        self.objectName = zStringField(self, 0x0010)
        self.name = zStringField(self, 0x0124)
        self.visual = zStringField(self, 0x0208)
        self.visualChange = zStringField(self, 0x0220)
        self.effect = zStringField(self, 0x0234)
        self.schemeName = zStringField(self, 0x024C)
        self.description = zStringField(self, 0x0274)
        
        self.text1 = zStringField(self, 0x0288)
        self.text2 = zStringField(self, 0x029C)
        self.text3 = zStringField(self, 0x02B0)
        self.text4 = zStringField(self, 0x02C4)
        self.text5 = zStringField(self, 0x02D8)
        self.text6 = zStringField(self, 0x02EC)

        self.count1 = Int32Field(self, 0x0300)
        self.count2 = Int32Field(self, 0x0304)
        self.count3 = Int32Field(self, 0x0308)
        self.count4 = Int32Field(self, 0x030C)
        self.count5 = Int32Field(self, 0x0310)
        self.count6 = Int32Field(self, 0x0314)


class ItemField(PointerField):
    def create_object(self):
        return Item(self.parent.process, self.address)
