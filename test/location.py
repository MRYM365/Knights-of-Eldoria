import unittest
from model.location import Location


class TestLocation(unittest.TestCase):
    def test_location_creation(self):
        loc = Location(3, 5)
        self.assertEqual(loc.get_x(), 3)
        self.assertEqual(loc.get_y(), 5)

    def test_location_equality(self):
        loc1 = Location(2, 4)
        loc2 = Location(2, 4)
        loc3 = Location(2, 5)
        self.assertTrue(loc1.equals(loc2))
        self.assertFalse(loc1.equals(loc3))

    def test_adjacent_locations(self):
        loc = Location(1, 1)
        adjacent = loc.get_adjacent_locations(5)
        self.assertEqual(len(adjacent), 8)  # 8 adjacent locations
        expected = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
        actual = [(l.get_x(), l.get_y()) for l in adjacent]
        self.assertEqual(set(actual), set(expected))


if __name__ == "__main__":
    unittest.main()