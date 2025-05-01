from __future__ import annotations
from model.agent import Agent
from typing import TYPE_CHECKING
import random

if TYPE_CHECKING:
    from model.location import Location


class Knight(Agent):
    def __init__(self, location: 'Location'):
        super().__init__(location)
        self.energy = 100.0  # Percentage
        self.target = None  # Current hunter being chased

    def move(self, new_location: 'Location'):
        """Move to a new location"""
        self.set_location(new_location)

    def chase(self, target_location: 'Location'):
        """Chase a target, consuming energy"""
        self.energy = max(0, self.energy - 20)
        self.target = target_location

    def should_retreat(self) -> bool:
        """Check if knight needs to retreat to garrison"""
        return self.energy <= 20

    def rest(self):
        """Recover energy while resting"""
        self.energy = min(100, self.energy + 10)
        self.target = None

    def interact_with_hunter(self, hunter) -> bool:
        """Interact with a hunter, returns True if hunter is detained"""
        if random.random() < 0.5:  # 50% chance to detain vs challenge
            # Detain
            hunter.stamina = max(0, hunter.stamina - 5)
            return True
        else:
            # Challenge
            hunter.stamina = max(0, hunter.stamina - 20)
            return False

    def __str__(self) -> str:
        status = f"Knight at {self.get_location()}, Energy: {self.energy:.1f}%"
        if self.target:
            status += f", Targeting: {self.target}"
        return status