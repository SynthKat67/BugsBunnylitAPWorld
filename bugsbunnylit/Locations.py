from typing import Dict, NamedTuple
from BaseClasses import Location
BASE_LOCATION_ID = 742000

class CounterGroup(NamedTuple):
    address: int
    max_count: int

class FlagGroup(NamedTuple):
    address: int
    flag: int

class PS1Location(Location):
    game = "Bugs Bunny Lost in Time"

magic_flags = {
    "Magic: Super Jump":FlagGroup(0x010048, 0x08),
    "Magic: Magical Tune":FlagGroup(0x010048, 0x04),
    "Magic: Magical Fan":FlagGroup(0x010048, 0x01),
    "Magic: Magical Password":FlagGroup(0x010048, 0x10),
}


HubCarrots = {

    "Stone Age: Golden Carrot Purchase":FlagGroup(0x01010C, 0x02),
    "Pirate Years: Golden Carrot Purchase":FlagGroup(0x01010C, 0x08),
    "Medieval Period: Golden Carrot Purchase":FlagGroup(0x01010C, 0x04),
    "1930's: Golden Carrot Purchase":FlagGroup(0x01010C, 0x10),
    "Dimension X: Golden Carrot Purchase":FlagGroup(0x01010C, 0x20),

}

counter_groups = {
    # Nowhere checks

    "Nowhere: Golden Carrot": CounterGroup(0x0100F5, 10),
    "Nowhere: Clock": CounterGroup(0x010101, 1),

    # Stone Age checks

    "Wabbit on the Run!: Golden Carrot": CounterGroup(0x010094, 22),
    "Wabbit on the Run!: Clock": CounterGroup(0x0100BA, 9),

    "Guess Who Needs a Kick Start: Golden Carrot": CounterGroup(0x010095, 5),
    "Guess Who Needs a Kick Start: Clock": CounterGroup(0x0100BB, 1),

    "Magic Hare Blower: Golden Carrot": CounterGroup(0x010096, 31),
    "Magic Hare Blower: Clock":CounterGroup(0x0100BC, 14),

    "Wabbit or Duck Season?: Clock":CounterGroup(0x010136, 1),

    # Pirate Years checks

    "Hey... What's Up, Dock?: Golden Carrot":CounterGroup(0x01009B, 17),
    "Hey... What's Up, Dock?: Clock":CounterGroup(0x0100C1, 9),

    "Mine or Mine?: Golden Carrot":CounterGroup(0x01009D, 41),
    "Mine or Mine?: Clock":CounterGroup(0x0100C3, 10),

    "When Sam Met Bunny: Golden Carrot":CounterGroup(0x01009C, 2),
    "When Sam Met Bunny: Clock":CounterGroup(0x0100C2, 1),

    "Follow the Red Pirate Road: Golden Carrot":CounterGroup(0X01009E, 9),
    "Follow the Red Pirate Road: Clock":CounterGroup(0x0100C4, 4),

    # Medieval Period Checks

    "Downhill Duck!: Clock":CounterGroup(0x01012A, 1),

    "What's Cookin' Doc?: Golden Carrot":CounterGroup(0x010097, 37),
    "What's Cookin' Doc?: Clock":CounterGroup(0x0100BD, 15),

    "Witch Way to Albuquerque?: Golden Carrot":CounterGroup(0x010098, 8),
    "Witch Way to Albuquerque?: Clock":CounterGroup(0x0100BE, 1),

    "the Carrot-Henge Mystery: Golden Carrot":CounterGroup(0x010099, 20),
    "the Carrot-Henge Mystery: Clock":CounterGroup(0x0100BF, 8),

    # 1930's Checks

    "the Big Bank Withdrawal: Golden Carrot":CounterGroup(0x01009F, 15),
    "the Big Bank Withdrawal: Clock":CounterGroup(0x0100C5, 6),

    "Objects in the Mirror Are Closer Than They Appear!: Golden Carrot":CounterGroup(0x0100A3, 15),
    "Objects in the Mirror Are Closer Than They Appear!: Clock":CounterGroup(0x0100C9, 4),

    "La Corrida: Golden Carrot":CounterGroup(0x010138, 5),
    "La Corrida: Clock":CounterGroup(0x0100EF, 1),

    "the Carrot Factory: Golden Carrot":CounterGroup(0x0100A1, 15),
    "the Carrot Factory: Clock":CounterGroup(0x0100C7, 8),

    "the Greatest Escape: Golden Carrot":CounterGroup(0x0100A0, 15),
    "the Greatest Escape: Clock":CounterGroup(0x0100C6, 6),

    # Dimension X Checks

    "the Planet X File!: Golden Carrot":CounterGroup(0x0100A4, 26),
    "the Planet X File!: Clock":CounterGroup(0x0100CA, 14),

    "the Conquest for Planet X!: Golden Carrot":CounterGroup(0x0100A5, 14),
    "the Conquest for Planet X!: Clock":CounterGroup(0x0100CB, 1),

    "Train Your Brain!: Golden Carrot":CounterGroup(0x010124, 21),
    "Train Your Brain!: Clock":CounterGroup(0x010125, 5),

    "Vort X Room: Clock":CounterGroup(0X0100CC, 4),
    }





       
location_name_to_id:Dict[str, int] ={}
current_id = BASE_LOCATION_ID + 1

for name in magic_flags:
    location_name_to_id[name] = current_id
    current_id += 1

for name in HubCarrots:
    location_name_to_id[name] = current_id
    current_id += 1

for group_name, group_data in counter_groups.items():
    for i in range(1, group_data.max_count + 1):
        location_name_to_id[f"{group_name} - {i}"] = current_id
        current_id += 1