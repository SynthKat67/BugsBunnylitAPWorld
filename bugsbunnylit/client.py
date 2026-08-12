from worlds._bizhawk.client import BizHawkClient
import worlds._bizhawk as bizhawk

from .Items import item_table
from .Locations import (
    location_name_to_id,
    magic_flags,
    HubCarrots,
    counter_groups,
)

SYSTEM_BUS = "System Bus"

# Key bit is controlled entirely by the vanilla game.
KEY_FLAG = 0x80


# ----------------------------------------------------------------
# Global counter addresses
# ----------------------------------------------------------------

TOTAL_CLOCK_ADDRESS = 0x010045
TOTAL_GOLDEN_CARROT_ADDRESS = 0x010047
TOTAL_GOLDEN_CARROT_OVERFLOW_ADDRESS = 0x01013C

# ----------------------------------------------------------------
# DeathLink / health addresses
# ----------------------------------------------------------------

HEALTH_ADDRESS = 0x010041
DEAD_HEALTH = 0

STAGE_ID_ADDRESS = 0x0100F6
REGION_ID_ADDRESS = 0x010000
MAIN_MENU_STATE = 0x0000
MAIN_MENU_REGION = 0x00

PAUSE_DEATHLINK_VALUE = 0x0F63

# ----------------------------------------------------------------
# AP-controlled Magic address
# ----------------------------------------------------------------

MAGIC_ADDRESS = 0x010048

# ----------------------------------------------------------------
# Item names
# ----------------------------------------------------------------

CLOCK = "Clock"
GOLDEN_CARROT = "Golden Carrot"


class BugsBunnyLiTClient(BizHawkClient):

    game = "Bugs Bunny Lost in Time"
    system = "PSX"
    patch_suffix = None

    def __init__(self):
        super().__init__()


        # --------------------------------------------------------
        # DeathLink state
        # --------------------------------------------------------

        self.death_link_pending = False

        self.death_link_death = False

        self.death_link_enabled = False

        self.was_dead = False

        # --------------------------------------------------------
        # AP-controlled globals
        # --------------------------------------------------------

        self.global_clock = 0

        self.global_golden_carrot = 0

        self.global_golden_carrot_overflow = 0

        self.global_magic = 0

        self.globals_initialized = False

        # Number of AP received items already processed.
        self.processed_items = 0

        # --------------------------------------------------------
        # Clock protection for Nowhere
        # --------------------------------------------------------

        # AP Clock items received before the first Nowhere check.
        self.pending_clocks = 0

        self.nowhere_unlocked = False

        self.nowhere_location_ids = {
            location_id
            for location_name, location_id in location_name_to_id.items()
            if location_name.startswith("Nowhere:")
        }

    # ============================================================
    # DeathLink packet handling
    # ============================================================

    def on_package(self, ctx, cmd, args):

        if cmd != "Bounced":
            return

        if "tags" not in args:
            return

        if "DeathLink" not in args["tags"]:
            return

        data = args.get("data", {})

        source = data.get(
            "source",
            "Unknown",
        )

        if ctx.slot is not None:

            our_name = ctx.slot_info[ctx.slot].name

            if source == our_name:
                return

        self.death_link_pending = True

        cause = data.get(
            "cause",
            "",
        )

        if cause:

            print(
                "[Bugs Bunny Lost in Time] "
                f"DeathLink received from {source}: {cause}"
            )

        else:

            print(
                "[Bugs Bunny Lost in Time] "
                f"DeathLink received from {source}"
            )

    # ============================================================
    # Apply incoming DeathLink to the game
    # ============================================================

    async def process_death_link(self, ctx):

        if not self.death_link_pending:
            return

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (
                    STAGE_ID_ADDRESS,
                    2,
                    SYSTEM_BUS,
                ),
            ],
        )

        current_level = int.from_bytes(
            values[0],
            byteorder="little",
        )

        deathlink_disabled = (
            current_level == PAUSE_DEATHLINK_VALUE
        )

        # DeathLink is disabled in this level/state.
        if deathlink_disabled:

            print(
                "[Bugs Bunny Lost in Time] "
                "Deathlink sent but Bugs has a seatbelt on! "
                f"Protected level: 0x{current_level:04X}"
            )

            self.death_link_pending = False

            return

        print(
            "[Bugs Bunny Lost in Time] "
            "DeathLink: Wabbit Season!"
        )

        # Mark this death as DeathLink-caused so check_death()
        # does not send another DeathLink.
        self.death_link_death = True

        await bizhawk.write(
            ctx.bizhawk_ctx,
            [
                (
                    HEALTH_ADDRESS,
                    [DEAD_HEALTH],
                    SYSTEM_BUS,
                ),
            ],
        )

        print(
            "[Bugs Bunny Lost in Time] "
            "DeathLink health write completed."
        )

        self.death_link_pending = False

    # ============================================================
    # Detect natural death
    # ============================================================

    async def check_death(self, ctx):

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (
                    HEALTH_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    STAGE_ID_ADDRESS,
                    2,
                    SYSTEM_BUS,
                ),
            ],
        )

        current_health = values[0][0]

        current_level = int.from_bytes(
            values[1],
            byteorder="little",
        )

        is_dead = current_health == DEAD_HEALTH

        deathlink_disabled = (
            current_level == PAUSE_DEATHLINK_VALUE
        )

        # Detect alive -> dead transition.

        if is_dead and not self.was_dead:

            # Death caused by incoming DeathLink.

            if self.death_link_death:

                print(
                    "[Bugs Bunny Lost in Time] "
                    "DeathLink death detected."
                )

                self.death_link_death = False

            # Normal in-game death.

            elif "DeathLink" in ctx.tags:

                if deathlink_disabled:

                    print(
                        "[Bugs Bunny Lost in Time] "
                        "No Bunnies Were Harmed in This Level "
                        f"0x{current_level:02X}."
                    )

                else:

                    print(
                        "[Bugs Bunny Lost in Time] "
                        "Yikes! Bugs died! - sending DeathLink."
                    )

                    await ctx.send_death(
                        "Bugs Bunny died."
                    )

                    print(
                        "[Bugs Bunny Lost in Time] "
                        "DeathLink sent."
                    )

        self.was_dead = is_dead

    # ============================================================
    # ROM validation
    # ============================================================

    async def validate_rom(self, ctx):

        try:
            values = await bizhawk.read(
                ctx.bizhawk_ctx,
                [
                    (
                        STAGE_ID_ADDRESS,
                        2,
                        SYSTEM_BUS,
                    ),
                    (
                        REGION_ID_ADDRESS,
                        1,
                        SYSTEM_BUS,
                    ),
                ],
            )
        except bizhawk.RequestFailedError:
            return False

        state_id = int.from_bytes(
            values[0],
            byteorder="little",
        )

        region_id = values[1][0]

        # --------------------------------------------------------
        # Do not recognize the game until the main menu is active.
        # --------------------------------------------------------

        if (
            state_id != MAIN_MENU_STATE
            or region_id != MAIN_MENU_REGION
        ):
            return False

        ctx.game = self.game

        ctx.items_handling = 0b011

        ctx.want_slot_data = True

        return True

    # ============================================================
    # Slot data
    # ============================================================

    def fill_slot_data(self):

        return {
            "goal": self.options.goal.value,
            "death_link": self.options.death_link.value,
        }

    # ============================================================
    # Golden Carrot handling
    # ============================================================

    def add_golden_carrot(self):

        if self.global_golden_carrot >= 255:

            self.global_golden_carrot = 0

            self.global_golden_carrot_overflow = (
                self.global_golden_carrot_overflow + 1
            ) & 0xFF

        else:

            self.global_golden_carrot += 1

    # ============================================================
    # Item ID -> item name
    # ============================================================

    def get_item_name(self, item_id):

        for name, code in item_table.items():

            if code == item_id:
                return name

        return None

    # ============================================================
    # Initialize AP-controlled globals
    # ============================================================

    async def initialize_globals(self, ctx):

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (
                    TOTAL_CLOCK_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    TOTAL_GOLDEN_CARROT_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    TOTAL_GOLDEN_CARROT_OVERFLOW_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    HEALTH_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
            ],
        )

        self.global_clock = values[0][0]

        self.global_golden_carrot = values[1][0]

        self.global_golden_carrot_overflow = values[2][0]

        # Magic is entirely AP-controlled.
        #
        # The key bit is deliberately NOT initialized here.
        self.global_magic = 0

        self.was_dead = (
            values[3][0] == DEAD_HEALTH
        )

        self.globals_initialized = True

        print(
            "[Bugs Bunny Lost in Time] "
            "Globals initialized: "
            f"clock={self.global_clock:02X}, "
            f"golden carrot={self.global_golden_carrot:02X}, "
            f"overflow={self.global_golden_carrot_overflow:02X}"
        )

    # ============================================================
    # Apply an AP item to our AP-controlled state
    # ============================================================

    def give_item(self, item_name, ctx):

    # --------------------------------------------------------
    # Clock
    # --------------------------------------------------------

        if item_name == CLOCK:

            # AP clocks received before the player has made
            # a Nowhere check are held back.
            #
            # This keeps the game at 0 clocks while entering
            # Nowhere.

            if not self.nowhere_unlocked:

                self.pending_clocks += 1

                print(
                    "[Bugs Bunny Lost in Time] "
                    f"Holding AP Clock. "
                    f"Pending clocks: {self.pending_clocks}"
                )

                return True

            # Nowhere has been checked.
            # Give the clock normally.

            old_value = self.global_clock

            self.global_clock = (
                self.global_clock + 1
            ) & 0xFF

            print(
                "[Bugs Bunny Lost in Time] "
                f"Clock global: "
                f"{old_value:02X} -> "
                f"{self.global_clock:02X}"
            )

            return True

        # --------------------------------------------------------
        # Golden Carrot
        # --------------------------------------------------------

        if item_name == GOLDEN_CARROT:

            old_golden_carrot = self.global_golden_carrot
            old_golden_overflow = (
                self.global_golden_carrot_overflow
            )

            self.add_golden_carrot()

            print(
                "[Bugs Bunny Lost in Time] "
                f"Golden Carrot global: "
                f"{old_golden_overflow:02X}:"
                f"{old_golden_carrot:02X} -> "
                f"{self.global_golden_carrot_overflow:02X}:"
                f"{self.global_golden_carrot:02X}"
            )

            return True

        # --------------------------------------------------------
        # Magic
        # --------------------------------------------------------

        if item_name in magic_flags:

            magic = magic_flags[item_name]

            old_magic = self.global_magic

            self.global_magic |= magic.flag

            print(
                "[Bugs Bunny Lost in Time] "
                f"Magic global: "
                f"{old_magic:02X} -> "
                f"{self.global_magic:02X}"
            )

            return True

        # --------------------------------------------------------
        # Unknown item
        # --------------------------------------------------------

        print(
            "[Bugs Bunny Lost in Time] "
            f"give_item() does not recognize: "
            f"{item_name!r}"
        )

        return False

    # ============================================================
    # Write AP-controlled game state
    # ============================================================

    async def write_game_state(self, ctx):

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (
                    MAGIC_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
            ],
        )

        current_magic = values[0][0]

        # Preserve vanilla key bit.
        magic_to_write = (
            self.global_magic & ~KEY_FLAG
        ) | (
            current_magic & KEY_FLAG
        )

        await bizhawk.write(
            ctx.bizhawk_ctx,
            [
                (
                    TOTAL_CLOCK_ADDRESS,
                    [self.global_clock],
                    SYSTEM_BUS,
                ),
                (
                    TOTAL_GOLDEN_CARROT_ADDRESS,
                    [self.global_golden_carrot],
                    SYSTEM_BUS,
                ),
                (
                    TOTAL_GOLDEN_CARROT_OVERFLOW_ADDRESS,
                    [self.global_golden_carrot_overflow],
                    SYSTEM_BUS,
                ),
                (
                    MAGIC_ADDRESS,
                    [magic_to_write],
                    SYSTEM_BUS,
                ),
            ],
        )

    # ============================================================
    # Handle AP received items
    # ============================================================

    async def handle_received_items(self, ctx):

        if self.processed_items >= len(ctx.items_received):
            return

        while self.processed_items < len(ctx.items_received):

            network_item = ctx.items_received[
                self.processed_items
            ]

            item_name = self.get_item_name(
                network_item.item
            )

            print(
                "[Bugs Bunny Lost in Time] "
                f"Received item: {item_name}"
            )

            if not self.give_item(
                item_name,
                ctx,
            ):

                print(
                    "[Bugs Bunny Lost in Time] "
                    f"Unknown AP item ID: "
                    f"{network_item.item}"
                )

            self.processed_items += 1

    # ============================================================
    # Release Clock items held for Nowhere
    # ============================================================

    async def release_pending_clocks(self, ctx):

        # Don't release anything until the player has actually
        # checked at least one Nowhere location.

        if not self.nowhere_unlocked:

            if self.nowhere_location_ids & ctx.locations_checked:

                self.nowhere_unlocked = True

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Nowhere check confirmed by AP."
                )

        # Nothing waiting.
        if self.pending_clocks <= 0:
            return

        if not self.nowhere_unlocked:
            return

        count = self.pending_clocks

        old_value = self.global_clock

        self.global_clock = (
            self.global_clock + count
        ) & 0xFF

        self.pending_clocks = 0

        print(
            "[Bugs Bunny Lost in Time] "
            f"Released {count} pending AP Clock(s): "
            f"{old_value:02X} -> "
            f"{self.global_clock:02X}"
        )

    # ============================================================
    # Freeze AP-controlled global values
    # ============================================================

    async def freeze_globals(self, ctx):

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (
                    TOTAL_CLOCK_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    TOTAL_GOLDEN_CARROT_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    TOTAL_GOLDEN_CARROT_OVERFLOW_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    MAGIC_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
            ],
        )

        current_clock = values[0][0]

        current_golden_carrot = values[1][0]

        current_golden_overflow = values[2][0]

        current_magic = values[3][0]

        writes = []

        # --------------------------------------------------------
        # Clock
        # --------------------------------------------------------

        if current_clock != self.global_clock:

            writes.append(
                (
                    TOTAL_CLOCK_ADDRESS,
                    [self.global_clock],
                    SYSTEM_BUS,
                )
            )

        # --------------------------------------------------------
        # Golden Carrots
        # --------------------------------------------------------

        if (
            current_golden_carrot
            != self.global_golden_carrot
        ):

            writes.append(
                (
                    TOTAL_GOLDEN_CARROT_ADDRESS,
                    [self.global_golden_carrot],
                    SYSTEM_BUS,
                )
            )

        # --------------------------------------------------------
        # Golden Carrot overflow
        # --------------------------------------------------------

        if (
            current_golden_overflow
            != self.global_golden_carrot_overflow
        ):

            writes.append(
                (
                    TOTAL_GOLDEN_CARROT_OVERFLOW_ADDRESS,
                    [self.global_golden_carrot_overflow],
                    SYSTEM_BUS,
                )
            )

        # --------------------------------------------------------
        # Magic
        # --------------------------------------------------------

        magic_to_write = (
            self.global_magic & ~KEY_FLAG
        ) | (
            current_magic & KEY_FLAG
        )

        if current_magic != magic_to_write:

            writes.append(
                (
                    MAGIC_ADDRESS,
                    [magic_to_write],
                    SYSTEM_BUS,
                )
            )

        if writes:

            await bizhawk.write(
                ctx.bizhawk_ctx,
                writes,
            )

    # ============================================================
    # Check flag-based locations
    # ============================================================

    async def check_flag_locations(self, ctx):

        flag_groups = {}

        # --------------------------------------------------------
        # Magic locations
        # --------------------------------------------------------

        for name, group in magic_flags.items():

            flag_groups.setdefault(
                group.address,
                [],
            ).append(
                (name, group)
            )

        # --------------------------------------------------------
        # Hub Carrot purchase locations
        # --------------------------------------------------------

        for name, group in HubCarrots.items():

            flag_groups.setdefault(
                group.address,
                [],
            ).append(
                (name, group)
            )

        # --------------------------------------------------------
        # Read each unique flag byte only once.
        # --------------------------------------------------------

        reads = [
            (
                address,
                1,
                SYSTEM_BUS,
            )
            for address in flag_groups
        ]

        if not reads:
            return

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            reads,
        )

        locations_to_check = []

        # --------------------------------------------------------
        # Compare returned byte against individual flags.
        # --------------------------------------------------------

        for address, value in zip(
            flag_groups,
            values,
        ):

            current_flags = value[0]

            for location_name, group in flag_groups[address]:

                if current_flags & group.flag:

                    location_id = (
                        location_name_to_id[
                            location_name
                        ]
                    )

                    if (
                        location_id
                        not in ctx.locations_checked
                    ):

                        locations_to_check.append(
                            location_id
                        )

        # --------------------------------------------------------
        # Send newly discovered flag locations.
        # --------------------------------------------------------

        if locations_to_check:

            await ctx.check_locations(
                locations_to_check
            )

    # ============================================================
    # Main watcher
    # ============================================================

    async def game_watcher(self, ctx):

        # --------------------------------------------------------
        # DeathLink setup
        # --------------------------------------------------------

        if ctx.slot_data is not None:

            death_link_enabled = bool(
                ctx.slot_data.get(
                    "death_link",
                    False,
                )
            )

            if (
                death_link_enabled
                != self.death_link_enabled
            ):

                await ctx.update_death_link(
                    death_link_enabled
                )

                self.death_link_enabled = (
                    death_link_enabled
                )

                if death_link_enabled:

                    print(
                        "[Bugs Bunny Lost in Time] "
                        "DeathLink ENABLED."
                    )

                else:

                    print(
                        "[Bugs Bunny Lost in Time] "
                        "DeathLink DISABLED."
                    )

        # --------------------------------------------------------
        # Counter-based locations
        # --------------------------------------------------------

        reads = []

        for name, group in counter_groups.items():

            reads.append(
                (
                    group.address,
                    1,
                    SYSTEM_BUS,
                )
            )

        if reads:

            values = await bizhawk.read(
                ctx.bizhawk_ctx,
                reads,
            )

        else:

            values = []

        locations_to_check = []

        # --------------------------------------------------------
        # Match each returned value to its counter group.
        # --------------------------------------------------------

        for (name, group), value in zip(
            counter_groups.items(),
            values,
        ):

            count = value[0]

            count = min(
                count,
                group.max_count,
            )

            for i in range(1, count + 1):

                location_name = (
                    f"{name} - {i}"
                )

                location_id = (
                    location_name_to_id[
                        location_name
                    ]
                )

                if (
                    location_id
                    not in ctx.locations_checked
                ):

                    locations_to_check.append(
                        location_id
                    )

        # --------------------------------------------------------
        # Send newly discovered counter locations.
        # --------------------------------------------------------

        if locations_to_check:

            # Check whether any of the locations we just detected
            # belong to Nowhere.
            #
            # We set nowhere_unlocked BEFORE calling
            # ctx.check_locations(), because ctx.locations_checked
            # may not update until a later network cycle.

            nowhere_found = bool(
                self.nowhere_location_ids
                & set(locations_to_check)
            )

            if nowhere_found and not self.nowhere_unlocked:

                self.nowhere_unlocked = True

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Nowhere unlocked! "
                    "Pending AP clocks can now be released."
                )

            # Always send the locations to AP, regardless of
            # whether they are Nowhere locations.
            await ctx.check_locations(
                locations_to_check
            )

        # --------------------------------------------------------
        # Flag-based locations
        # --------------------------------------------------------

        await self.check_flag_locations(ctx)

       
        # --------------------------------------------------------
        # Initialize globals
        # --------------------------------------------------------

        if not self.globals_initialized:

            await self.initialize_globals(ctx)

            return

        # --------------------------------------------------------
        # Release AP clocks after the first Nowhere check.
        # --------------------------------------------------------

        await self.release_pending_clocks(ctx)

        # --------------------------------------------------------
        # Process AP received items
        # --------------------------------------------------------

        await self.handle_received_items(ctx)

        
        # --------------------------------------------------------
        # Keep AP-controlled values frozen.
        # --------------------------------------------------------

        await self.freeze_globals(ctx)

        # --------------------------------------------------------
        # DeathLink
        # --------------------------------------------------------

        await self.process_death_link(ctx)

        await self.check_death(ctx)