from ctypes import c_byte, c_double, c_float, c_int32, c_uint32, sizeof

SIZE_POINTER = sizeof(c_uint32)
SIZE_HANDLE = sizeof(c_uint32)
SIZE_PID = sizeof(c_uint32)

SIZE_INT32 = sizeof(c_int32)
SIZE_UINT32 = sizeof(c_uint32)
SIZE_FLOAT = sizeof(c_float)
SIZE_DOUBLE = sizeof(c_double)

SIZE_CHAR = sizeof(c_byte)
SIZE_BYTE = sizeof(c_byte)