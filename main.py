from collections import deque
from process.process import Process
from g2.world import World


with Process("Gothic2.exe") as g2:
    world_address = g2.follow_pointer_path([0x393240, 0x80, 0xB8, 0x10, 0xB8])
    world = World(g2, world_address)
    update_queue = deque()
    
    update_queue.append(world.update)
   
    while update_queue:
        current_update = update_queue.popleft()
        current_update(update_queue)

    item_count = {}
    item_list = world["voblist_npcs"]
    i = 0
    while item_list is not None:
        item = item_list["data"]
        if item != None:
            name = item["name"]
            if name in item_count:
                item_count[name] += 1
            else:
                item_count[name] = 1
        item_list = item_list["next"]
    
    for item in sorted(item_count):
        print(f"{item}: {item_count[item]}")