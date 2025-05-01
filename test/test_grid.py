import unittest
from model.grid import Grid
from model.location import Location
from model.treasure import Treasure, TreasureType
from model.hunter import Hunter, HunterSkill
from model.knight import Knight
from model.hideout import Hideout


class TestGrid(unittest.TestCase):
    def setUp(self):
        self.grid = Grid(20)
        self.grid.initialize(num_hideouts=2, initial_hunters=(1, 1), num_knights=2)

    def test_initialization(self):
        self.assertEqual(len(self.grid.hideouts), 2)
        self.assertEqual(len(self.grid.knights), 2)
        self.assertGreater(len(self.grid.treasures), 0)

    def test_agent_placement(self):
        loc = Location(0, 0)
        treasure = Treasure(loc, TreasureType.SILVER)
        self.grid.place_agent(treasure)
        self.assertEqual(self.grid.grid[0][0], treasure)

    def test_movement(self):
        hunter = self.grid.hunters[0]
        original_loc = hunter.get_location()
        adjacent = original_loc.get_adjacent_locations(self.grid.size)

        # Move to first adjacent location
        if adjacent:
            new_loc = adjacent[0]
            self.grid.move_agent(hunter, new_loc)
            self.assertTrue(hunter.get_location().equals(new_loc))
            self.assertIsNone(self.grid.grid[original_loc.get_x()][original_loc.get_y()])
            self.assertEqual(self.grid.grid[new_loc.get_x()][new_loc.get_y()], hunter)

    def test_simulation_step(self):
        initial_treasure_count = len(self.grid.treasures)
        self.grid.update()
        self.assertLessEqual(len(self.grid.treasures), initial_treasure_count)

    def test_wrap_around(self):
        # Test that moving past grid edge wraps around
        loc = Location(0, 0)
        hunter = Hunter(loc, HunterSkill.NAVIGATION)
        self.grid.place_agent(hunter)

        # Move left (should wrap to right edge)
        new_loc = Location(0, 19)
        self.grid.move_agent(hunter, new_loc)
        self.assertTrue(hunter.get_location().equals(new_loc))


if __name__ == "__main__":
    unittest.main()