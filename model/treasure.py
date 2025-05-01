from __future__ import annotations
from enum import Enum
from model.agent import Agent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.location import Location


class TreasureType(Enum):
    BRONZE = 1
    SILVER = 2
    GOLD = 3


class Treasure(Agent):
    def __init__(self, location: 'Location', treasure_type: TreasureType, initial_value: float = 100.0):
        super().__init__(location)
        self.type = treasure_type
        self.value = initial_value
        self.initial_value = initial_value

    def decay_value(self):
        """Reduce treasure value by 0.1% each step"""
        self.value *= 0.999
        return self.value > 0.01  # Returns True if treasure still has value

    def get_value_increase(self) -> float:
        """Returns the percentage increase a hunter gets for collecting this treasure"""
        if self.type == TreasureType.BRONZE:
            return 0.03
        elif self.type == TreasureType.SILVER:
            return 0.07
        elif self.type == TreasureType.GOLD:
            return 0.13

    def __str__(self) -> str:
        return f"{self.type.name} Treasure at {self.get_location()} (Value: {self.value:.2f}%)"