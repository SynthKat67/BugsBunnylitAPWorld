from dataclasses import dataclass

from Options import (
    Choice,
    DeathLink,
    PerGameCommonOptions,
)

class LevelRequirements(Choice):
    """Determines whether level requirements use the vanilla order or are shuffled."""

    display_name = "Level Requirements"

    option_vanilla = 0
    option_shuffle = 1

    default = option_vanilla

class Goal(Choice):
    """Determines which ending is required to complete the game."""

    display_name = "Goal"

    option_present_day = 0

    default = option_present_day

@dataclass
class BugsBunnyLiTOptions(PerGameCommonOptions):
    goal: Goal
    level_requirements: LevelRequirements
    death_link: DeathLink