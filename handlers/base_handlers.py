from process.process import Process

def default_handler(process: Process, address: int, update_queue):
    return "<not-fetched>"

def int32_handler(process: Process, address: int, update_queue):
    return process.read_int32(address)

def uint32_handler(process: Process, address: int, update_queue):
    return process.read_uint32(address)

def string_handler(process: Process, address: int, update_queue):
    return process.read_zstring(address)

def custom_handler_factory(type):
    def custom_handler(process: Process, address: int, update_queue):
        object_address = process.read_int32(address)
        if object_address == 0:
            return None
        object = type(process, object_address)
        update_queue.append(object.update)
        return object
    
    return custom_handler
