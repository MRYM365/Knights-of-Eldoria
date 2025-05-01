from __future__ import annotations
from enum import Enum
from model.agent import Agent
from typing import TYPE_CHECKING, List
import random

if TYPE_CHECKING:
    from model.location import Location
    from model.treasure import Treasure
    from model.hideout import Hideout


class HunterSkill(Enum):
    NAVIGATION = 1  # Better at finding paths and avoiding knights
    ENDURANCE = 2   # Stamina depletes slower and recovers faster
    STEALTH = 3     # Better at avoiding knight detection


class Hunter(Agent):
    def __init__(self, location: 'Location', skill: HunterSkill):
        super().__init__(location)
        self.skill = skill
        self.stamina = 100.0  # Percentage
        self.carrying = None  # Currently carried treasure
        self.known_treasures: List['Location'] = []  # Locations of known treasures
        self.known_hideouts: List['Location'] = []  # Locations of known hideouts
        self.known_knights: List['Location'] = []  # Locations of recent knight sightings
        self.survival_time = 0  # Steps survived at 0% stamina
        self.wealth = 0  # Total wealth collected

    def move(self, new_location: 'Location'):
        """Move to a new location, reducing stamina by 1%"""
        self.set_location(new_location)
        # Endurance skill reduces stamina depletion
        stamina_reduction = 0.75 if self.skill == HunterSkill.ENDURANCE else 1.0
        self.stamina = max(0, self.stamina - stamina_reduction)

    def rest(self):
        """Recover stamina while resting in hideout"""
        # Endurance skill increases recovery rate
        recovery_rate = 3.0 if self.skill == HunterSkill.ENDURANCE else 2.0
        self.stamina = min(100, self.stamina + recovery_rate)

    def scan_area(self, grid, radius=3):
        """Scan surrounding area for objects"""
        current_loc = self.get_location()
        grid_size = len(grid)

        # Navigation skill increases scan radius
        if self.skill == HunterSkill.NAVIGATION:
            radius += 1

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue  # Skip current location

                x = (current_loc.get_x() + dx) % grid_size
                y = (current_loc.get_y() + dy) % grid_size
                cell = grid[x][y]

                if cell is not None:
                    cell_location = cell.get_location()
                    # Check for Treasure using hasattr
                    if hasattr(cell, 'type') and cell_location not in self.known_treasures:
                        self.known_treasures.append(cell_location)
                    # Check for Hideout using hasattr
                    elif hasattr(cell, 'hunters') and cell_location not in self.known_hideouts:
                        self.known_hideouts.append(cell_location)
                    # Check for Knight using hasattr
                    elif hasattr(cell, 'energy') and cell_location not in self.known_knights:
                        self.known_knights.append(cell_location)

    def collect_treasure(self, treasure: 'Treasure'):
        """Collect a piece of treasure if not already carrying one"""
        if self.carrying is None:
            self.carrying = treasure
            return True
        return False

    def drop_treasure(self):
        """Drop currently carried treasure"""
        dropped = self.carrying
        self.carrying = None
        return dropped

    def is_exhausted(self) -> bool:
        """Check if hunter is exhausted (stamina <= 0%)"""
        return self.stamina <= 0

    def should_rest(self) -> bool:
        """Check if hunter needs to rest (stamina <= 6%)"""
        return self.stamina <= 6

    def update_survival(self) -> bool:
        """Update survival time when exhausted, returns False if hunter dies"""
        if self.is_exhausted():
            self.survival_time += 1
            return self.survival_time <= 5  # Die after 5 steps at 0% stamina
        return True

    def get_skill_modifier(self) -> float:
        """Get skill-based modifier for various actions"""
        if self.skill == HunterSkill.NAVIGATION:
            return 1.2  # 20% better at navigation
        elif self.skill == HunterSkill.ENDURANCE:
            return 1.2  # 20% better at endurance
        elif self.skill == HunterSkill.STEALTH:
            return 1.2  # 20% better at stealth
        return 1.0

    def __str__(self) -> str:
        status = f"Hunter ({self.skill.name}) at {self.get_location()}, Stamina: {self.stamina:.1f}%"
        if self.carrying:
            status += f", Carrying: {self.carrying.type.name}"
        return status