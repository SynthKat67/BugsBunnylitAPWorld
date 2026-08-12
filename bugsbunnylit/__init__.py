from worlds.AutoWorld import World
from .Options import BugsBunnyLiTOptions, Goal
from .Items import PS1GameItem, item_table, item_data_table
from .Locations import PS1Location, location_name_to_id
from .Regions import create_regions
from .Rules import set_rules
print("BUGS BUNNY WORLD IMPORTED")

class BugsBunnyLiT(World):
    game = "Bugs Bunny Lost in Time"
    options_dataclass = BugsBunnyLiTOptions

    item_name_to_id = item_table
    location_name_to_id = location_name_to_id

    def __init__(self, multiworld, player):
        super().__init__(multiworld, player)

    def create_regions(self):
        create_regions(self)

    def set_rules(self):
        set_rules(self)

        if self.options.goal.value == Goal.option_present_day:

            self.multiworld.completion_condition[self.player] = (
                lambda state:
                state.can_reach(
                    "Present Day Ending",
                    "Region",
                    self.player,
                )
            )

        elif self.options.goal.value == Goal.option_pismo_beach:

            self.multiworld.completion_condition[self.player] = (
                lambda state:
                state.can_reach(
                    "Pismo Beach Ending",
                    "Region",
                    self.player,
                )
            )
        

    def fill_slot_data(self):
        return {
            "death_link": self.options.death_link.value,
        }


    def create_item(self, name: str):
        data = item_data_table[name]
        return PS1GameItem(
            name,
            data.classification,
            data.code,
            self.player,
        )

    
    def create_items(self):
        pool = []
    

        pool.extend(self.create_item("Golden Carrot") for _ in range(333))
        pool.extend(self.create_item("Clock") for _ in range(124))

        for magic in (
        "Magic: Super Jump",
        "Magic: Magical Tune",
        "Magic: Magical Fan",
        "Magic: Magical Password",
        ):
            pool.append(self.create_item(magic))


        self.multiworld.itempool += pool

from . import client