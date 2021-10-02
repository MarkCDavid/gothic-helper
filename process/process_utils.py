from ctypes import c_uint32, c_char, create_string_buffer, byref, sizeof
from process.process_handle import ProcessHandle
from process.process_constants import  PSAPI, LIST_ALL_MODULES, PROCESS_QUERY_INFORMATION, PROCESS_VM_READ
import struct


# TODO: Introduce ProcessInformation class/struct
def get_process_info_by_name(processName):
    allProcessesInformation = [get_process_information(pid) for pid in get_current_processes()]
    currentProcessesInformation = [x for x in allProcessesInformation if x is not None]
    for processInformation in currentProcessesInformation:
        _, _, name  = processInformation
        if name == processName:
            return processInformation
    return None


def get_current_processes(count=512):
    process_pids = []

    bufferSize = sizeof(c_uint32) * count
    buffer = create_string_buffer(bufferSize)
    readBytes = c_uint32()
    if not PSAPI.EnumProcesses(buffer, bufferSize, byref(readBytes)):
        return process_pids

    for step in range(0, readBytes.value, sizeof(c_uint32)):
        pid_slice = slice(step, step + sizeof(c_uint32))
        (pid,) = struct.unpack("@i", buffer.raw[pid_slice])
        process_pids.append(pid)

    return process_pids

def get_process_information(pid):
    with ProcessHandle(pid, False, PROCESS_QUERY_INFORMATION | PROCESS_VM_READ) as handle:
        if not handle.valid:
            return None

        base_address = get_process_base_address(handle.value)
        if base_address is None:
            return None

        process_name = get_process_name(handle.value, base_address)
        if process_name is None:
            return None

        return (pid, base_address, process_name)

def get_process_base_address(handle):
    buffer, bufferSize = create_buffer(c_uint32, 64)
    count = c_uint32()

    success = PSAPI.EnumProcessModules(handle, buffer, bufferSize, byref(count), LIST_ALL_MODULES)

    return buffer[0] if success else None

def get_process_name(handle, base_address):
    buffer, bufferSize = create_buffer(c_char, 128)

    success = PSAPI.GetModuleBaseNameA(handle, base_address, buffer, bufferSize)

    return buffer.value.decode("ascii") if success else None

def create_buffer(type, size):
    array_type = type * size
    python_buffer = [0 for _ in range(size)]
    buffer = (array_type)(*list(python_buffer))
    return (buffer, sizeof(type) * len(buffer))