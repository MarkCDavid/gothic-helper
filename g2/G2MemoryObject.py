
class G2MemoryObject:
    def __init__(self, process, address):
        self.process = process
        self.address = address
        self.values = {}

    def __getitem__(self, index):
        if isinstance(index, tuple):
            return None
        return self.values[index]

    def update(self, update_queue):
        for field in self.fields:
            offset, handler = self.fields[field]
            self.values[field] = handler(self.process, self.address + offset, update_queue)

            

    def __str__(self) -> str:
        return f"\n{type(self)} address: {hex(self.address)}\n{self.values}\n"
