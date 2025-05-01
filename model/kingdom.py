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
        """Initialize the kingdom with a grid of at least 20x20 cells"""
        if size < 20:
            size = 20  # Minimum size requirement
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.hunters = []
        self.knights = []
        self.hideouts = []
        self.treasures = []
        self.steps = 0
        self.total_wealth = 0

    def initialize(self, num_hideouts=20, num_hunters=20, num_knights=15, num_treasures=50):
        """Initialize the simulation with agents and treasures"""
        # Clear the grid and agent lists
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.hideouts = []
        self.hunters = []
        self.knights = []
        self.treasures = []
        self.total_wealth = 0

        # Place hideouts first
        for _ in range(num_hideouts):
            while True:
                loc = Location(random.randint(0, self.size - 1), random.randint(0, self.size - 1))
                if self.grid[loc.get_x()][loc.get_y()] is None:
                    hideout = Hideout(loc)
                    self.grid[loc.get_x()][loc.get_y()] = hideout
                    self.hideouts.append(hideout)
                    break

        # Place hunters in hideouts
        hunters_placed = 0
        while hunters_placed < num_hunters:
            hideout = random.choice(self.hideouts)
            hunter = Hunter(hideout.get_location(), random.choice(list(HunterSkill)))
            hideout.add_hunter(hunter)
            self.hunters.append(hunter)
            hunters_placed += 1
            # Ensure hideout remains in grid
            self.grid[hideout.get_location().get_x()][hideout.get_location().get_y()] = hideout
            logging.info(f"Hunter with {hunter.skill.name} skill placed at hideout ({hideout.get_location().get_x()}, {hideout.get_location().get_y()})")

        # Place knights
        for _ in range(num_knights):
            while True:
                loc = Location(random.randint(0, self.size - 1), random.randint(0, self.size - 1))
                if self.grid[loc.get_x()][loc.get_y()] is None:
                    knight = Knight(loc)
                    self.grid[loc.get_x()][loc.get_y()] = knight
                    self.knights.append(knight)
                    break

        # Place treasures
        for _ in range(num_treasures):
            while True:
                loc = Location(random.randint(0, self.size - 1), random.randint(0, self.size - 1))
                if self.grid[loc.get_x()][loc.get_y()] is None:
                    treasure_type = random.choice(list(TreasureType))
                    treasure = Treasure(loc, treasure_type)
                    self.grid[loc.get_x()][loc.get_y()] = treasure
                    self.treasures.append(treasure)
                    break

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
        for hunter in self.hunters[:]:  # Iterate over a copy of the list
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
                cell = self.grid[new_x][new_y]
                
                if cell and hasattr(cell, 'hunters'):  # Hideout check
                    # Store treasure in hideout
                    treasure = hunter.drop_treasure()
                    cell.store_treasure(treasure)
                    self.total_wealth += treasure.value  # Update total wealth when treasure is stored
                    logging.info(f"Hunter delivered {treasure.type.name} treasure to hideout at ({new_x}, {new_y})")
                else:
                    self.grid[new_x][new_y] = hunter
            else:
                # Move randomly if no known hideouts
                next_loc = self.get_random_empty_location()
                hunter.move(next_loc)
                self.grid[next_loc.get_x()][next_loc.get_y()] = hunter
        else:
            # Look for treasure
            if hunter.known_treasures:
                # Filter known treasures to only include actual treasures still in the grid
                valid_treasures = [
                    loc for loc in hunter.known_treasures
                    if self.grid[loc.get_x()][loc.get_y()] and hasattr(self.grid[loc.get_x()][loc.get_y()], 'value')
                ]
                
                if valid_treasures:
                    target = max(
                        valid_treasures,
                        key=lambda loc: self.grid[loc.get_x()][loc.get_y()].value
                    )
                    next_step = self.find_next_step(hunter.get_location(), target)
                    hunter.move(next_step)

                    # Update hunter's new position in grid
                    new_x, new_y = next_step.get_x(), next_step.get_y()
                    cell = self.grid[new_x][new_y]

                    if cell and hasattr(cell, 'value'):  # Treasure check
                        hunter.collect_treasure(cell)
                        self.treasures.remove(cell)
                        self.grid[new_x][new_y] = hunter
                        logging.info(f"Hunter collected {cell.type.name} treasure at ({new_x}, {new_y})")
                    else:
                        self.grid[new_x][new_y] = hunter
                else:
                    # No valid treasures found, move randomly
                    next_loc = self.get_random_empty_location()
                    hunter.move(next_loc)
                    self.grid[next_loc.get_x()][next_loc.get_y()] = hunter
            else:
                # Move randomly if no known treasures
                next_loc = self.get_random_empty_location()
                hunter.move(next_loc)
                self.grid[next_loc.get_x()][next_loc.get_y()] = hunter

    def update_knights(self):
        """Update all knights in the kingdom"""
        for knight in self.knights[:]:  # Iterate over a copy of the list
            current_loc = knight.get_location()
            current_x, current_y = current_loc.get_x(), current_loc.get_y()

            # Clear current position if knight is still there
            if self.grid[current_x][current_y] == knight:
                self.grid[current_x][current_y] = None

            if knight.should_retreat():
                self.handle_knight_retreat(knight)
            else:
                self.handle_knight_patrol(knight)

            # Update new position in grid if knight moved
            new_loc = knight.get_location()
            if new_loc.get_x() != current_x or new_loc.get_y() != current_y:
                self.grid[new_loc.get_x()][new_loc.get_y()] = knight

    def handle_knight_retreat(self, knight):
        """Handle knight retreating to garrison when energy is low"""
        if knight.garrison_location:
            next_step = self.find_next_step(knight.get_location(), knight.garrison_location)
            knight.move(next_step)
            knight.rest()  # Recover energy while moving to garrison
        else:
            # Find nearest hideout as temporary garrison
            nearest_hideout = min(
                self.hideouts,
                key=lambda h: self.distance(knight.get_location(), h.get_location())
            )
            knight.garrison_location = nearest_hideout.get_location()
            next_step = self.find_next_step(knight.get_location(), nearest_hideout.get_location())
            knight.move(next_step)
            knight.rest()

    def handle_knight_patrol(self, knight):
        """Handle knight patrolling and chasing hunters"""
        # Scan for hunters within 3-cell radius
        target = knight.scan_for_hunters(self.grid)
        if target:
            # If hunter is carrying treasure, increase chase priority
            if target.carrying:
                knight.chase(target)
                next_step = self.find_next_step(knight.get_location(), target.get_location())
                knight.move(next_step)
                logging.info(f"Knight at ({knight.get_location().get_x()}, {knight.get_location().get_y()}) chasing {target.skill.name} hunter carrying {target.carrying.type.name} treasure (Energy: {knight.energy:.1f}%)")
            else:
                # Regular chase for non-carrying hunters
                knight.chase(target)
                next_step = self.find_next_step(knight.get_location(), target.get_location())
                knight.move(next_step)
                logging.info(f"Knight at ({knight.get_location().get_x()}, {knight.get_location().get_y()}) patrolling near {target.skill.name} hunter (Energy: {knight.energy:.1f}%)")

            # Check if knight caught up with hunter
            if knight.get_location().equals(target.get_location()):
                result = knight.interact_with_hunter(target)
                if result == "detained":
                    # Remove hunter from grid and lists
                    self.hunters.remove(target)
                    logging.info(f"Knight detained {target.skill.name} hunter at ({target.get_location().get_x()}, {target.get_location().get_y()}) (Hunter Stamina: {target.stamina:.1f}%, Knight Energy: {knight.energy:.1f}%)")
                elif result == "challenged":
                    # Hunter drops treasure if carrying
                    if target.carrying:
                        treasure = target.drop_treasure()
                        x, y = target.get_location().get_x(), target.get_location().get_y()
                        self.grid[x][y] = treasure
                        self.treasures.append(treasure)
                        logging.info(f"{target.skill.name} hunter dropped {treasure.type.name} treasure after challenge at ({x}, {y}) (Hunter Stamina: {target.stamina:.1f}%, Knight Energy: {knight.energy:.1f}%)")
        else:
            # Random patrol movement
            adjacent = knight.get_location().get_adjacent_locations(self.size)
            valid_moves = [loc for loc in adjacent if self.grid[loc.get_x()][loc.get_y()] is None]
            if valid_moves:
                next_step = random.choice(valid_moves)
                knight.move(next_step)
                logging.info(f"Knight patrolling to ({next_step.get_x()}, {next_step.get_y()}) (Energy: {knight.energy:.1f}%)")

    def update_hideouts(self):
        """Update all hideouts, handling recruitment and information sharing"""
        for hideout in self.hideouts:
            # Ensure hideout is in grid
            x, y = hideout.get_location().get_x(), hideout.get_location().get_y()
            if self.grid[x][y] != hideout:
                self.grid[x][y] = hideout
                
            # Share information among hunters
            if len(hideout.hunters) > 1:
                hunter_skills = [h.skill.name for h in hideout.hunters]
                logging.info(f"Hideout at ({x}, {y}) sharing information among {len(hideout.hunters)} hunters with skills: {', '.join(hunter_skills)}")
            hideout.share_information()

            # Try to recruit new hunter
            new_skill = hideout.try_recruit()
            if new_skill:
                new_hunter = Hunter(hideout.get_location(), new_skill)
                hideout.add_hunter(new_hunter)
                self.hunters.append(new_hunter)
                # Ensure hideout remains in grid after recruitment
                self.grid[x][y] = hideout
                logging.info(f"New {new_skill.name} hunter recruited at hideout ({x}, {y}) - Total hunters in hideout: {len(hideout.hunters)}")

            # Update grid to reflect current hideout state
            self.grid[x][y] = hideout

    def is_simulation_over(self) -> bool:
        """Check if simulation should end"""
        return len(self.treasures) == 0 or (len(self.hunters) == 0 and not any(h.try_recruit() for h in self.hideouts))

    def __str__(self) -> str:
        return (f"Kingdom (Size: {self.size}x{self.size}, Step: {self.steps})\n"
                f"Hunters: {len(self.hunters)}, Knights: {len(self.knights)}, "
                f"Hideouts: {len(self.hideouts)}, Treasures: {len(self.treasures)}")

    def distance(self, loc1: Location, loc2: Location) -> float:
        """Calculate Manhattan distance between two locations, accounting for grid wrapping"""
        dx = min(abs(loc1.get_x() - loc2.get_x()), self.size - abs(loc1.get_x() - loc2.get_x()))
        dy = min(abs(loc1.get_y() - loc2.get_y()), self.size - abs(loc1.get_y() - loc2.get_y()))
        return dx + dy

    def find_next_step(self, current: Location, target: Location) -> Location:
        """Find the next step towards the target, accounting for grid wrapping"""
        dx = target.get_x() - current.get_x()
        dy = target.get_y() - current.get_y()

        # Handle wrapping
        if abs(dx) > self.size / 2:
            dx = -dx if dx > 0 else -dx
        if abs(dy) > self.size / 2:
            dy = -dy if dy > 0 else -dy

        # Choose direction with larger difference
        if abs(dx) > abs(dy):
            new_x = (current.get_x() + (1 if dx > 0 else -1)) % self.size
            new_y = current.get_y()
        else:
            new_x = current.get_x()
            new_y = (current.get_y() + (1 if dy > 0 else -1)) % self.size

        return Location(new_x, new_y)