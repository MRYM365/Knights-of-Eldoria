from __future__ import annotations
from typing import List, Set, Optional
from model.agent import Agent
from model.hunter import Hunter, HunterSkill
from model.treasure import Treasure
import random
import logging


class Hideout(Agent):
    def __init__(self, location: 'Location'):
        super().__init__(location)
        self.hunters: List[Hunter] = []  # List of hunters in this hideout (max 5)
        self.stored_treasures: List[Treasure] = []  # List of treasures stored here
        self.known_treasures: List['Location'] = []  # Locations of known treasures
        self.known_hideouts: List['Location'] = []  # Locations of other known hideouts
        self.known_knights: List['Location'] = []  # Locations of recent knight sightings

    def add_hunter(self, hunter: Hunter) -> bool:
        """Add a hunter to the hideout if there's space (max 5 hunters)"""
        if len(self.hunters) < 5:
            self.hunters.append(hunter)
            return True
        return False

    def remove_hunter(self, hunter: Hunter) -> bool:
        """Remove a hunter from the hideout"""
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            return True
        return False

    def store_treasure(self, treasure: Treasure):
        """Store a piece of treasure in the hideout and update its value"""
        # Apply hideout bonus to treasure value
        treasure.value *= 1.1  # 10% value increase when stored in hideout
        self.stored_treasures.append(treasure)
        logging.info(f"Treasure stored in hideout at {self.get_location()}, new value: {treasure.value:.2f}")

    def share_information(self):
        """Share all known information among hunters in this hideout"""
        # Collect all information from hunters
        all_treasures = set()
        all_hideouts = set()
        all_knights = set()

        for hunter in self.hunters:
            all_treasures.update(hunter.known_treasures)
            all_hideouts.update(hunter.known_hideouts)
            all_knights.update(hunter.known_knights)

        # Update hideout's knowledge
        self.known_treasures = list(all_treasures)
        self.known_hideouts = list(all_hideouts)
        self.known_knights = list(all_knights)

        # Share updated information with all hunters
        for hunter in self.hunters:
            hunter.known_treasures = list(all_treasures)
            hunter.known_hideouts = list(all_hideouts)
            hunter.known_knights = list(all_knights)

        logging.info(f"Information shared among {len(self.hunters)} hunters at hideout {self.get_location()}")

    def try_recruit(self) -> Optional[HunterSkill]:
        """Attempt to recruit a new hunter if conditions are met:
        - Hideout has 3-4 hunters
        - At least 2 different skills present
        - 20% chance of recruitment
        """
        if len(self.hunters) >= 3 and len(self.hunters) < 5:
            skills: Set[HunterSkill] = {h.skill for h in self.hunters}
            if len(skills) >= 2 and random.random() < 0.2:  # 20% chance
                # Create new hunter with random existing skill
                new_skill = random.choice(list(skills))
                return new_skill
        return None

    def get_total_wealth(self) -> float:
        """Calculate total wealth stored in this hideout"""
        return sum(treasure.value for treasure in self.stored_treasures)

    def __str__(self) -> str:
        return f"Hideout at {self.get_location()} with {len(self.hunters)} hunters and {len(self.stored_treasures)} treasures"