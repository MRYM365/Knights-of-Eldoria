from __future__ import annotations
from typing import List
from model.agent import Agent
import random


class Hideout(Agent):
    def __init__(self, location: 'Location'):
        super().__init__(location)
        self.hunters = []  # List of hunters in this hideout
        self.stored_treasures = []  # List of treasures stored here
        self.known_treasures = []  # Locations of known treasures
        self.known_hideouts = []  # Locations of other known hideouts
        self.known_knights = []  # Locations of recent knight sightings

    def add_hunter(self, hunter):
        if len(self.hunters) < 5:
            self.hunters.append(hunter)
            return True
        return False

    def remove_hunter(self, hunter):
        if hunter in self.hunters:
            self.hunters.remove(hunter)
            return True
        return False

    def store_treasure(self, treasure):
        self.stored_treasures.append(treasure)

    def share_information(self):
        """Share all known information among hunters in this hideout"""
        for hunter in self.hunters:
            hunter.known_treasures = list(set(hunter.known_treasures + self.known_treasures))
            hunter.known_hideouts = list(set(hunter.known_hideouts + self.known_hideouts))
            hunter.known_knights = list(set(hunter.known_knights + self.known_knights))

    def try_recruit(self):
        """Attempt to recruit a new hunter if conditions are met"""
        if len(self.hunters) >= 3 and len(self.hunters) < 5:
            skills = {h.skill for h in self.hunters}
            if len(skills) >= 2 and random.random() < 0.2:
                # Create new hunter with random existing skill
                new_skill = random.choice(list(skills))
                return new_skill
        return None

    def __str__(self) -> str:
        return f"Hideout at {self.get_location()} with {len(self.hunters)} hunters and {len(self.stored_treasures)} treasures"