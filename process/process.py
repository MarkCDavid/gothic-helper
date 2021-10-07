from ctypes import byref, c_size_t
from process.buffer import Buffer
from process.process_info import ProcessInfoFetcher
from process.process_constants import KERNEL32, PROCESS_ALL_ACCESS
import traceback as tb
import struct
from multiprocessing import Lock

from process.sizes import SIZE_BYTE, SIZE_UINT32

class Process:
    def __init__(self, processName) -> None:
        self.lock = Lock()
        self.buffer = Buffer(Buffer.MB)
        self.processInfo = ProcessInfoFetcher().by_name(processName)  
        if self.processInfo.pid is None:
            raise Exception(f"Could not find the process with the name {processName} running. Are you sure it is running?")
        self._handle = None

    def read_memory(self, address, size):
        with self.lock:
            readBytes = c_size_t()
            bufferPointer, bufferSize = self.buffer.allocate(SIZE_BYTE * size)
            success = KERNEL32.ReadProcessMemory(self._handle, address, bufferPointer, bufferSize, byref(readBytes))
            if not success:
                print(f"address: {hex(address)} size: {bufferSize} read: {readBytes.value}")
                print(f"read_memory error: {KERNEL32.GetLastError()}")
            return self.buffer.read(0, size) if success else bytes()

    def read(self, address, format, size):
        value_packed = self.read_memory(address, size)
        return struct.unpack(format, value_packed)

    def read_fd(self, address, fieldData):
        result = self.read(address + fieldData.offset, fieldData.format, fieldData.size)
        return result if len(result) > 1 else result[0]

    def follow_pointer_path(self, pointer_path):
        address = self.processInfo.baseAddress
        for offset in pointer_path:
            address += offset
            (address,) = self.read(address, "@I", SIZE_UINT32)
        return address
    
    def __enter__(self):
        self._handle = KERNEL32.OpenProcess(PROCESS_ALL_ACCESS, False, self.processInfo.pid)
        if self._handle == 0:
            raise Exception(f"Could not open a handle to the process with the name {self.processInfo.processName}.")
        return self

    def __exit__(self, type, value, traceback):
        if traceback is not None:
            tb.print_tb(traceback)
            return False
        if self._handle != 0: 
            KERNEL32.CloseHandle(self._handle)
        return True
