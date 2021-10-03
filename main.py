from collections import deque
from g2 import item
from g2.memory.resolver import Resolver
from g2.world import World
from process.process import Process

with Process("Gothic2.exe") as g2:
    world_address = g2.follow_pointer_path([0x393240, 0x80, 0xB8, 0x10, 0xB8])
    world = World(g2, world_address)
    resolver = Resolver(g2, world)
    resolver.resolve()

    print(world.worldName)
   