class Location:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y

    def get_x(self) -> int:
        return self._x

    def get_y(self) -> int:
        return self._y

    def set_x(self, new_x: int):
        self._x = new_x

    def set_y(self, new_y: int):
        self._y = new_y

    def equals(self, other_location: 'Location') -> bool:
        return self._x == other_location.get_x() and self._y == other_location.get_y()

    def __str__(self) -> str:
        return f"({self._x}, {self._y})"

    def get_adjacent_locations(self, grid_size: int) -> list['Location']:
        """Returns all 8 adjacent locations (including diagonals) with grid wrapping"""
        adjacent = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip current location
                new_x = (self._x + dx) % grid_size
                new_y = (self._y + dy) % grid_size
                adjacent.append(Location(new_x, new_y))
        return adjacent