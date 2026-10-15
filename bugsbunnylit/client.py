from worlds._bizhawk.client import BizHawkClient
import worlds._bizhawk as bizhawk
from NetUtils import ClientStatus

from .Items import item_table
from .Locations import (
    location_name_to_id,
    magic_flags,
    magic_locations,
    HubCarrots,
    counter_groups,
    level_entries,
    PLAYER_Y_ADDRESS,
    PLAYER_X_ADDRESS,
    LevelRequirement,
)


SYSTEM_BUS = "System Bus"


# ================================================================
# Vanilla game state
# ================================================================

KEY_FLAG = 0x80

STAGE_ID_ADDRESS = 0x0100F6
REGION_ID_ADDRESS = 0x010000

HUB_SELECT_ADDRESS = 0x0BB314
HUB_SELECT_VALUE = 0x9C
HUB_SELECT_CLOCK_VALUE = 100

MOVEMENT_ADDRESS = 0x0BB5F8
MOVEMENT_STATIONARY_VALUE = (
    (0x02),
    (0x01),
    )

MAIN_MENU_HUB_ENTRY_REGION = 0x00
NEW_GAME_CUTSCENE_REGION = 0x38
NOWHERE_REGION = 0x33

LEVEL_STAGE_VALUES = (
    (0x0AB5),
    (0x1654),
    (0x0555), 
    (0x115B),
    (0x0F5F),
    (0x2557),
    (0x095E),
    (0x025C),
    (0x00EB),
    (0x1A64),
    (0x0F63),
    (0x05F8),
    (0x0066),
    (0x0858),
    (0x0E65),
    (0x1459),
    (0x1F56),
    (0x0F61),
    (0x295D),
    (0x15E4),
    (0x00EB),
    (0x0F60),
)

MAIN_MENU_STATE = 0x0000
MAIN_MENU_REGION = 0x00
CREDITS_REGION = 0x47
# Region 3 = normal active hub/save state.
SAVE_LOADED_REGION = 0x03


# ================================================================
# Global game addresses
# ================================================================

TOTAL_CLOCK_ADDRESS = 0x010045
TOTAL_GOLDEN_CARROT_ADDRESS = 0x010047
TOTAL_GOLDEN_CARROT_OVERFLOW_ADDRESS = 0x01013C

MAGIC_ADDRESS = 0x010048


# ================================================================
# DeathLink / health
# ================================================================

HEALTH_ADDRESS = 0x010041
DEAD_HEALTH = 0

PAUSE_DEATHLINK_VALUE = (
    (0x0F63),
    (0x0004),
)

# ================================================================
# Item names
# ================================================================

CLOCK = "Clock"
GOLDEN_CARROT = "Golden Carrot"

MERLIN_ADDRESS = 0x010133
MERLIN_VALUE = 0x0002FFFF

class BugsBunnyLiTClient(BizHawkClient):

    game = "Bugs Bunny Lost in Time"
    system = "PSX"
    patch_suffix = None

    def __init__(self):
        super().__init__()
        
        # ========================================================
        # Cooldown to prevent level re-entry loops on exit
        # ========================================================
        self.hub_transit_cooldown = 0

        # ========================================================
        # Main menu / save state
        # ========================================================

        self.previous_region = None
        self.current_region = MAIN_MENU_REGION
        self.startup_region_confirmed = False
        self.awaiting_hub = True
        self.save_loaded = False
        self.gameplay_checks_enabled = False

        # ========================================================
        # Persistent location restoration
        # ========================================================

        self.locations_restored = False

        self.location_restore_pending = False

        self.location_restore_delay = 0

        # Number of watcher cycles to wait after region 3 appears.
        self.location_restore_delay_cycles = 10

        # Number of restoration attempts.
        self.location_restore_retry_count = 0

        # This is intentionally generous because the game can
        # rewrite level/save memory during the hub initialization.
        self.location_restore_max_retries = 120

        # Only becomes True after the expected counters have actually
        # been observed in RAM.
        self.location_restore_complete = False

        self.hub_entry_handled = False
        self.hub_entry_from_region = None

        self.hub_select_clock_delay_cycles = 1
        self.hub_select_clock_delay_remaining = 0
        self.was_hub_select_active = False

        # ========================================================
        # Level Unlock Requirements
        # ========================================================

        self.level_requirements = {}
        self.level_requirements_initialized = False
        self.gate_states = {}
        self.level_entry_previous_values = {}
        self.level_entry_stable_cycles = {}
        self.level_entry_write_delay = 3

        # ========================================================
        # DeathLink
        # ========================================================

        self.death_link_pending = False
        self.death_link_death = False
        self.death_link_enabled = False
        self.was_dead = False

        # ========================================================
        # AP-controlled globals
        #
        # These are authoritative AP state.
        #
        # We NEVER initialize these from game memory.
        # ========================================================

        self.global_clock = 0
        self.global_golden_carrot = 0
        self.global_golden_carrot_overflow = 0
        self.global_magic = 0

        self.globals_initialized = False

        # Number of received AP items already processed.
        self.processed_items = 0

        # ========================================================
        # Clock / Nowhere
        # ========================================================

        self.pending_clocks = 0

        # This is AP state.
        #
        # It intentionally survives a ROM reset.
        self.nowhere_unlocked = False

        self.nowhere_location_ids = {
            location_id
            for location_name, location_id
            in location_name_to_id.items()
            if location_name.startswith("Nowhere:")
        }



    async def manage_save_state(self, ctx):

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (
                    REGION_ID_ADDRESS,
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

        current_region = values[0][0]

        current_stage = int.from_bytes(
            values[1],
            byteorder="little",
        )

        self.current_region = current_region

        in_level_stage = (
            current_stage in LEVEL_STAGE_VALUES
        )

        # ========================================================
        # MAIN MENU
        #
        # Region 0 means gameplay is no longer active.
        # Disable location/gameplay interaction until the hub
        # is loaded again.
        # ========================================================

        if current_region == MAIN_MENU_REGION:

            if self.gameplay_checks_enabled:

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Main menu detected. "
                    "Disabling gameplay/location checks."
                )

            self.gameplay_checks_enabled = False
            self.save_loaded = False
            self.hub_save_delay_active = False
            self.hub_save_delay_cycles = 0
            self.location_restore_pending = False
            self.location_restore_complete = False
            self.locations_restored = False

            self.hub_entry_handled = False
            self.gate_states.clear()

        # ========================================================
        # HUB
        # ========================================================

        entered_hub = (
            current_region == SAVE_LOADED_REGION
            and self.previous_region != SAVE_LOADED_REGION
        )

        if entered_hub:

            self.gate_states.clear()
            
            self.hub_entry_from_region = self.previous_region
            
            self.hub_transit_cooldown = 20 

            excluded_hub_entry = (
                self.previous_region == MAIN_MENU_HUB_ENTRY_REGION
                or self.previous_region == NOWHERE_REGION
                or self.previous_region == NEW_GAME_CUTSCENE_REGION
            )

            

            await bizhawk.write(
                ctx.bizhawk_ctx,
                [
                    (
                        MERLIN_ADDRESS,
                        list(
                            MERLIN_VALUE.to_bytes(
                                4,
                                byteorder="little",
                            )
                        ),
                        SYSTEM_BUS,
                    ),
                ],
            )

           
            self.startup_region_confirmed = True
            self.save_loaded = True

            # Re-enable gameplay/location processing.
            self.gameplay_checks_enabled = True

            self.locations_restored = False
            self.location_restore_complete = False
            self.location_restore_pending = True

            self.location_restore_delay = (
                self.location_restore_delay_cycles
            )

            self.location_restore_retry_count = 0


        if current_region == SAVE_LOADED_REGION:

            self.awaiting_hub = False
            self.save_loaded = True
            self.gameplay_checks_enabled = True

        if current_stage in LEVEL_STAGE_VALUES:
            self.gameplay_checks_enabled = True

        # ========================================================
        # PERSISTENT LOCATION RESTORATION
        # ========================================================

        if (
            self.gameplay_checks_enabled
            and self.save_loaded
            and self.location_restore_pending
            and not self.location_restore_complete
        ):

            if self.location_restore_delay > 0:

                self.location_restore_delay -= 1

            else:

                restored = await self.restore_location_progress(ctx)

                if restored:

                    self.location_restore_complete = True
                    self.locations_restored = True
                    self.location_restore_pending = False

                    print(
                        "[Bugs Bunny Lost in Time] "
                        "All AP location progress successfully "
                        "restored and verified."
                    )

                else:

                    self.location_restore_retry_count += 1

                    if (
                        self.location_restore_retry_count
                        >= self.location_restore_max_retries
                    ):

                        print(
                            "[Bugs Bunny Lost in Time] "
                            "WARNING: Location restoration did not "
                            "complete after "
                            f"{self.location_restore_max_retries} "
                            "attempts. Restarting retry counter."
                        )

                        self.location_restore_retry_count = 0

                    else:

                        print(
                            "[Bugs Bunny Lost in Time] "
                            "Location restoration not yet stable. "
                            "Retry "
                            f"{self.location_restore_retry_count}/"
                            f"{self.location_restore_max_retries}"
                        )

    
        self.previous_region = current_region

        return False

    async def restore_location_progress(self, ctx):

        checked_locations = set(ctx.locations_checked)

        if not checked_locations:

            print(
                "[Bugs Bunny Lost in Time] "
                "No previously checked locations to restore."
            )

            return True

        # ========================================================
        # Determine expected counter values from AP
        # ========================================================

        expected_counters = {}

        for name, group in counter_groups.items():

            highest_checked = 0

            for i in range(
                1,
                group.max_count + 1,
            ):

                location_name = f"{name} - {i}"

                location_id = location_name_to_id.get(
                    location_name
                )

                if location_id is None:
                    continue

                if location_id in checked_locations:

                    highest_checked = max(
                        highest_checked,
                        i,
                    )

            if highest_checked > 0:

                expected_counters[name] = (
                    group,
                    highest_checked,
                )

        # ========================================================
        # READ CURRENT COUNTERS
        # ========================================================

        counter_reads = []
        counter_read_info = []

        for name, (group, expected) in expected_counters.items():

            counter_reads.append(
                (
                    group.address,
                    1,
                    SYSTEM_BUS,
                )
            )

            counter_read_info.append(
                (
                    name,
                    group,
                    expected,
                )
            )

        current_counters = {}

        if counter_reads:

            values = await bizhawk.read(
                ctx.bizhawk_ctx,
                counter_reads,
            )

            for (
                (name, group, expected),
                value,
            ) in zip(
                counter_read_info,
                values,
            ):

                current = value[0]

                current_counters[name] = current

        # ========================================================
        # WRITE COUNTERS
        # ========================================================

        counter_writes = []

        for name, (group, expected) in expected_counters.items():

            current = current_counters.get(
                name,
                0,
            )

            if current != expected:

                counter_writes.append(
                    (
                        group.address,
                        [expected],
                        SYSTEM_BUS,
                    )
                )

                print(
                    "[Bugs Bunny Lost in Time] "
                    "COUNTER WRITE: "
                    f"{name}: {current} -> {expected} "
                    f"at 0x{group.address:06X}"
                )

            else:

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Counter already correct: "
                    f"{name} = {current} "
                    f"at 0x{group.address:06X}"
                )

        # ========================================================
        # FLAG LOCATIONS
        # ========================================================

        flag_groups = {}

        for name, group in magic_flags.items():

            flag_groups.setdefault(
                group.address,
                [],
            ).append(
                (name, group)
            )

        for name, group in HubCarrots.items():

            flag_groups.setdefault(
                group.address,
                [],
            ).append(
                (name, group)
            )

        flag_writes = []

        if flag_groups:

            flag_reads = [
                (
                    address,
                    1,
                    SYSTEM_BUS,
                )
                for address in flag_groups
            ]

            flag_values = await bizhawk.read(
                ctx.bizhawk_ctx,
                flag_reads,
            )

            for address, value in zip(
                flag_groups,
                flag_values,
            ):

                current_flags = value[0]
                restored_flags = current_flags

                for location_name, group in flag_groups[address]:

                    location_id = location_name_to_id.get(
                        location_name
                    )

                    if (
                        location_id is not None
                        and location_id in checked_locations
                    ):

                        if not (restored_flags & group.flag):

                            print(
                                "[Bugs Bunny Lost in Time] "
                                "FLAG WRITE: "
                                f"{location_name} "
                                f"at 0x{address:06X}"
                            )

                        restored_flags |= group.flag

                if restored_flags != current_flags:

                    flag_writes.append(
                        (
                            address,
                            [restored_flags],
                            SYSTEM_BUS,
                        )
                    )

        # ========================================================
        # PERFORM WRITES
        # ========================================================

        writes = counter_writes + flag_writes

        if writes:

            print(
                "[Bugs Bunny Lost in Time] "
                f"Writing {len(writes)} location-state value(s)."
            )

            await bizhawk.write(
                ctx.bizhawk_ctx,
                writes,
            )

        # ========================================================
        # VERIFY COUNTERS
        # ========================================================

        all_counters_correct = True
        all_flags_correct = True

        if counter_reads:

            verify_counter_values = await bizhawk.read(
                ctx.bizhawk_ctx,
                counter_reads,
            )

            for (
                (name, group, expected),
                value,
            ) in zip(
                counter_read_info,
                verify_counter_values,
            ):

                actual = value[0]

                if actual != expected:

                    all_counters_correct = False

                    print(
                        "[Bugs Bunny Lost in Time] "
                        f"COUNTER NOT STABLE: {name} "
                        f"expected {expected}, got {actual} "
                        f"at 0x{group.address:06X}"
                    )

                else:

                    print(
                        "[Bugs Bunny Lost in Time] "
                        f"COUNTER VERIFIED: {name} = {actual}"
                    )    

            

        if flag_groups:

            verify_flag_reads = [
                (
                    address,
                    1,
                    SYSTEM_BUS,
                )
                for address in flag_groups
            ]

            verify_flag_values = await bizhawk.read(
                ctx.bizhawk_ctx,
                verify_flag_reads,
            )

            for address, value in zip(
                flag_groups,
                verify_flag_values,
            ):

                actual_flags = value[0]

                for location_name, group in flag_groups[address]:

                    location_id = location_name_to_id.get(
                        location_name
                    )

                    if (
                        location_id is not None
                        and location_id in checked_locations
                    ):

                        if actual_flags & group.flag:

                            print(
                                "[Bugs Bunny Lost in Time] "
                                "FLAG VERIFIED: "
                                f"{location_name} "
                                f"at 0x{address:06X}"
                            )

                        else:

                            all_flags_correct = False

                            print(
                                "[Bugs Bunny Lost in Time] "
                                "FLAG NOT STABLE: "
                                f"{location_name} "
                                f"missing at 0x{address:06X}"
                            )

        if not all_counters_correct:
            return False


        if not all_flags_correct:
            return False

        # ========================================================
        # Everything currently matches AP state.
        # ========================================================

        return True

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

        data = args.get(
            "data",
            {},
        )

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
    # Apply incoming DeathLink
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
                (
                    REGION_ID_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
            ],
        )

        current_health = values[0][0]

        current_level = int.from_bytes(
            values[1],
            byteorder="little",
        )

        current_region = values[2][0]

        if current_region == MAIN_MENU_REGION:

            self.was_dead = False

            return

        is_dead = current_health == DEAD_HEALTH

        deathlink_disabled = (
            current_level == PAUSE_DEATHLINK_VALUE
        )

        if is_dead and not self.was_dead:

            if self.death_link_death:

                print(
                    "[Bugs Bunny Lost in Time] "
                    "DeathLink death detected."
                )

                self.death_link_death = False

            elif "DeathLink" in ctx.tags:

                if deathlink_disabled:

                    print(
                        "[Bugs Bunny Lost in Time] "
                        "No Bunnies Were Harmed In This Level "
                        f"0x{current_level:04X}."
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

        # Only the actual main menu validates the ROM.
        if (
            state_id != MAIN_MENU_STATE
            or region_id != MAIN_MENU_REGION
        ):

            return False

        print(
            "[Bugs Bunny Lost in Time] "
            "ROM validation successful."
        )

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

        self.global_clock = 0
        self.global_golden_carrot = 0
        self.global_golden_carrot_overflow = 0
        self.global_magic = 0

        # ========================================================
        # Reconstruct Nowhere from AP state BEFORE replaying items
        # ========================================================

        if self.nowhere_location_ids & ctx.locations_checked:

            if not self.nowhere_unlocked:

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Previously checked Nowhere location detected "
                    "after ROM restart. "
                    "Clock items are unlocked."
                )

            self.nowhere_unlocked = True

        self.globals_initialized = True

        print(
            "[Bugs Bunny Lost in Time] "
            "AP globals initialized locally: "
            f"clock={self.global_clock:02X}, "
            f"golden carrot={self.global_golden_carrot:02X}, "
            f"overflow={self.global_golden_carrot_overflow:02X}, "
            f"magic={self.global_magic:02X}"
        )

    # ============================================================
    # Apply AP item to AP-controlled state
    # ============================================================

    def give_item(self, item_name, ctx):

        # --------------------------------------------------------
        # Clock
        # --------------------------------------------------------

        if item_name == CLOCK:

            if not self.nowhere_unlocked:

                self.pending_clocks += 1

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Holding AP Clock. "
                    f"Pending clocks: {self.pending_clocks}"
                )

                return True

            old_value = self.global_clock

            self.global_clock = (
                self.global_clock + 1
            ) & 0xFF

            print(
                "[Bugs Bunny Lost in Time] "
                "Clock global: "
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
                "Golden Carrot global: "
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
                "Magic global: "
                f"{old_magic:02X} -> "
                f"{self.global_magic:02X}"
            )

            return True

        print(
            "[Bugs Bunny Lost in Time] "
            "give_item() does not recognize: "
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
                    "Unknown AP item ID: "
                    f"{network_item.item}"
                )

            self.processed_items += 1

    # ============================================================
    # Release Clock items held for Nowhere
    # ============================================================

    async def release_pending_clocks(self, ctx):

        # Confirm Nowhere from AP state.
        if not self.nowhere_unlocked:

            if self.nowhere_location_ids & ctx.locations_checked:

                self.nowhere_unlocked = True

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Nowhere check confirmed by AP."
                )

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
            f"{old_value:02X} -> {self.global_clock:02X}"
        )

    # ============================================================
    # Freeze AP-controlled globals
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
                (
                    REGION_ID_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    HUB_SELECT_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
            ],
        )

        current_clock = values[0][0]
        current_golden_carrot = values[1][0]
        current_golden_overflow = values[2][0]
        current_magic = values[3][0]
        current_region = values[4][0]
        current_hub_select = values[5][0]

        writes = []

        # --------------------------------------------------------
        # Clock
        # --------------------------------------------------------

        hub_select_active = (
            current_region == SAVE_LOADED_REGION
            and current_hub_select == HUB_SELECT_VALUE
        )

        if hub_select_active:

            self.was_hub_select_active = True
            self.hub_select_clock_delay_remaining = (
                self.hub_select_clock_delay_cycles
            )

            if (
                self.nowhere_unlocked
                and self.global_clock < 40
            ):
                clock_to_write = HUB_SELECT_CLOCK_VALUE

            else:
                clock_to_write = self.global_clock


            if current_clock != clock_to_write:

                print(
                    "[Bugs Bunny Lost in Time] "
                    "Hub select active: "
                    f"game clock {current_clock} -> "
                    f"{clock_to_write}. "
                    f"AP clock remains {self.global_clock}."
                )

                writes.append(
                    (
                        TOTAL_CLOCK_ADDRESS,
                        [clock_to_write],
                        SYSTEM_BUS,
                    )
                )

        else:

            if self.was_hub_select_active:

                self.was_hub_select_active = False

                self.hub_select_clock_delay_remaining = (
                    self.hub_select_clock_delay_cycles
                )

            if self.hub_select_clock_delay_remaining > 0:

                self.hub_select_clock_delay_remaining -= 1
            else:

                clock_to_write = self.global_clock

                if current_clock != clock_to_write:

                    writes.append(
                        (
                            TOTAL_CLOCK_ADDRESS,
                            [clock_to_write],
                            SYSTEM_BUS,
                        )
                    )

        # --------------------------------------------------------
        # Golden carrots
        # --------------------------------------------------------

        if current_golden_carrot != self.global_golden_carrot:

            writes.append(
                (
                    TOTAL_GOLDEN_CARROT_ADDRESS,
                    [self.global_golden_carrot],
                    SYSTEM_BUS,
                )
            )

        # --------------------------------------------------------
        # Golden carrot overflow
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
    # Level Unlocks
    # ============================================================

    def get_level_requirements(self, level_name, level):

        requirements = self.level_requirements.get(
            level_name
        )
    
        if requirements is not None:
            return requirements

        return level.requirements

    
    def load_level_requirements(self, ctx):

        self.level_requirements = {}

        if not ctx.slot_data:
            return False

        raw_requirements = ctx.slot_data.get(
            "level_requirements",
            {},
        )

        if not raw_requirements:
            print(
                "[Bugs Bunny Lost in Time] "
                "WARNING: No level_requirements found in slot data."
            )
            return False

        self.level_requirements = {}

        for level_name, requirements in raw_requirements.items():

            self.level_requirements[level_name] = [
                LevelRequirement(
                    item=requirement["item"],
                    amount=requirement["amount"],
                )
                for requirement in requirements
            ]

        print(
            "[Bugs Bunny Lost in Time] "
            f"Loaded requirements for "
            f"{len(self.level_requirements)} levels."
        )

        print(
            "[Bugs Bunny Lost in Time] "
            "=== CLIENT LEVEL REQUIREMENTS ==="
        )

        for level_name, requirements in self.level_requirements.items():

            print(
                f"[Bugs Bunny Lost in Time] "
                f"{level_name}: "
                + ", ".join(
                    f"{r.item} x{r.amount}"
                    if r.item in (CLOCK, GOLDEN_CARROT)
                    else r.item
                    for r in requirements
                )
            )

        return True

    def level_requirements_met(self, level_name, level):

        requirements = self.get_level_requirements(
            level_name,
            level,
        )

        for requirement in requirements:


            # --------------------------------------------------------
            # Clock
            # --------------------------------------------------------

            if requirement.item == CLOCK:

                if self.global_clock < requirement.amount:
                    return False

            # --------------------------------------------------------
            # Golden Carrot
            # --------------------------------------------------------

            elif requirement.item == GOLDEN_CARROT:

                total_carrots = (
                    self.global_golden_carrot
                    + (
                        self.global_golden_carrot_overflow
                        * 256
                    )
                )

                if total_carrots < requirement.amount:
                    return False

            # --------------------------------------------------------
            # Magic
            # --------------------------------------------------------

            elif requirement.item in magic_flags:

                required_magic = magic_flags[
                    requirement.item
                ].flag

                if not (
                    self.global_magic
                    & required_magic
                ):
                    return False

            # --------------------------------------------------------
            # Unknown requirement
            # --------------------------------------------------------

            else:

                print(
                    "[Bugs Bunny Lost in Time] "
                    f"Unknown level requirement: "
                    f"{requirement.item!r}"
                )

                return False

        return True

    # ============================================================
    # Hub Select Screen
    # ============================================================

    async def is_hub_select(self, ctx):

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (
                    REGION_ID_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
                (
                    HUB_SELECT_ADDRESS,
                    1,
                    SYSTEM_BUS,
                ),
            ],
        )

        current_region = values[0][0]
        hub_select_value = values[1][0]

        return (
            current_region == SAVE_LOADED_REGION
            and hub_select_value == HUB_SELECT_VALUE
        )

    # ============================================================
    # Maintain HUB level entries
    # ============================================================

    async def maintain_hub_levels(self, ctx):

        RED_PIRATE_ROAD_GATE_ADDRESS = 0x0DCDA8
        RED_PIRATE_ROAD_GATE_VALUE = 0xFF4F

        if self.current_region != SAVE_LOADED_REGION:
            return

        entry_addresses = set()
        for level in level_entries.values():
            for address, value in level.entries:
                entry_addresses.add(address)
            for address, value in level.closed_entries:
                entry_addresses.add(address)

        entry_reads = [
            (address, 2, SYSTEM_BUS)
            for address in entry_addresses
        ]

        entry_values = await bizhawk.read(
            ctx.bizhawk_ctx,
            entry_reads,
        )

        current_entries = {
            address: int.from_bytes(value, byteorder="little")
            for address, value in zip(entry_addresses, entry_values)
        }

        
        if self.hub_transit_cooldown > 0:
            self.hub_transit_cooldown -= 1

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            [
                (REGION_ID_ADDRESS, 1, SYSTEM_BUS),
                (HUB_SELECT_ADDRESS, 1, SYSTEM_BUS),
                (PLAYER_X_ADDRESS, 4, SYSTEM_BUS),
                (PLAYER_Y_ADDRESS, 2, SYSTEM_BUS),
            ],
        )

        current_region = values[0][0]
        hub_select_value = values[1][0]
        
        player_x = int.from_bytes(values[2], byteorder="little", signed=False)
        player_y = int.from_bytes(values[3], byteorder="little", signed=False)

        level_entries_active = (current_region == SAVE_LOADED_REGION and hub_select_value != HUB_SELECT_VALUE)

        if not level_entries_active:
            return

        stable_addresses = set()
        for address, current_value in current_entries.items():
            previous_value = self.level_entry_previous_values.get(address)

            if previous_value == current_value:
                self.level_entry_stable_cycles[address] = (
                    self.level_entry_stable_cycles.get(address, 0) + 1
                )
            else:
                self.level_entry_stable_cycles[address] = 0

            self.level_entry_previous_values[address] = current_value

            if self.level_entry_stable_cycles.get(address, 0) >= self.level_entry_write_delay:
                stable_addresses.add(address)

        writes = []
        if level_entries_active:
            for level_name, level in level_entries.items():
                requirements_met = self.level_requirements_met(level_name, level)

                # ========================================================
                # OPEN LEVEL (Requires Stability & Cooldown Safety)
                # ========================================================
                if requirements_met:

                    # Dimension X levels still respect the transit cooldown timer to protect the UFO logic
                    is_dimension_x_level = level_name in (
                        "the Planet X File!",
                        "the Conquest for Planet X!",
                        "Train Your Brain!"
                    )
                    
                    if self.hub_transit_cooldown > 0 and is_dimension_x_level:
                        for address, _ in level.entries + level.closed_entries:
                            self.level_entry_stable_cycles[address] = 0
                        continue

                    if level_name == "Follow the Red Pirate Road":
                        gate_value = await bizhawk.read(
                            ctx.bizhawk_ctx,
                            [(RED_PIRATE_ROAD_GATE_ADDRESS, 2, "System Bus")]
                        )
                        gate_value = int.from_bytes(gate_value[0], byteorder="little")

                        if gate_value != RED_PIRATE_ROAD_GATE_VALUE:
                            continue

                    for address, value in level.entries:
                        # Open levels MUST wait to be completely stable before writing
                        if address not in stable_addresses:
                            continue
                        current_value = current_entries.get(address)

                        if current_value in level.protected_values:
                            self.level_entry_stable_cycles[address] = 0
                            continue

                        if current_value != value:
                            writes.append((address, list(value.to_bytes(2, byteorder="little")), SYSTEM_BUS))

                # ========================================================
                # CLOSED LEVEL (100% Unrestricted Instant Overwrite)
                # ========================================================
                else:
                    for address, value in level.closed_entries:
                        current_value = current_entries.get(address)

                        if current_value in level.protected_values:
                            self.level_entry_stable_cycles[address] = 0
                            continue

                        if current_value != value:
                            writes.append((address, list(value.to_bytes(2, byteorder="little")), SYSTEM_BUS))

        if writes:
            await bizhawk.write(
                ctx.bizhawk_ctx,
                writes,
            )

        # ========================================================
        # PERSISTENT HUB GATES
        # ========================================================

        gate_writes = []
        if level_entries_active:
            for level_name, level in level_entries.items():
                if not level.conditional_entries:
                    continue

                read_instructions = [
                    (conditional.address, 2, SYSTEM_BUS) 
                    for conditional in level.conditional_entries
                ]
                live_bytes_list = await bizhawk.read(ctx.bizhawk_ctx, read_instructions)
                
                live_memory = {}
                for conditional, b_list in zip(level.conditional_entries, live_bytes_list):
                    live_memory[conditional.address] = int.from_bytes(bytes(b_list), byteorder="little")

                for conditional in level.conditional_entries:
                    gate = conditional.gate
                    current_live_value = live_memory.get(conditional.address)

                    inside_x_range = (gate.x_min <= player_x <= gate.x_max)
                    inside_y_range = (gate.y_min <= player_y <= gate.y_max)
                    inside_gate_region = (inside_x_range and inside_y_range)

                    should_be_open = inside_gate_region
                    target_value = conditional.open_value if should_be_open else conditional.closed_value

                    if current_live_value != target_value:
                        gate_writes.append(
                            (
                                conditional.address,
                                list(target_value.to_bytes(2, byteorder="little")),
                                SYSTEM_BUS,
                            )
                        )
                        self.gate_states[conditional.address] = should_be_open

            if gate_writes:
                await bizhawk.write(ctx.bizhawk_ctx, gate_writes)

    # ============================================================
    # Check flag-based locations
    # ============================================================

    async def check_flag_locations(self, ctx):

        flag_groups = {}

        # --------------------------------------------------------
        # Hub carrots
        # --------------------------------------------------------

        for name, group in HubCarrots.items():

            flag_groups.setdefault(
                group.address,
                [],
            ).append(
                (name, group)
            )

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

        for address, value in zip(
            flag_groups,
            values,
        ):

            current_flags = value[0]

            for location_name, group in flag_groups[address]:

                if current_flags & group.flag:

                    location_id = location_name_to_id.get(
                        location_name
                    )

                    if (
                        location_id is not None
                        and location_id not in ctx.locations_checked
                    ):

                        locations_to_check.append(
                            location_id
                        )

        if locations_to_check:

            await ctx.check_locations(
                locations_to_check
            )

    async def check_magic_locations(self, ctx):

        if not magic_locations:
            return

        reads = [
            (
                REGION_ID_ADDRESS,
                1,
                SYSTEM_BUS,
            ),
            (
                0x069450,
                1,
                SYSTEM_BUS,
            ),
        
        ]

        values = await bizhawk.read(
            ctx.bizhawk_ctx,
            reads,
        )

        current_region = values [0][0]
        current_value = values [1][0]

        locations_to_check = []

        for location_name, location in magic_locations.items():

            if current_region != location.region:
                continue

            if current_value != location.value:
                continue

            location_id = location_name_to_id.get(
                location_name
            )

            if location_id is None:
                continue

            if location_id in ctx.locations_checked:
                continue

            locations_to_check.append(
                location_id
            )

        if locations_to_check:

            await ctx.check_locations(
                locations_to_check
            )
            
# Credits Check


    async def check_credits(self, ctx):

        if self.current_region != CREDITS_REGION:
            return

        if self.global_clock < 120:
            print(
                    "[Bugs Bunny Lost in Time] "
                    "GOAL NOT REACHED! "
                    )
            return
        
        if ctx.finished_game:
            return

        print(
            "[Bugs Bunny Lost in Time] "
            "CREDITS REACHED! "
            "Sending goal completion."
        )

        await ctx.send_msgs([
            {
                "cmd": "StatusUpdate",
                "status": ClientStatus.CLIENT_GOAL,
            }
        ])

        ctx.finished_game = True
    # ============================================================
    # Main watcher
    # ============================================================

    async def game_watcher(self, ctx):

        try:
            await self.manage_save_state(ctx)

            if not self.gameplay_checks_enabled:
                return
         
            # ========================================================
            # DeathLink setup
            # ========================================================

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

            # ========================================================
            # Load randomized level requirements
            # ========================================================

            if not self.level_requirements_initialized:

                self.level_requirements_initialized = (
                    self.load_level_requirements(ctx)
                )

            # ========================================================
            # Initialize AP globals
            # ========================================================

            if not self.globals_initialized:

                await self.initialize_globals(ctx)

                # Replay AP item history.
                await self.handle_received_items(ctx)

                # Release clocks if Nowhere was already checked.
                await self.release_pending_clocks(ctx)

                # Write AP globals into new ROM.
                await self.freeze_globals(ctx)


                if not self.startup_region_confirmed:
                    return

            # ========================================================
            # Counter-based locations
            #
            # These are READ from the individual level counters.
            # ========================================================

            reads = []

            for name, group in counter_groups.items():

                reads.append(
                    (
                        group.address,
                        1,
                        SYSTEM_BUS,
                    )
                )

            values = []

            if reads:

                values = await bizhawk.read(
                    ctx.bizhawk_ctx,
                    reads,
                )

            locations_to_check = []

            for (name, group), value in zip(
                counter_groups.items(),
                values,
            ):

                count = value[0]

                # Diagnostic output.
                print(
                    "[Bugs Bunny Lost in Time] "
                    f"COUNTER READ: {name} = {count} "
                    f"at 0x{group.address:06X}"
                )

                count = min(
                    count,
                    group.max_count,
                )

                for i in range(
                    1,
                    count + 1,
                ):

                    location_name = (
                        f"{name} - {i}"
                    )

                    location_id = location_name_to_id.get(
                        location_name
                    )

                    if location_id is None:
                        continue

                    if (
                        location_id
                        not in ctx.locations_checked
                    ):

                        locations_to_check.append(
                            location_id
                        )

            # ========================================================
            # Send counter locations
            # ========================================================

            if locations_to_check:

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

                await ctx.check_locations(
                    locations_to_check
                )

            # ========================================================
            # Flag-based locations
            # ========================================================

            await self.check_flag_locations(ctx)

            await self.check_magic_locations(ctx)

            # ========================================================
            # Release clocks after Nowhere check
            # ========================================================

            await self.release_pending_clocks(ctx)

            # ========================================================
            # Process newly received AP items
            # ========================================================

            await self.handle_received_items(ctx)

            # ========================================================
            # Keep AP globals frozen
            # ========================================================

            await self.freeze_globals(ctx)

            # ========================================================
            # Update level unlocks
            # ========================================================

            await self.maintain_hub_levels(ctx)

            # ========================================================
            # DeathLink
            # ========================================================

            await self.process_death_link(ctx)

            await self.check_death(ctx)

            await self.check_credits(ctx)

        except bizhawk.RequestFailedError as e:

            print(
                "[Bugs Bunny Lost in Time] "
                f"BizHawk request failed: {e}. "
                "Emulator may be paused or temporarily unavailable."
            )

            return