import logging
import random
from typing import List, Optional, Tuple
from model.location import Location
from model.hunter import Hunter, HunterSkill
from model.knight import Knight
from model.hideout import Hideout
from model.treasure import Treasure, TreasureType


class Kingdom:
    def __init__(self, size: int = 20):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.hunters = []
        self.knights = []
        self.hideouts = []
        self.treasures = []
        self.steps = 0

    def initialize(self, num_hideouts=20, num_hunters=20, num_knights=15, num_treasures=50):
        # Clear existing agents
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.hideouts = []
        self.hunters = []
        self.knights = []
        self.treasures = []

        # Place hideouts with hunters
        for _ in range(num_hideouts):
            loc = self.get_random_empty_location()
            hideout = Hideout(loc)
            self.grid[loc.get_x()][loc.get_y()] = hideout  # Changed to get_x()/get_y()
            self.hideouts.append(hideout)

            # Place 1 hunter per hideout initially
            if len(self.hunters) < num_hunters:
                skill = random.choice(list(HunterSkill))
                hunter = Hunter(loc, skill)
                hideout.add_hunter(hunter)
                self.hunters.append(hunter)

        # ... rest of initialization code

        # Place knights
        for _ in range(num_knights):
            loc = self.get_random_empty_location()
            knight = Knight(loc)
            self.grid[loc.get_x()][loc.get_y()] = knight
            self.knights.append(knight)

        # Place treasures
        for _ in range(num_treasures):
            loc = self.get_random_empty_location()
            treasure_type = random.choice(list(TreasureType))
            treasure = Treasure(loc, treasure_type)
            self.grid[loc.get_x()][loc.get_y()] = treasure
            self.treasures.append(treasure)

    def get_random_empty_location(self) -> Location:
        """Find a random empty location in the grid"""
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.grid[x][y] is None:
                return Location(x, y)

    def step(self):
        """Perform one simulation step"""
        self.steps += 1

        # Update treasures
        self.update_treasures()

        # Update hunters
        self.update_hunters()

        # Update knights
        self.update_knights()

        # Update hideouts
        self.update_hideouts()

    def update_treasures(self):
        """Update all treasures in the kingdom, removing those that have decayed"""
        for treasure in self.treasures[:]:  # Iterate over a copy of the list
            if not treasure.decay_value():
                loc = treasure.get_location()
                x, y = loc.get_x(), loc.get_y()

                # Only clear if this treasure is still in the grid
                if self.grid[x][y] == treasure:
                    self.grid[x][y] = None

                self.treasures.remove(treasure)
                logging.info(f"{treasure.type.name} treasure decayed at ({x}, {y})")

    def update_hunters(self):
        """Update all hunters, handling deaths, resting, and exploration"""
        for hunter in self.hunters[:]:
            if not hunter.update_survival():
                loc = hunter.location
                if self.grid[loc.x][loc.y] == hunter:
                    self.grid[loc.x][loc.y] = None
                self.hunters.remove(hunter)
                continue
            # Iterate over a copy of the list
            x, y = hunter.get_location().get_x(), hunter.get_location().get_y()
            logging.info(f"Hunter {hunter.skill.name.lower()} at ({x}, {y}) - "
                         f"Stamina: {hunter.stamina:.1f}%, "
                         f"Carrying: {'Yes' if hunter.carrying else 'No'}")
            if not hunter.update_survival():
                # Handle hunter death
                loc = hunter.get_location()
                x, y = loc.get_x(), loc.get_y()

                # Only clear if this hunter is still in the grid
                if self.grid[x][y] == hunter:
                    self.grid[x][y] = None

                self.hunters.remove(hunter)
                logging.info(f"Hunter died at ({x}, {y}) (Stamina: 0%)")
                continue

            current_loc = hunter.get_location()
            current_x, current_y = current_loc.get_x(), current_loc.get_y()

            # Clear current position if hunter is still there
            if self.grid[current_x][current_y] == hunter:
                self.grid[current_x][current_y] = None

            if hunter.should_rest():
                self.handle_hunter_resting(hunter)
            else:
                self.handle_hunter_exploring(hunter)

            # Update new position in grid if hunter moved
            new_loc = hunter.get_location()
            if new_loc.get_x() != current_x or new_loc.get_y() != current_y:
                self.grid[new_loc.get_x()][new_loc.get_y()] = hunter

    def handle_hunter_resting(self, hunter):
        """Handle hunter resting behavior - move to nearest hideout or rest if already there"""
        nearest_hideout = min(
            self.hideouts,
            key=lambda h: self.distance(hunter.get_location(), h.get_location())
        )

        current_x, current_y = hunter.get_location().get_x(), hunter.get_location().get_y()

        # Clear current position if hunter is still there
        if self.grid[current_x][current_y] == hunter:
            self.grid[current_x][current_y] = None

        if not hunter.get_location().equals(nearest_hideout.get_location()):
            next_step = self.find_next_step(hunter.get_location(), nearest_hideout.get_location())
            hunter.move(next_step)

            # Update hunter's new position in grid
            new_x, new_y = next_step.get_x(), next_step.get_y()
            self.grid[new_x][new_y] = hunter

            logging.info(f"Hunter moving to hideout at ({new_x}, {new_y}) (Stamina: {hunter.stamina:.1f}%)")
        else:
            nearest_hideout.add_hunter(hunter)
            hunter.rest()
            logging.info(f"Hunter resting in hideout (Stamina: {hunter.stamina:.1f}%)")
            nearest_hideout.share_information()

    def handle_hunter_exploring(self, hunter):
        """Handle hunter exploration behavior - collect treasure or explore randomly"""
        hunter.scan_area(self.grid)

        current_x, current_y = hunter.get_location().get_x(), hunter.get_location().get_y()

        # Clear current position if hunter is still there
        if self.grid[current_x][current_y] == hunter:
            self.grid[current_x][current_y] = None

        if hunter.carrying:
            if hunter.known_hideouts:
                target = min(
                    hunter.known_hideouts,
                    key=lambda loc: self.distance(hunter.get_location(), loc)
                )
                next_step = self.find_next_step(hunter.get_location(), target)
                hunter.move(next_step)

                # Update hunter's new position in grid
                new_x, new_y = next_step.get_x(), next_step.get_y()
                self.grid[new_x][new_y] = hunter

                logging.info(f"Hunter carrying treasure moving to hideout at ({new_x}, {new_y})")

                cell = self.grid[new_x][new_y]
                if cell and hasattr(cell, 'hunters'):  # Hideout check
                    cell.store_treasure(hunter.drop_treasure())
                    cell.add_hunter(hunter)
                    logging.info(f"Hunter delivered treasure to hideout at ({new_x}, {new_y})")
                    # Remove hunter from grid (now inside hideout)
                    self.grid[new_x][new_y] = cell
        else:
            if hunter.known_treasures:
                target = min(
                    hunter.known_treasures,
                    key=lambda loc: self.distance(hunter.get_location(), loc)
                )
                next_step = self.find_next_step(hunter.get_location(), target)
                hunter.move(next_step)

                # Update hunter's new position in grid
                new_x, new_y = next_step.get_x(), next_step.get_y()
                self.grid[new_x][new_y] = hunter

                logging.info(f"Hunter moving to treasure at ({new_x}, {new_y})")

                cell = self.grid[new_x][new_y]
                if cell and hasattr(cell, 'type'):  # Treasure found
                    hunter.collect_treasure(cell)
                    self.treasures.remove(cell)  # Remove from global list
                    self.grid[new_x][new_y] = hunter  # Hunter now occupies this cell
                    logging.info(f"Hunter collected treasure at ({new_x}, {new_y})")
                    return  # Important to prevent further moves this turn
            else:
                adjacent = hunter.get_location().get_adjacent_locations(self.size)
                valid_moves = [
                    loc for loc in adjacent
                    if not (self.grid[loc.get_x()][loc.get_y()] and
                            hasattr(self.grid[loc.get_x()][loc.get_y()], 'energy'))  # Avoid knights
                ]
                if valid_moves:
                    next_step = random.choice(valid_moves)
                    hunter.move(next_step)

                    # Update hunter's new position in grid
                    new_x, new_y = next_step.get_x(), next_step.get_y()
                    self.grid[new_x][new_y] = hunter

                    logging.info(f"Hunter exploring to ({new_x}, {new_y})")

    def update_knights(self):
        """Update all knights in the kingdom"""
        for knight in self.knights:
            if knight.should_retreat():
                logging.info(f"Knight retreating to garrison (Energy: {knight.energy:.1f}%)")
                self.handle_knight_retreat(knight)
            else:
                self.handle_knight_patrol(knight)

    def update_hideouts(self):
        for hideout in self.hideouts:
            if not hideout.hunters and not hideout.stored_treasures:
                loc = hideout.location
                self.grid[loc.x][loc.y] = None
                self.hideouts.remove(hideout)
                continue
            hideout_x, hideout_y = hideout.get_location().get_x(), hideout.get_location().get_y()
            logging.info(f"Hideout at ({hideout_x}, {hideout_y}): "
                         f"{len(hideout.stored_treasures)} treasures, "
                         f"{len(hideout.hunters)} hunters")
            hideout.share_information()
            new_skill = hideout.try_recruit()
            if new_skill:
                new_hunter = Hunter(hideout.get_location(), new_skill)
                hideout.add_hunter(new_hunter)
                self.hunters.append(new_hunter)
                logging.info(f"New {new_skill.name.lower()} hunter recruited at hideout ({hideout.get_location().get_x()}, {hideout.get_location().get_y()})")

    def is_simulation_over(self) -> bool:
        """Check if simulation should end"""
        return len(self.treasures) == 0 or (len(self.hunters) == 0 and not any(h.try_recruit() for h in self.hideouts))

    def __str__(self) -> str:
        return (f"Kingdom (Size: {self.size}x{self.size}, Step: {self.steps})\n"
                f"Hunters: {len(self.hunters)}, Knights: {len(self.knights)}, "
                f"Hideouts: {len(self.hideouts)}, Treasures: {len(self.treasures)}")

    def handle_hunter_resting(self, hunter):
        """Handle hunter resting behavior"""
        # Find nearest hideout
        nearest_hideout = min(
            self.hideouts,
            key=lambda h: self.distance(hunter.get_location(), h.get_location())
        )

        # Move toward hideout if not already there
        if not hunter.get_location().equals(nearest_hideout.get_location()):
            next_step = self.find_next_step(hunter.get_location(), nearest_hideout.get_location())
            hunter.move(next_step)
        else:
            # Rest in hideout
            nearest_hideout.add_hunter(hunter)
            hunter.rest()
            nearest_hideout.share_information()

    def handle_hunter_exploring(self, hunter):
        """Handle hunter exploring behavior with proper grid position updates"""
        current_loc = hunter.get_location()
        current_x, current_y = current_loc.get_x(), current_loc.get_y()

        # Clear current position (only if hunter is still there)
        if self.grid[current_x][current_y] == hunter:
            self.grid[current_x][current_y] = None

        # Scan area first
        hunter.scan_area(self.grid)

        # If carrying treasure, go to nearest hideout
        if hunter.carrying:
            if hunter.known_hideouts:
                target = min(
                    hunter.known_hideouts,
                    key=lambda loc: self.distance(hunter.get_location(), loc)
                )
                next_step = self.find_next_step(hunter.get_location(), target)
                hunter.move(next_step)

                # Update hunter's position in grid
                new_x, new_y = next_step.get_x(), next_step.get_y()
                self.grid[new_x][new_y] = hunter

                # Check if reached hideout
                cell = self.grid[new_x][new_y]
                if cell and hasattr(cell, 'hunters'):  # Hideout check
                    cell.store_treasure(hunter.drop_treasure())
                    cell.add_hunter(hunter)
                    # Remove hunter from grid (now inside hideout)
                    self.grid[new_x][new_y] = cell
        else:
            # Find nearest known treasure
            if hunter.known_treasures:
                target = min(
                    hunter.known_treasures,
                    key=lambda loc: self.distance(hunter.get_location(), loc)
                )
                next_step = self.find_next_step(hunter.get_location(), target)
                hunter.move(next_step)

                # Update hunter's position in grid
                new_x, new_y = next_step.get_x(), next_step.get_y()
                self.grid[new_x][new_y] = hunter

                # Check if reached treasure
                cell = self.grid[new_x][new_y]
                if cell and hasattr(cell, 'type'):  # Treasure check
                    hunter.collect_treasure(cell)
                    self.treasures.remove(cell)  # Remove from treasures list
                    self.grid[new_x][new_y] = hunter
                    logging.info(f"Hunter collected {cell.type.name} treasure at ({new_x}, {new_y})")
            else:
                # Random exploration
                adjacent = hunter.get_location().get_adjacent_locations(self.size)
                valid_moves = [
                    loc for loc in adjacent
                    if not (self.grid[loc.get_x()][loc.get_y()] and
                            hasattr(self.grid[loc.get_x()][loc.get_y()], 'energy'))  # Avoid knights
                ]
                if valid_moves:
                    next_step = random.choice(valid_moves)
                    hunter.move(next_step)
                    # Update hunter's position in grid
                    new_x, new_y = next_step.get_x(), next_step.get_y()
                    self.grid[new_x][new_y] = hunter

    def handle_knight_retreat(self, knight):
        """Handle knight retreat behavior with proper energy management"""
        current_loc = knight.get_location()
        current_x, current_y = current_loc.get_x(), current_loc.get_y()

        # Clear current position if knight is still there
        if self.grid[current_x][current_y] == knight:
            self.grid[current_x][current_y] = None

        # Find nearest hideout (garrison)
        if self.hideouts:
            nearest_garrison = min(
                self.hideouts,
                key=lambda h: self.distance(knight.get_location(), h.get_location())
            )

            # If not at garrison, move toward it
            if not knight.get_location().equals(nearest_garrison.get_location()):
                next_step = self.find_next_step(knight.get_location(), nearest_garrison.get_location())
                knight.move(next_step)
                self.grid[next_step.get_x()][next_step.get_y()] = knight
            else:
                # Rest in garrison and recover energy
                knight.rest()
                if knight.energy >= 100:  # Fully recovered
                    knight.target = None
        else:
            # No hideouts - just rest in place
            knight.rest()

    def handle_knight_patrol(self, knight):
        """Handle knight patrol behavior with proper logging and position tracking"""
        current_loc = knight.get_location()
        current_x, current_y = current_loc.get_x(), current_loc.get_y()

        # Clear current position if knight is still there
        if self.grid[current_x][current_y] == knight:
            self.grid[current_x][current_y] = None

        # Check for hunters in 3-cell radius
        hunter_locations = []
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                if dx == 0 and dy == 0:
                    continue
                x = (current_x + dx) % self.size
                y = (current_y + dy) % self.size
                cell = self.grid[x][y]
                if cell and hasattr(cell, 'skill'):  # Hunter check
                    hunter_locations.append(Location(x, y))
                    logging.info(f"Knight spotted hunter at ({x}, {y})")

        if hunter_locations:
            # Chase nearest hunter
            target = min(
                hunter_locations,
                key=lambda loc: self.distance(knight.get_location(), loc)
            )
            knight.chase(target)
            next_step = self.find_next_step(knight.get_location(), target)
            logging.info(f"Knight chasing hunter from ({current_x}, {current_y}) "
                         f"to ({next_step.get_x()}, {next_step.get_y()}) "
                         f"(Energy: {knight.energy:.1f}%)")
            knight.move(next_step)
            new_x, new_y = next_step.get_x(), next_step.get_y()
            self.grid[new_x][new_y] = knight

            # Check if caught hunter
            cell = self.grid[new_x][new_y]
            if cell and hasattr(cell, 'skill'):  # Hunter check
                detained = knight.interact_with_hunter(cell)
                logging.info(f"Knight {'detained' if detained else 'challenged'} "
                             f"hunter at ({new_x}, {new_y})")
                if cell.carrying:
                    dropped = cell.drop_treasure()
                    logging.info(f"Hunter dropped {dropped.type.name} treasure at ({new_x}, {new_y})")
        else:
            # Random patrol
            adjacent = knight.get_location().get_adjacent_locations(self.size)
            if adjacent:
                next_step = random.choice(adjacent)
                logging.info(f"Knight patrolling from ({current_x}, {current_y}) "
                             f"to ({next_step.get_x()}, {next_step.get_y()}) "
                             f"(Energy: {knight.energy:.1f}%)")
                knight.move(next_step)
                new_x, new_y = next_step.get_x(), next_step.get_y()
                self.grid[new_x][new_y] = knight

    def distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate wrapped distance between two locations"""
        dx = min(abs(loc1.get_x() - loc2.get_x()), self.size - abs(loc1.get_x() - loc2.get_x()))
        dy = min(abs(loc1.get_y() - loc2.get_y()), self.size - abs(loc1.get_y() - loc2.get_y()))
        return (dx ** 2 + dy ** 2) ** 0.5  # Euclidean distance

    def find_next_step(self, current: Location, target: Location) -> Location:
        """Find next step toward target location"""
        dx = (target.get_x() - current.get_x() + self.size) % self.size
        dy = (target.get_y() - current.get_y() + self.size) % self.size

        # Prefer cardinal directions
        if dx > self.size / 2:
            dx -= self.size
        if dy > self.size / 2:
            dy -= self.size

        if abs(dx) > abs(dy):
            x = current.get_x() + (1 if dx > 0 else -1)
            return Location(x % self.size, current.get_y())
        else:
            y = current.get_y() + (1 if dy > 0 else -1)
            return Location(current.get_x(), y % self.size)