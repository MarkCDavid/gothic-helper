from ctypes import c_ubyte


class Buffer:

    KB = 1024
    MB = KB * KB

    def __init__(self, initialSize):
        self.bufferSize = initialSize
        self.buffer = self._construct(initialSize)

    def allocate(self, size):
        if size > self.bufferSize:
            self.buffer = self._construct(size)
            self.bufferSize = size
        return (self.buffer, size)

    def read(self, start, end):
        return bytes(self.buffer[start : end])


    def _construct(self, size):
        bufferType = c_ubyte * size
        return bufferType()
