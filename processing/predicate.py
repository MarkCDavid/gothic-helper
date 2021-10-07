from processing.vobfetcher import NpcFetcher
from processing.types import Item, Npc, Vob

def build_default_ignore_predicate():
    def predicate(vob: Vob, hero: Npc):
        if vob.homeWorld == 0:
            return True
            
        if vob.address == hero.address:
            return True

        return False
    return predicate

def build_item_ignore_predicate(npcFetcher: NpcFetcher):
    def predicate(vob: Item, hero: Npc):
        if build_default_ignore_predicate()(vob, hero):
            return True
       
        if vob.address in npcFetcher.ignoreItems:
            return True

        return False
    return predicate



