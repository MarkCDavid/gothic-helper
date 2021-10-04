from ctypes import c_uint32, byref
from collections import namedtuple
from process.buffer import Buffer
from process.process_handle import ProcessHandle
from process.process_constants import PSAPI, LIST_ALL_MODULES, PROCESS_QUERY_INFORMATION, PROCESS_VM_READ
import struct

from process.sizes import SIZE_CHAR, SIZE_PID, SIZE_POINTER

ProcessInfo = namedtuple("ProcessInfo", ["pid", "processName", "baseAddress"])


class ProcessInfoFetcher:
    def __init__(self) -> None:
        self.buffer = Buffer(Buffer.MB)

    def by_name(self, processName):
        for pid in self.get_current_processes():
            processInformation = self.get_process_information(pid)
            if processInformation is None:
                continue
            if processInformation.processName == processName:
                return processInformation
        return None

    def get_current_processes(self, count=512):
        processPids = []

        bufferPointer, bufferSize = self.buffer.allocate(SIZE_PID * count)
        readBytes = c_uint32()

        if not PSAPI.EnumProcesses(bufferPointer, bufferSize, byref(readBytes)):
            return processPids

        for step in range(0, readBytes.value, SIZE_PID):
            (pid,) = struct.unpack("@i", self.buffer.read(step, step + SIZE_PID))
            processPids.append(pid)

        return processPids

    def get_process_information(self, pid) -> "ProcessInfo":
        with ProcessHandle(pid, False, PROCESS_QUERY_INFORMATION | PROCESS_VM_READ) as handle:
            if not handle.valid:
                return None
            
            baseAddress = self.get_process_base_address(handle.value)
            if baseAddress is None:
                return None

            processName = self.get_process_name(handle.value, baseAddress)
            if processName is None:
                return None

            return ProcessInfo(pid, processName, baseAddress)

    def get_process_base_address(self, handle):
        bufferPointer, bufferSize = self.buffer.allocate(SIZE_POINTER * 64)
        success = PSAPI.EnumProcessModules(handle, bufferPointer, bufferSize, byref(c_uint32()), LIST_ALL_MODULES)
        if success == 0:
            return None
        (address,) = struct.unpack("@I", self.buffer.read(0, SIZE_POINTER))
        return address

    def get_process_name(self, handle, base_address):
        bufferPointer, bufferSize = self.buffer.allocate(SIZE_CHAR * 128)

        nameLength = PSAPI.GetModuleBaseNameA(handle, base_address, bufferPointer, bufferSize)
        if nameLength == 0:
            return None
        return self.buffer.read(0, nameLength).decode("ascii")
