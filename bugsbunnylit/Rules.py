from worlds.generic.Rules import set_rule

MAGIC_RULES = {

        
    "Magic Hare Blower: Clock - 14": ["Magic: Magical Fan"],
    "Magic Hare Blower: Clock - 13": ["Magic: Magical Fan"],
    "Magic Hare Blower: Clock - 12": ["Magic: Magical Fan"],
    "Magic Hare Blower: Clock - 11": ["Magic: Magical Fan"],
    "Magic Hare Blower: Clock - 10": ["Magic: Magical Fan"],
    "Magic Hare Blower: Clock - 9": ["Magic: Magical Fan"],
    "Magic Hare Blower: Clock - 8": ["Magic: Magical Fan"],

    "Magic Hare Blower: Golden Carrot - 31": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 30": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 29": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 28": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 27": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 26": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 25": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 24": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 23": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 22": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 21": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 20": ["Magic: Magical Fan"],
    "Magic Hare Blower: Golden Carrot - 19": ["Magic: Magical Fan"],



    "Follow the Red Pirate Road: Clock - 4": ["Magic: Magical Tune"],

    "Follow the Red Pirate Road: Golden Carrot - 9": ["Magic: Magical Tune"],
    "Follow the Red Pirate Road: Golden Carrot - 8": ["Magic: Magical Tune"],
    "Follow the Red Pirate Road: Golden Carrot - 7": ["Magic: Magical Tune"],
    "Follow the Red Pirate Road: Golden Carrot - 6": ["Magic: Magical Tune"],
    "Follow the Red Pirate Road: Golden Carrot - 5": ["Magic: Magical Tune"],
    "Follow the Red Pirate Road: Golden Carrot - 4": ["Magic: Magical Tune"],



    "What's Cookin' Doc?: Clock - 15": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Clock - 14": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Clock - 13": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Clock - 12": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Clock - 11": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Clock - 10": ["Magic: Magical Fan"],
    "What's Cookin' Doc?: Clock - 9": ["Magic: Magical Fan"],

    "What's Cookin' Doc?: Golden Carrot - 37": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 36": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 35": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 34": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 33": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 32": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 31": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 30": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 29": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 28": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 27": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 26": ["Magic: Magical Tune"],
    "What's Cookin' Doc?: Golden Carrot - 25": ["Magic: Magical Fan"],



    "the Carrot-Henge Mystery: Clock - 8": ["Magic: Magical Password"],
    "the Carrot-Henge Mystery: Clock - 7": ["Magic: Magical Password"],
    "the Carrot-Henge Mystery: Clock - 6": ["Magic: Magical Password"],

    "the Carrot-Henge Mystery: Golden Carrot - 20": ["Magic: Magical Password"],
    "the Carrot-Henge Mystery: Golden Carrot - 19": ["Magic: Magical Password"],
    "the Carrot-Henge Mystery: Golden Carrot - 18": ["Magic: Magical Password"],


    "the Greatest Escape: Clock - 6": ["Magic: Super Jump"],
    "the Greatest Escape: Clock - 5": ["Magic: Super Jump", "Magic: Magical Tune"],

    "the Greatest Escape: Golden Carrot - 15": ["Magic: Super Jump"],
    "the Greatest Escape: Golden Carrot - 14": ["Magic: Super Jump"],
    "the Greatest Escape: Golden Carrot - 13": ["Magic: Super Jump", "Magic: Magical Tune"],

    }

def set_rules(world):

    for location, requirements in MAGIC_RULES.items():
        set_rule(
            world.get_location(location),
            lambda state, req=requirements: all(
                state.has(item, world.player)
                for item in req
        )
    )

    ENTRANCE_RULES = {

    "Stone Age": lambda state, p: state.has("Clock", p, 1),
    "Pirate Years": lambda state, p: state.has("Clock", p, 5),
    "1930's": lambda state, p: state.has("Clock", p, 15),
    "Medieval Period": lambda state, p: state.has("Clock", p, 30),
    "Dimension X": lambda state, p: state.has("Clock", p, 40),
    "Present Day Ending": lambda state, p: state.has("Clock", p, 120),
    "Pismo Beach Ending": lambda state, p:
    state.has("Clock", p, 124)
    and state.has("Golden Carrot", p, 333)
    and state.has("Magic: Super Jump", p)
    and state.has("Magic: Magical Tune", p)
    and state.has("Magic: Magical Fan", p)
    and state.has("Magic: Magical Password", p),

    "Wabbit on the Run!": lambda state, p: state.has("Clock", p, 1),
    "Guess Who Needs a Kick Start": lambda state, p: state.has("Clock", p, 3),
    "Wabbit or Duck Season?":lambda state, p: state.has("Golden Carrot", p, 50) and state.has("Clock", p, 1),
    "Magic Hare Blower": lambda state, p: state.has("Clock", p, 80),
    "Stone Age: Golden Carrot Purchase":lambda state, p: state.has("Clock", p, 1),

    "Hey... What's Up, Dock?": lambda state, p: state.has("Clock", p, 5),
    "When Sam Met Bunny": lambda state, p: state.has("Clock", p, 35),
    "Mine or Mine?": lambda state, p: state.has("Clock", p, 100),
    "Follow the Red Pirate Road": lambda state, p: state.has("Clock", p, 11) and state.has("Magic: Super Jump", p),
    "Pirate Years: Golden Carrot Purchase":lambda state, p: state.has("Clock", p, 5),

    "What's Cookin' Doc?": lambda state, p: state.has("Clock", p, 30),
    "Witch Way to Albuquerque?": lambda state, p: state.has("Clock", p, 65),
    "the Carrot-Henge Mystery": lambda state, p: state.has("Clock", p, 73),
    "Downhill Duck!": lambda state, p: state.has("Golden Carrot", p, 250) and state.has("Clock", p, 30),
    "Medieval Period: Golden Carrot Purchase":lambda state, p: state.has("Clock", p, 30),
    "Magic: Super Jump":lambda state, p: state.has("Clock", p, 30),
    "Magic: Magical Tune":lambda state, p: state.has("Clock", p, 65),
    "Magic: Magical Fan":lambda state, p: state.has("Clock", p, 73),
    "Magic: Magical Password":lambda state, p: state.has("Clock", p, 73),


    "the Big Bank Withdrawal": lambda state, p: state.has("Clock", p, 15),
    "the Greatest Escape": lambda state, p: state.has("Clock", p, 25),
    "Objects in the Mirror Are Closer Than They Appear!": lambda state, p: state.has("Clock", p, 50),
    "the Carrot Factory": lambda state, p: state.has("Clock", p, 90),
    "La Corrida": lambda state, p: state.has("Golden Carrot", p, 150) and state.has("Clock", p, 15),
    "1930's: Golden Carrot Purchase":lambda state, p: state.has("Clock", p, 15),

    "the Planet X File!": lambda state, p: state.has("Clock", p, 40),
    "Vort X Room": lambda state, p: state.has("Clock", p, 60),
    "the Conquest for Planet X!": lambda state, p: state.has("Clock", p, 70),
    "Train Your Brain!": lambda state, p: state.has("Clock", p, 117),
    "Dimension X: Golden Carrot Purchase":lambda state, p: state.has("Clock", p, 40),
   
    }

    print("=== Registered Entrances ===")
    for region in world.multiworld.regions:
        for exit in region.exits:
            print(repr(exit.name))

    print("=== Rule Entrances ===")
    for entrance in ENTRANCE_RULES:
        print(repr(entrance))


    for entrance, rule in ENTRANCE_RULES.items():
        set_rule(
        world.get_entrance(entrance),
        lambda state, r=rule: r(state, world.player)
    )

