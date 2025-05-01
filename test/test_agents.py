import unittest
from model.location import Location
from model.hunter import Hunter, HunterSkill
from model.knight import Knight
from model.treasure import Treasure, TreasureType
from model.hideout import Hideout


class TestAgents(unittest.TestCase):
    def setUp(self):
        self.location = Location(5, 5)
        self.grid_size = 20

    def test_hunter_creation(self):
        hunter = Hunter(self.location, HunterSkill.NAVIGATION)
        self.assertEqual(hunter.skill, HunterSkill.NAVIGATION)
        self.assertEqual(hunter.stamina, 100.0)
        self.assertIsNone(hunter.carried_treasure)

    def test_hunter_movement(self):
        hunter = Hunter(self.location, HunterSkill.ENDURANCE)
        new_location = Location(6, 5)
        hunter.move(new_location)
        self.assertTrue(hunter.get_location().equals(new_location))
        self.assertAlmostEqual(hunter.stamina, 98.0)  # 2% stamina decrease

    def test_knight_chase(self):
        knight = Knight(self.location)
        hunter = Hunter(Location(5, 6), HunterSkill.STEALTH)
        target = knight.should_chase([hunter])
        self.assertEqual(target, hunter)

    def test_treasure_decay(self):
        treasure = Treasure(self.location, TreasureType.GOLD)
        initial_value = treasure.value
        treasure.decay_value()
        self.assertAlmostEqual(treasure.value, initial_value * 0.999)

    def test_hideout_capacity(self):
        hideout = Hideout(self.location)
        self.assertTrue(hideout.can_accommodate())

        # Add 5 hunters
        for _ in range(5):
            hunter = Hunter(self.location, HunterSkill.NAVIGATION)
            hideout.add_hunter(hunter)

        self.assertFalse(hideout.can_accommodate())


if __name__ == "__main__":
    unittest.main()