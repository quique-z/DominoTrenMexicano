from dataclasses import dataclass
from typing import Set, Optional
from enum import Enum, auto

from game.RevealedChip import RevealedChip


class TurnAction(Enum):
    PLAYED_CHIPS = auto()
    PASS = auto()
    DREW = auto()

@dataclass(frozen=True)
class TurnLog:
    turn_number: int
    player_id: int
    action: TurnAction
    set_chips_played: Optional[Set[RevealedChip]]
    set_numbers_not_available: Optional[Set[int]]
