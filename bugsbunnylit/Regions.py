from BaseClasses import Region
from .Locations import PS1Location, location_name_to_id


def create_regions(world):
    player = world.player
    
    menu = Region("Menu", player, world.multiworld)
    nowhere = Region("Nowhere", player, world.multiworld)
    stone_age = Region("Stone Age", player, world.multiworld)
    pirate = Region("Pirate Years", player, world.multiworld)
    medieval = Region("Medieval Period", player, world.multiworld)
    thirties = Region("1930's", player, world.multiworld)
    dimension_x = Region("Dimension X", player, world.multiworld)
    present_day_ending = Region("Present Day Ending", player, world.multiworld)
    pismo_beach_ending = Region("Pismo Beach Ending", player, world.multiworld)

    wabbit_on_run = Region("Wabbit on the Run!", player, world.multiworld)
    who_needs_kickstart = Region("Guess Who Needs a Kick Start", player, world.multiworld)
    magic_hare_blower = Region("Magic Hare Blower", player, world.multiworld)
    wabbit_duck_season = Region("Wabbit or Duck Season?", player, world.multiworld)
    stone_age_gc_purchase = Region("Stone Age: Golden Carrot Purchase", player, world.multiworld)

    whats_up_dock = Region("Hey... What's Up, Dock?", player, world.multiworld)
    mine_or_mine = Region("Mine or Mine?", player, world.multiworld)
    when_sam_met_bunny = Region("When Sam Met Bunny", player, world.multiworld)
    pirate_road = Region("Follow the Red Pirate Road", player, world.multiworld)
    pirate_gc_purchase = Region("Pirate Years: Golden Carrot Purchase", player, world.multiworld)

    downhill_duck = Region("Downhill Duck!", player, world.multiworld)
    whats_cooking_doc = Region("What's Cookin' Doc?", player, world.multiworld)
    albuquerque = Region("Witch Way to Albuquerque?", player, world.multiworld)
    carrothenge = Region("the Carrot-Henge Mystery", player, world.multiworld)
    medieval_gc_purchase = Region("Medieval Period: Golden Carrot Purchase", player, world.multiworld)

    big_bank = Region("the Big Bank Withdrawal", player, world.multiworld)
    objects_in_mirror = Region("Objects in the Mirror Are Closer Than They Appear!", player, world.multiworld)
    corrida = Region("La Corrida", player, world.multiworld)
    factory = Region("the Carrot Factory", player, world.multiworld)
    great_escape = Region("the Greatest Escape", player, world.multiworld)
    thirties_gc_purchase = Region("1930's: Golden Carrot Purchase", player, world.multiworld)

    planet_x_file = Region("the Planet X File!", player, world.multiworld)
    conquest_planet_x = Region("the Conquest for Planet X!", player, world.multiworld)
    train_brain = Region("Train Your Brain!", player, world.multiworld)
    vort_x_room = Region("Vort X Room", player, world.multiworld)
    dimension_x_gc_purchase = Region("Dimension X: Golden Carrot Purchase", player, world.multiworld)

    magic_sj = Region("Magic: Super Jump", player, world.multiworld)
    magic_mt = Region("Magic: Magical Tune", player, world.multiworld)
    magic_mf = Region("Magic: Magical Fan", player, world.multiworld)
    magic_mp = Region("Magic: Magical Password", player, world.multiworld)

    world.multiworld.regions += [
        menu,
        nowhere,
        stone_age,
        pirate,
        medieval,
        thirties,
        dimension_x,
        present_day_ending,
        pismo_beach_ending,

        wabbit_on_run,
        who_needs_kickstart,
        magic_hare_blower,
        wabbit_duck_season,
        stone_age_gc_purchase,

        whats_up_dock,
        mine_or_mine,
        when_sam_met_bunny,
        pirate_road,
        pirate_gc_purchase,

        downhill_duck,
        whats_cooking_doc,
        albuquerque,
        carrothenge,
        medieval_gc_purchase,

        big_bank,
        objects_in_mirror,
        corrida,
        factory,
        great_escape,
        thirties_gc_purchase,

        planet_x_file,
        conquest_planet_x,
        train_brain,
        vort_x_room,
        dimension_x_gc_purchase,

        magic_sj,
        magic_mt,
        magic_mf,
        magic_mp,
        ]
    menu.connect(nowhere)

    nowhere.connect(stone_age, "Stone Age")
    nowhere.connect(pirate, "Pirate Years")
    nowhere.connect(medieval, "Medieval Period")
    nowhere.connect(thirties, "1930's")
    nowhere.connect(dimension_x, "Dimension X")
    nowhere.connect(present_day_ending, "Present Day Ending")
    nowhere.connect(pismo_beach_ending, "Pismo Beach Ending")

    
    REGION_PREFIXES = {

    
    "Nowhere": nowhere,
    
    "Wabbit on the Run!": wabbit_on_run,
    "Guess Who Needs a Kick Start": who_needs_kickstart,
    "Magic Hare Blower": magic_hare_blower,
    "Wabbit or Duck Season?": wabbit_duck_season,
    "Stone Age: Golden Carrot Purchase": stone_age_gc_purchase,

    "Hey... What's Up, Dock?": whats_up_dock,
    "Mine or Mine?": mine_or_mine,
    "When Sam Met Bunny": when_sam_met_bunny,
    "Follow the Red Pirate Road": pirate_road,
    "Pirate Years: Golden Carrot Purchase": pirate_gc_purchase,

    "Downhill Duck!": downhill_duck,
    "What's Cookin' Doc?": whats_cooking_doc,
    "Witch Way to Albuquerque?": albuquerque,
    "the Carrot-Henge Mystery": carrothenge,
    "Medieval Period: Golden Carrot Purchase": medieval_gc_purchase,

    "the Big Bank Withdrawal": big_bank,
    "Objects in the Mirror Are Closer Than They Appear!": objects_in_mirror,
    "La Corrida": corrida,
    "the Carrot Factory": factory,
    "the Greatest Escape": great_escape,
    "1930's: Golden Carrot Purchase": thirties_gc_purchase,

    "the Planet X File!": planet_x_file,
    "the Conquest for Planet X!": conquest_planet_x,
    "Train Your Brain!": train_brain,
    "Vort X Room": vort_x_room,
    "Dimension X: Golden Carrot Purchase": dimension_x_gc_purchase,

    "Magic: Super Jump": magic_sj,
    "Magic: Magical Tune": magic_mt,
    "Magic: Magical Fan": magic_mf,
    "Magic: Magical Password": magic_mp,
    }

    stone_age.connect(wabbit_on_run, "Wabbit on the Run!")
    stone_age.connect(who_needs_kickstart, "Guess Who Needs a Kick Start")
    stone_age.connect(magic_hare_blower, "Magic Hare Blower")
    stone_age.connect(wabbit_duck_season, "Wabbit or Duck Season?")
    stone_age.connect(stone_age_gc_purchase, "Stone Age: Golden Carrot Purchase")

    pirate.connect(whats_up_dock, "Hey... What's Up, Dock?")
    pirate.connect(mine_or_mine, "Mine or Mine?")
    pirate.connect(when_sam_met_bunny, "When Sam Met Bunny")
    pirate.connect(pirate_road, "Follow the Red Pirate Road")
    pirate.connect(pirate_gc_purchase, "Pirate Years: Golden Carrot Purchase")

    medieval.connect(downhill_duck, "Downhill Duck!")
    medieval.connect(whats_cooking_doc, "What's Cookin' Doc?")
    medieval.connect(albuquerque, "Witch Way to Albuquerque?")
    medieval.connect(carrothenge, "the Carrot-Henge Mystery")
    medieval.connect(medieval_gc_purchase, "Medieval Period: Golden Carrot Purchase")
    medieval.connect(magic_sj, "Magic: Super Jump")
    medieval.connect(magic_mt, "Magic: Magical Tune")
    medieval.connect(magic_mf, "Magic: Magical Fan")
    medieval.connect(magic_mp, "Magic: Magical Password")

    thirties.connect(big_bank, "the Big Bank Withdrawal")
    thirties.connect(objects_in_mirror, "Objects in the Mirror Are Closer Than They Appear!")
    thirties.connect(corrida, "La Corrida")
    thirties.connect(factory, "the Carrot Factory")
    thirties.connect(great_escape, "the Greatest Escape")
    thirties.connect(thirties_gc_purchase, "1930's: Golden Carrot Purchase")

    dimension_x.connect(planet_x_file, "the Planet X File!")
    dimension_x.connect(conquest_planet_x, "the Conquest for Planet X!")
    dimension_x.connect(train_brain, "Train Your Brain!")
    dimension_x.connect(vort_x_room, "Vort X Room")
    dimension_x.connect(dimension_x_gc_purchase, "Dimension X: Golden Carrot Purchase")



    for name, id in location_name_to_id.items():
            for prefix, region in REGION_PREFIXES.items():
                if name.startswith(prefix):
                    region.locations.append(
                        PS1Location(player, name, id, region)
                    )
                    break







