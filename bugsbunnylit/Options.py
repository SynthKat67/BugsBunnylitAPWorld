from dataclasses import dataclass

from Options import (
    Choice,
    DeathLink,
    PerGameCommonOptions,
)


class Goal(Choice):
    """
    Determines which ending is required to complete the game.
    """

    display_name = "Goal"

    option_present_day = 0
    option_pismo_beach = 1

    default = option_present_day

@dataclass
class BugsBunnyLiTOptions(PerGameCommonOptions):
    goal: Goal
    death_link: DeathLink