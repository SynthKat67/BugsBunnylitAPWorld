from typing import Dict, NamedTuple
from BaseClasses import Location

BASE_LOCATION_ID = 742000

PLAYER_X_ADDRESS = 0x0BB580
PLAYER_Y_ADDRESS = 0x0BB588

GATE_Y_MIN = 8260
GATE_Y_MAX = 9450

WITCH_WAY_X_MIN = 6839
WITCH_WAY_X_MAX = 8060

CARROT_HENGE_X_MIN = 10440
CARROT_HENGE_X_MAX = 11640

class CounterGroup(NamedTuple):
    address: int
    max_count: int

class FlagGroup(NamedTuple):
    address: int
    flag: int

class LevelRequirement(NamedTuple):
    item: str
    amount: int = 1

class CoordinateGate(NamedTuple):
    x_min: int
    x_max: int
    y_min: int
    y_max: int

class ConditionalEntry(NamedTuple):
    address: int
    open_value: int
    closed_value: int
    gate: CoordinateGate

class LevelEntry(NamedTuple):
    entries: tuple
    requirements: tuple[LevelRequirement, ...]
    persistent_entries: tuple
    closed_entries: tuple
    conditional_entries: tuple[ConditionalEntry, ...] = ()
    protected_values: tuple = ()

class PS1Location(Location):
    game = "Bugs Bunny Lost in Time"


class MagicLocation:
    def __init__(self, address, value, region):
        self.address = address
        self.value = value
        self.region = region

magic_flags = {
    "Magic: Super Jump":FlagGroup(0x010048, 0x08),
    "Magic: Magical Tune":FlagGroup(0x010048, 0x04),
    "Magic: Magical Fan":FlagGroup(0x010048, 0x01),
    "Magic: Magical Password":FlagGroup(0x010048, 0x10),
}

magic_locations = {
            "Magic: Super Jump": MagicLocation(
                address=0x069450,
                value=0x17,
                region=0x0D,
                ),

            "Magic: Magical Tune":MagicLocation(
                address=0x069450,
                value=0x0F,
                region=0x10,
                ),

            "Magic: Magical Fan":MagicLocation(
                address=0x069450, 
                value=0x77,
                region=0x11,
                ),

            "Magic: Magical Password":MagicLocation(
                address=0x069450,
                value=0xCF,
                region=0x12,
                ),
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

level_entries = {

    "Wabbit on the Run!": LevelEntry(
        entries=(
            (0x0C3AF0, 0xC614),
        ),
        requirements=(
            LevelRequirement("Clock", 1),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0C3AF0, 0xC694),
        ),
    ),

    "Guess Who Needs a Kick Start": LevelEntry(
        entries=(
            (0x0C3CE4, 0xCB48),
        ),
        requirements=(
            LevelRequirement("Clock", 3),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0C3CE4, 0xCBC8),
        ),
    ),

    "Magic Hare Blower": LevelEntry(
        entries=(
            (0x0C3ED8, 0xD160),
        ),
        requirements=(
            LevelRequirement("Clock", 80),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0C3ED8, 0xD1E0),
        ),
    ),

    "Wabbit or Duck Season?": LevelEntry(
        entries=(
            (0x0C4A90, 0xD9DC),
        ),
        requirements=(
            LevelRequirement("Golden Carrot", 50),
            LevelRequirement("Clock", 1),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0C4A90, 0xDA5C),
        ),
    ),

    "Mine or Mine?": LevelEntry(
        entries=(
            (0x0B5860, 0x05A4),
        ),
        requirements=(
            LevelRequirement("Clock", 100),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B5860, 0x0624),
        ),
    ),

    "Follow the Red Pirate Road": LevelEntry(
        entries=(
            (0x0B5A54, 0x0BE0),
        ),
        requirements=(
            LevelRequirement("Clock", 11),
            LevelRequirement("Magic: Super Jump"),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B5A54, 0x0C80),
        ),
    ),

    "Hey... What's Up, Dock?": LevelEntry(
        entries=(
            (0x0B5478, 0xF950),
        ),
        requirements=(
            LevelRequirement("Clock", 5),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B5478, 0xF9F0),
        ),
    ),

    "When Sam Met Bunny": LevelEntry(
        entries=(
            (0x0B566C, 0xFF8C),
            (0x0B566E, 0x800F),
        ),
        requirements=(
            LevelRequirement("Clock", 35),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B566C, 0x000C),
            (0x0B566E, 0x8010),
        ),
    ),

    "What's Cookin' Doc?": LevelEntry(
        entries=(
            (0x0B2D68, 0xD928),
        ),
        requirements=(
            LevelRequirement("Clock", 30),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B2D68, 0xD9A8),
        ),
    ),

    "Witch Way to Albuquerque?": LevelEntry(
        entries=(
            (0x0B2F5C, 0xDF40),
        ),
        requirements=(
            LevelRequirement("Clock", 65),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B2F5C, 0xDFC0),
        ),
        conditional_entries=(
            ConditionalEntry(
                address=0x0B3D08,
                open_value=0xEE48,
                closed_value=0xEE08,
                gate=CoordinateGate(
                    x_min=WITCH_WAY_X_MIN,
                    x_max=WITCH_WAY_X_MAX,
                    y_min=GATE_Y_MIN,
                    y_max=GATE_Y_MAX,
                ),
            ),
        ),
    ),

    "the Carrot-Henge Mystery": LevelEntry(
        entries=(
            (0x0B3150, 0xE57C),
        ),
        requirements=(
            LevelRequirement("Clock", 73),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B3150, 0xE5FC),
        ),
        conditional_entries=(
            ConditionalEntry(
                address=0x0B3920,
                open_value=0xECC8,
                closed_value=0xEC88,
                gate=CoordinateGate(
                    x_min=CARROT_HENGE_X_MIN,
                    x_max=CARROT_HENGE_X_MAX,
                    y_min=GATE_Y_MIN,
                    y_max=GATE_Y_MAX,
                ),
            ),
        ),
    ),

    "Downhill Duck!": LevelEntry(
        entries=(
            (0x0B44D8, 0xF0EC),
        ),
        requirements=(
            LevelRequirement("Golden Carrot", 250),
            LevelRequirement("Clock", 30),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B44D8, 0xF16C),
        ),
    ),

    "the Big Bank Withdrawal": LevelEntry(
        entries=(
            (0x0B7D7C, 0x2A6C),
        ),
        requirements=(
            LevelRequirement("Clock", 15),
        ),
        persistent_entries=(),
        closed_entries=(
             (0x0B7D7C, 0x2ACC),
        ),
    ),

    "the Greatest Escape": LevelEntry(
        entries=(
            (0x0B7B88, 0x2430),
        ),
        requirements=(
            LevelRequirement("Clock", 25),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B7B88, 0x24B0),
        ),
    ),

    "Objects in the Mirror Are Closer Than They Appear!": LevelEntry(
        entries=(
            (0x0B8358, 0x2ED4),
        ),
        requirements=(
            LevelRequirement("Clock", 50),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B8358, 0x2F54),
        ),
    ),

    "the Carrot Factory": LevelEntry(
        entries=(
            (0x0B7994, 0x1D50),
        ),
        requirements=(
            LevelRequirement("Clock", 90),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0B7994, 0x1E10),
        ),
    ),

    "La Corrida": LevelEntry(
        entries=(
            (0x0BA48C, 0x3CA8),
        ),
        requirements=(
            LevelRequirement("Golden Carrot", 150),
            LevelRequirement("Clock", 15),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0BA48C, 0x3D28),
        ),
    ),

    "Vort X Room": LevelEntry(
        entries=(
            (0x0C0A1C, 0xBF78),
        ),
        requirements=(
            LevelRequirement("Clock", 60),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0C0A1C, 0xBF58),
        ),
    ),

    "Train Your Brain!": LevelEntry(
        entries=(
            (0x0BFC70, 0xAA94),
        ),
        requirements=(
            LevelRequirement("Clock", 117),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0BFC70, 0xAB14),
        ),
        protected_values=(
            (0x0BFC70, 0xAB74),
        ),
    ),

    "the Conquest for Planet X!": LevelEntry(
        entries=(
            (0x0BFE64, 0xB2DC),
            (0x0C024C, 0xB7C4),
        ),
        requirements=(
            LevelRequirement("Clock", 70),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0BFE64, 0xB39C),
            (0x0C024C, 0xB7A4),
        ),
        protected_values=(
            (0x0C024C, 0xB31C),
            (0x0C024C, 0xB2FC),
            (0x0C024C, 0xB37C),
            (0x0C024C, 0xB35C),
            (0x0C024C, 0xB7C4),
        ),
    ),

    "the Planet X File!": LevelEntry(
        entries=(
            (0x0BFA7C, 0xA22C),
        ),
        requirements=(
            LevelRequirement("Clock", 40),
        ),
        persistent_entries=(),
        closed_entries=(
            (0x0BFA7C, 0xA2AC),
        ),
        protected_values=(
            (0x0BFA7C, 0xA32C),
        ),
    ),
}



location_name_to_id: Dict[str, int] = {}

current_id = BASE_LOCATION_ID + 1

for name in magic_locations:
    location_name_to_id[name] = current_id
    current_id += 1

for name in HubCarrots:
    location_name_to_id[name] = current_id
    current_id += 1

for group_name, group_data in counter_groups.items():
    for i in range(1, group_data.max_count + 1):
        location_name_to_id[f"{group_name} - {i}"] = current_id
        current_id += 1