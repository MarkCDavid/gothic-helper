from process.process_constants import KERNEL32

class ProcessHandle:
    def __init__(self, pid, inheritHandle, access):
        self.pid = pid
        self.inheritHandle = inheritHandle
        self.access = access
        self.value = 0
        self.valid = False

    def __enter__(self):
        self.value = KERNEL32.OpenProcess(self.access, self.inheritHandle, self.pid)
        self.valid = self.value != 0
        return self

    def __exit__(self, type, value, traceback):
        if(self.valid):
            KERNEL32.CloseHandle(self.value)
            self.value = 0
            self.valid = False
        return True