from queue import Queue
from collections import Set
from process.process import Process
from g2.memory.objects import Object, ObjectField

class Resolver:
    
    def __init__(self, process: "Process", root: "Object"):
        self.process = process
        self.root = root
        self.pointerMap = {}

    def resolve_root(self):
        self.pointerMap.clear()
        self.pointerMap[self.root.address] = self.root

        self.root.load_memory()
        
        fieldsToResolve: "Queue[ObjectField]" = Queue()
        for fieldToResolve in self.root.get_fields():
            fieldsToResolve.put(fieldToResolve)

        while not fieldsToResolve.empty():
            fieldToResolve = fieldsToResolve.get()
            fieldToResolve.resolve(fieldsToResolve, self.pointerMap)
    
    def resolve(self, root: "Object"):
        root.load_memory()
        
        fieldsToResolve: "Queue[ObjectField]" = Queue()
        for fieldToResolve in root.get_fields():
            fieldsToResolve.put(fieldToResolve)

        while not fieldsToResolve.empty():
            fieldToResolve = fieldsToResolve.get()
            fieldToResolve.resolve(fieldsToResolve, self.pointerMap, True)
        