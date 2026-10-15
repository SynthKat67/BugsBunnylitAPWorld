from worlds.AutoWorld import World
from .Options import BugsBunnyLiTOptions, Goal
from .Items import PS1GameItem, item_table, item_data_table
from .Locations import PS1Location, location_name_to_id, level_entries, LevelRequirement, magic_flags
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

        self.level_requirements = {}

    # ========================
    # GENERATION
    # ========================

    def generate_early(self):
        self.level_requirements = self.generate_level_requirements()   

    def post_fill(self):
        self.debug_magic_access()
        self.debug_spheres()
        self.debug_magic_spheres()

    def create_regions(self):
        create_regions(self)

    def debug_magic_access(self):
        print("\n========================================")
        print("       MAGIC ACCESS DEBUG")
        print("========================================")

        state = self.multiworld.state

        magic_items = [
            "Magic: Super Jump",
            "Magic: Magical Tune",
            "Magic: Magical Fan",
            "Magic: Magical Password",
        ]

        for magic in magic_items:
            locations = []

            for location in self.multiworld.get_locations(self.player):
                if location.item is not None:
                    if location.item.name == magic:
                        locations.append(location)

            print(f"\n{magic}")

            if not locations:
                print("  NOT PLACED")
                continue

            for location in locations:
                print(
                    f"  Located at: {location.name}"
                )

                try:
                    reachable = state.can_reach(location)
                    print(
                        f"  Reachable now: {reachable}"
                    )
                except Exception as e:
                    print(
                        f"  Reachability check failed: {e}"
                    )

    def debug_spheres(self):

        print("\n========================================")
        print("          PROGRESSION SPHERES")
        print("========================================")

        state = self.multiworld.state

        spheres = self.multiworld.get_spheres()

        for sphere_number, sphere in enumerate(spheres):

            print(f"\n--- SPHERE {sphere_number} ---")

            for location in sphere:
                if location.player != self.player:
                    continue

                item = location.item

                if item is None:
                    print(f"  {location.name} -> EMPTY")
                else:
                    print(
                        f"  {location.name} -> {item.name}"
                    )

    def debug_magic_spheres(self):
        print("\n========================================")
        print("          MAGIC SPHERES")
        print("========================================")

        spheres = self.multiworld.get_spheres()

        magic_items = {
            "Magic: Super Jump",
            "Magic: Magical Tune",
            "Magic: Magical Fan",
            "Magic: Magical Password",
        }

        for sphere_number, sphere in enumerate(spheres):
            for location in sphere:
                if location.player != self.player:
                    continue

                if location.item and location.item.name in magic_items:
                    print(
                        f"{location.item.name} "
                        f"-> Sphere {sphere_number} "
                        f"-> {location.name}"
                    )

    def set_rules(self):
        set_rules(self)

        if self.options.goal.value == Goal.option_present_day:

            self.multiworld.completion_condition[self.player] = (
                lambda state:
                state.has(
                    "Game Complete",
                    self.player,
                )
            )

    # LEVEL UNLOCK RANDOMIZER

    def generate_level_requirements(self):

        if self.options.level_requirements.value == 0:
            requirements = {
                level_name: list(level.requirements)
                for level_name, level in level_entries.items()
            }

        else:
            level_names = list(level_entries.keys())

            # Keep the requirement sets themselves intact. We only shuffle
            # which level receives each set. Super Jump is restored below as
            # the permanent requirement of Follow the Red Pirate Road.
            requirement_sets = [
                [
                    requirement
                    for requirement in level.requirements
                    if requirement.item != "Magic: Super Jump"
                ]
                for level in level_entries.values()
            ]

            level_capacity = {
                "Wabbit on the Run!": 31,
                "Guess Who Needs a Kick Start": 6,
                "Magic Hare Blower": 45,
                "Wabbit or Duck Season?": 1,
                "Mine or Mine?": 51,
                "Follow the Red Pirate Road": 13,
                "Hey... What's Up, Dock?": 26,
                "When Sam Met Bunny": 3,
                "What's Cookin' Doc?": 52,
                "Witch Way to Albuquerque?": 9,
                "the Carrot-Henge Mystery": 28,
                "Downhill Duck!": 1,
                "the Big Bank Withdrawal": 21,
                "the Greatest Escape": 21,
                "Objects in the Mirror Are Closer Than They Appear!": 19,
                "the Carrot Factory": 23,
                "La Corrida": 6,
                "Vort X Room": 4,
                "Train Your Brain!": 26,
                "the Conquest for Planet X!": 15,
                "the Planet X File!": 40,
            }

            # These are the five independent era hubs. We don't force an
            # exact order, but we strongly prefer not to put every cheap
            # requirement into one era while another era is completely gated.
            era_groups = {
                "Stone Age": {
                    "Wabbit on the Run!",
                    "Guess Who Needs a Kick Start",
                    "Magic Hare Blower",
                    "Wabbit or Duck Season?",
                },
                "Pirate Years": {
                    "Hey... What's Up, Dock?",
                    "Mine or Mine?",
                    "When Sam Met Bunny",
                    "Follow the Red Pirate Road",
                },
                "Medieval Period": {
                    "Downhill Duck!",
                    "What's Cookin' Doc?",
                    "Witch Way to Albuquerque?",
                    "the Carrot-Henge Mystery",
                },
                "1930's": {
                    "the Big Bank Withdrawal",
                    "Objects in the Mirror Are Closer Than They Appear!",
                    "La Corrida",
                    "the Carrot Factory",
                    "the Greatest Escape",
                },
                "Dimension X": {
                    "the Planet X File!",
                    "the Conquest for Planet X!",
                    "Train Your Brain!",
                    "Vort X Room",
                },
            }

            def requirement_pair(reqs):
                clocks = 0
                carrots = 0

                for requirement in reqs:
                    if requirement.item == "Clock":
                        clocks = requirement.amount
                    elif requirement.item == "Golden Carrot":
                        carrots = requirement.amount

                return clocks, carrots

            def unlocks(reqs, clocks, carrots):
                req_clocks, req_carrots = requirement_pair(reqs)
                return (
                    req_clocks <= clocks
                    and req_carrots <= carrots
                )

            # The important property for AP's restrictive progression fill is
            # the shape of the "reachable location curve": how many checks
            # become available as the player accumulates clocks/carrots.
            #
            # Earlier versions used hard pass/fail thresholds. This version
            # instead scores that entire curve, with much stronger weight on
            # the early game where a bad assignment can strand hundreds of
            # progression items.
            clock_checkpoints = [
                (0, 20.0),
                (1, 18.0),
                (3, 17.0),
                (5, 16.0),
                (11, 14.0),
                (15, 12.0),
                (25, 10.0),
                (30, 8.0),
                (35, 7.0),
                (40, 6.0),
                (50, 5.0),
                (60, 4.0),
                (70, 3.0),
                (80, 2.0),
                (100, 1.5),
                (117, 1.0),
                (124, 0.5),
            ]

            carrot_checkpoints = [
                (0, 4.0),
                (50, 2.5),
                (150, 1.5),
                (250, 0.75),
                (333, 0.25),
            ]

            def curve_score(candidate):
                score = 0.0

                # At each clock total, reward unlocked capacity. A level with
                # 52 checks becoming available at 15 clocks is much more
                # useful to the restrictive fill than a 1-check level opening
                # at 15 clocks.
                for clocks, weight in clock_checkpoints:
                    capacity = sum(
                        level_capacity[level_name]
                        for level_name, reqs in candidate.items()
                        if unlocks(reqs, clocks, 0)
                    )

                    score -= capacity * weight

                # Carrot gates are much rarer, so use them as secondary
                # checkpoints. Evaluate them at useful clock totals too.
                for carrots, weight in carrot_checkpoints:
                    for clocks in (0, 15, 30, 50):
                        capacity = sum(
                            level_capacity[level_name]
                            for level_name, reqs in candidate.items()
                            if unlocks(reqs, clocks, carrots)
                        )

                        score -= capacity * weight

                return score

            def bottleneck_penalty(candidate):
                # Penalize especially bad early bottlenecks. These are still
                # soft penalties: no candidate is rejected.
                score = 0.0

                for clocks in (0, 1, 3, 5, 11, 15, 30):
                    capacity = sum(
                        level_capacity[level_name]
                        for level_name, reqs in candidate.items()
                        if unlocks(reqs, clocks, 0)
                    )

                    if capacity < 20:
                        score += (20 - capacity) * 8.0
                    elif capacity < 40:
                        score += (40 - capacity) * 2.0

                # We especially want a healthy amount of capacity before the
                # large 50/150/250-carrot gates arrive.
                for clocks, carrots, target in (
                    (15, 50, 70),
                    (30, 50, 120),
                    (30, 150, 180),
                    (50, 150, 240),
                    (50, 250, 300),
                ):
                    capacity = sum(
                        level_capacity[level_name]
                        for level_name, reqs in candidate.items()
                        if unlocks(reqs, clocks, carrots)
                    )

                    if capacity < target:
                        score += (target - capacity) * 0.35

                return score

            def era_penalty(candidate):
                score = 0.0

                for era_levels in era_groups.values():
                    # At 15 clocks, each era should have at least some
                    # accessible content. This is intentionally a soft
                    # preference rather than a rejection rule.
                    early_capacity = sum(
                        level_capacity[level_name]
                        for level_name in era_levels
                        if unlocks(candidate[level_name], 15, 0)
                    )

                    if early_capacity < 3:
                        score += 8.0
                    elif early_capacity < 10:
                        score += 2.0

                return score

            def assignment_variation(candidate):
                # Prevent the optimizer from repeatedly producing a nearly
                # vanilla-looking ladder. This is a small bonus for mixing
                # cheap and expensive requirements across different-sized
                # levels, while the capacity curve remains dominant.
                levels = list(candidate.items())
                variation = 0.0

                for i, (level_name, reqs) in enumerate(levels):
                    clocks, carrots = requirement_pair(reqs)
                    capacity = level_capacity[level_name]

                    difficulty = (clocks / 124.0) + (carrots / 333.0)

                    # Favor some variation between level size and requirement
                    # difficulty, but do not let this overpower fill safety.
                    expected = min(capacity / 52.0, 1.0)
                    variation += abs(difficulty - (1.0 - expected)) * 0.10

                return variation

            best_requirements = None
            best_score = None

            # We sample a large number of permutations, but only use scoring;
            # there is deliberately no "couldn't find a valid layout" error.
            attempts = 25000

            for _ in range(attempts):
                shuffled = [list(reqs) for reqs in requirement_sets]
                self.random.shuffle(shuffled)

                candidate = {
                    level_name: reqs
                    for level_name, reqs
                    in zip(level_names, shuffled)
                }

                score = curve_score(candidate)
                score += bottleneck_penalty(candidate)
                score += era_penalty(candidate)
                score += assignment_variation(candidate)

                # Tiny random tie-breaker. The capacity curve remains the
                # overwhelmingly dominant factor.
                score += self.random.random() * 0.02

                if best_score is None or score < best_score:
                    best_score = score
                    best_requirements = candidate

            requirements = best_requirements

        # Super Jump is permanently required for Follow the Red Pirate Road.
        # It is never randomized away from this level.
        requirements["Follow the Red Pirate Road"] = [
            requirement
            for requirement in requirements["Follow the Red Pirate Road"]
            if requirement.item != "Magic: Super Jump"
        ]

        requirements["Follow the Red Pirate Road"].append(
            LevelRequirement("Magic: Super Jump")
        )

        print("=== LEVEL REQUIREMENTS ===")

        for level_name, reqs in requirements.items():
            print(
                f"{level_name}: "
                + ", ".join(
                    f"{r.item} x{r.amount}"
                    if r.item in ("Clock", "Golden Carrot")
                    else r.item
                    for r in reqs
                )
            )

        return requirements

    # DEATHLINK

    def fill_slot_data(self):
        return {
            "goal": self.options.goal.value,

            "level_requirements": {
                level_name: [
                    {
                        "item": requirement.item,
                        "amount": requirement.amount,
                    }
                    for requirement in requirements
                ]
                for level_name, requirements 
                in self.level_requirements.items()
            },

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
