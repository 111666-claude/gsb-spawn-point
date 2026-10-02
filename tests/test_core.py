import unittest

from spawn.core import Spawner


class BasicTest(unittest.TestCase):
    def test_empty_spawner_returns_none(self):
        self.assertIsNone(Spawner(10, 0).choose(0))

    def test_single_point_is_chosen(self):
        spawner = Spawner(10, 0)
        spawner.add_point("a", 0, 0)
        self.assertEqual(spawner.choose(0), "a")

    def test_nearby_allies_of_unknown_point(self):
        self.assertEqual(Spawner(10, 0).nearby_allies("ghost"), 0)

    def test_set_threat_of_unknown_point_is_ignored(self):
        spawner = Spawner(10, 0)
        spawner.set_threat("ghost", 5)
        self.assertEqual(spawner.points, {})

    def test_scanned_starts_at_zero(self):
        self.assertEqual(Spawner(10, 0).scanned_count(), 0)


if __name__ == "__main__":
    unittest.main()
