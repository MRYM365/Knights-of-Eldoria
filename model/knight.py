from __future__ import annotations
from model.agent import Agent
from typing import TYPE_CHECKING, Optional
import random

if TYPE_CHECKING:
    from model.location import Location
    from model.hunter import Hunter


class Knight(Agent):
    def __init__(self, location: 'Location'):
        super().__init__(location)
        self.energy = 100.0  # Percentage
        self.target: Optional['Hunter'] = None  # Current hunter being chased
        self.garrison_location: Optional['Location'] = None  # Location of nearest garrison

    def move(self, new_location: 'Location'):
        """Move to a new location"""
        self.set_location(new_location)

    def chase(self, target: 'Hunter'):
        """Chase a target, consuming 20% energy"""
        self.energy = max(0, self.energy - 20)
        self.target = target

    def should_retreat(self) -> bool:
        """Check if knight needs to retreat to garrison (energy <= 20%)"""
        return self.energy <= 20

    def rest(self):
        """Recover energy while resting in garrison (10% per step)"""
        self.energy = min(100, self.energy + 10)
        self.target = None

    def interact_with_hunter(self, hunter: 'Hunter') -> str:
        """Interact with a hunter, returns 'detained' or 'challenged'"""
        if random.random() < 0.3:  # 30% chance to detain
            # Detain: 5% stamina reduction
            hunter.stamina = max(0, hunter.stamina - 5)
            return "detained"
        else:
            # Challenge: 20% stamina reduction
            hunter.stamina = max(0, hunter.stamina - 20)
            return "challenged"

    def scan_for_hunters(self, grid, radius=3) -> Optional['Hunter']:
        """Scan for hunters within 3-cell radius, prioritizing treasure-carrying hunters"""
        current_loc = self.get_location()
        grid_size = len(grid)
        nearest_hunter = None
        min_distance = float('inf')
        treasure_hunter = None
        treasure_distance = float('inf')

        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx == 0 and dy == 0:
                    continue  # Skip current location

                x = (current_loc.get_x() + dx) % grid_size
                y = (current_loc.get_y() + dy) % grid_size
                cell = grid[x][y]

                if cell is not None and hasattr(cell, 'skill'):  # Check if cell contains a hunter
                    distance = abs(dx) + abs(dy)
                    if cell.carrying:  # Prioritize treasure-carrying hunters
                        if distance < treasure_distance:
                            treasure_distance = distance
                            treasure_hunter = cell
                    elif distance < min_distance:
                        min_distance = distance
                        nearest_hunter = cell

        # Return treasure-carrying hunter if found, otherwise return nearest hunter
        return treasure_hunter if treasure_hunter else nearest_hunter

    def __str__(self) -> str:
        status = f"Knight at {self.get_location()}, Energy: {self.energy:.1f}%"
        if self.target:
            status += f", Targeting: {self.target.get_location()}"
        return status