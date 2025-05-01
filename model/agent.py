from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model.location import Location


class Agent:
    def __init__(self, location: 'Location'):
        self._location = location  # Note the underscore

    def get_location(self) -> 'Location':
        return self._location

    def set_location(self, new_location: 'Location'):
        self._location = new_location

    def __str__(self) -> str:
        return f"{self.__class__.__name__} at {self._location}"