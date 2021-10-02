from g2.G2MemoryObject import G2MemoryObject
from handlers.base_handlers import default_handler, int32_handler, string_handler, uint32_handler

class Item(G2MemoryObject):
    def __init__(self, process, address):
        super().__init__(process, address)
        self.fields = {
            "name": (0x012C, string_handler),
            "visual": (0x0214, string_handler),
            "visualChange": (0x0228, string_handler),
            "effect": (0x023C, string_handler),
            "schemeName": (0x0254, string_handler),
            "description": (0x027C, string_handler),
            "text1": (0x0290, string_handler),
            "text2": (0x02A4, string_handler),
            "text3": (0x02B8, string_handler),
            "text4": (0x02CC, string_handler),
            "text5": (0x02E0, string_handler),
            "text6": (0x02F4, string_handler),
            "count1": (0x0300, int32_handler),
            "count2": (0x0304, int32_handler),
            "count3": (0x0308, int32_handler),
            "count4": (0x030C, int32_handler),
            "count5": (0x0310, int32_handler),
            "count6": (0x0314, int32_handler),
        }
