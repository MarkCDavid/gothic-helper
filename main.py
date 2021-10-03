from g2.memory.objectsUtils import sortList_iterator, zstring_value
from g2.memory.resolver import Resolver
from g2.npc import Npc
from g2.world import World
from process.process import Process
import time 

HERO_OBJECT_NAME = "PC_HERO"

def get_hero(world: World) -> "Npc":
    for npc in sortList_iterator(world.npcList):
        if zstring_value(npc.objectName) == HERO_OBJECT_NAME:
            return npc
    return None

with Process("Gothic2.exe") as g2:
    world_address = g2.follow_pointer_path([0x393240, 0x80, 0xB8, 0x10, 0xB8])
    world = World(g2, world_address)

    start = time.time_ns()

    resolver = Resolver(g2, world)
    resolver.resolve()

    end = time.time_ns()
    duration = end - start
    print(f"Resolving took: {duration/1000000000}s")

    hero = get_hero(world)
    print(zstring_value(hero.objectName))
    print(zstring_value(hero.name))
    print(f"Item is at {hero.transform.get_coordinates()} and is in {hero.homeWorld}")
   