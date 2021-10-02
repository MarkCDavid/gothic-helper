from ctypes import byref, c_byte, c_char, c_double, c_float, c_int32, c_size_t, c_uint32, sizeof
from process.process_utils import get_process_info_by_name, create_buffer
from process.process_constants import KERNEL32, PROCESS_ALL_ACCESS
import traceback as tb
import struct

class Process:
    def __init__(self, processName) -> None:
        self.processName = processName
        (self.pid, self.baseAddress, _) = get_process_info_by_name(processName)    
        if self.pid is None:
            raise Exception(f"Could not find the process with the name {processName} running. Are you sure it is running?")
        self._handle = None

    def read_memory(self, address, size):
        buffer, bufferSize = create_buffer(c_byte, size)
        bytesRead = c_size_t()
        
        success = KERNEL32.ReadProcessMemory(self._handle, address, buffer, bufferSize, byref(bytesRead))
        return bytes(buffer) if success else bytes()

    def read_uint32(self, address):
        value_packed = self.read_memory(address, sizeof(c_uint32))
        (value,) = struct.unpack("@I", value_packed)
        return value
    
    def read_int32(self, address):
        value_packed = self.read_memory(address, sizeof(c_int32))
        (value,) = struct.unpack("@i", value_packed)
        return value

    def read_float(self, address):
        value_packed = self.read_memory(address, sizeof(c_float))
        (value,) = struct.unpack("@f", value_packed)
        return value

    def read_double(self, address):
        value_packed = self.read_memory(address, sizeof(c_double))
        (value,) = struct.unpack("@d", value_packed)
        return value

    def read_zstring(self, address):
        string_pointer = self.read_uint32(address)
        string_size = self.read_int32(address + sizeof(c_uint32))
        string_data = self.read_memory(string_pointer, sizeof(c_char) * string_size)
        return string_data.decode("ascii")

    def follow_pointer_path(self, pointer_path):
        address = self.baseAddress
        for offset in pointer_path:
            address += offset
            address = self.read_uint32(address)
        return address
    
    def __enter__(self):
        self._handle = KERNEL32.OpenProcess(PROCESS_ALL_ACCESS, False, self.pid)
        if self._handle == 0:
            raise Exception(f"Could not open a handle to the process with the name {self.processName}.")
        return self

    def __exit__(self, type, value, traceback):
        if traceback is not None:
            tb.print_tb(traceback)
            return False
        if self._handle != 0: 
            KERNEL32.CloseHandle(self._handle)
        return True
