from typing import Dict, NamedTuple
from BaseClasses import Item, ItemClassification

BASE_ITEM_ID = 742000


class GameItemData(NamedTuple):
    code: int
    classification: ItemClassification


item_templates = {

    "Golden Carrot": ItemClassification.progression,
    "Clock": ItemClassification.progression,
    "Magic: Super Jump": ItemClassification.progression,
    "Magic: Magical Tune": ItemClassification.progression,
    "Magic: Magical Fan": ItemClassification.progression,
    "Magic: Magical Password": ItemClassification.progression,
}

item_table: Dict[str, int] = {}
item_data_table: Dict[str, GameItemData] = {}


item_name_groups = {
    "Magic": {
        "Magic: Super Jump",
        "Magic: Magical Tune",
        "Magic: Magical Fan",
        "Magic: Magical Password",
    },
}


current_id = BASE_ITEM_ID + 1

for item_name, classification in item_templates.items():
    item_table[item_name] = current_id
    item_data_table[item_name] = GameItemData(code=current_id, classification=classification)
    current_id += 1

class PS1GameItem(Item):
    game: str = "Bugs Bunny Lost in Time"



