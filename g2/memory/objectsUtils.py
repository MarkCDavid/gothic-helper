from g2.sortList import SortList
from g2.zstring import zString


def zstring_value(zstring: zString):
    if zstring is None or zstring.stringPointer is None or zstring.stringPointer.string is None:
        return ""

    return zstring.stringPointer.string

def sortList_iterator(sortList: SortList):
    while sortList is not None:
        if sortList.data is not None:
            yield sortList.data
        sortList = sortList.next