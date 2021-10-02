from ctypes import c_double, c_float, sizeof
from process.process import Process

def default_handler(process: Process, address: int, _):
    return "<not-fetched>"

def int32_handler(process: Process, address: int, _):
    return process.read_int32(address)

def uint32_handler(process: Process, address: int, _):
    return process.read_uint32(address)

def string_handler(process: Process, address: int, _):
    return process.read_zstring(address)

def mat4_handler(process: Process, address: int, _):
    mat4 = [[None for _ in range(4)] for _ in range(4)]
    for i in range(4):
        for j in range(4):
            offset = (i * 4 + j) * sizeof(c_float)
            value = process.read_float(address + offset)
            mat4[i][j] = value
    return mat4

def custom_handler_factory(type):
    def custom_handler(process: Process, address: int, update_queue):
        object_address = process.read_int32(address)
        if object_address == 0:
            return None
        object = type(process, object_address)
        update_queue.append(object.update)
        return object
    
    return custom_handler
