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


class ScoringTest(unittest.TestCase):
    def test_lower_threat_wins(self):
        spawner = Spawner(10, 0)
        spawner.add_point("a", 0, 0, threat=5)
        spawner.add_point("b", 100, 0, threat=0)
        self.assertEqual(spawner.choose(0), "b")

    def test_allies_boost_score(self):
        spawner = Spawner(10, 0)
        spawner.add_point("a", 0, 0, threat=0)
        spawner.add_point("b", 100, 0, threat=4)
        for x in (1, 2, 3):
            spawner.add_ally(x, 0)
        self.assertEqual(spawner.choose(0), "a")

    def test_tie_breaks_by_id(self):
        spawner = Spawner(10, 0)
        spawner.add_point("b", 0, 0)
        spawner.add_point("a", 100, 0)
        self.assertEqual(spawner.choose(0), "a")

    def test_negative_score_still_chosen(self):
        spawner = Spawner(10, 0)
        spawner.add_point("a", 0, 0, threat=9)
        self.assertEqual(spawner.choose(0), "a")


class AllyEdgeTest(unittest.TestCase):
    def test_ally_exactly_on_radius_counts(self):
        spawner = Spawner(10, 0)
        spawner.add_point("a", 0, 0)
        spawner.add_ally(10, 0)
        self.assertEqual(spawner.nearby_allies("a"), 1)

    def test_ally_just_outside_radius_does_not_count(self):
        spawner = Spawner(10, 0)
        spawner.add_point("a", 0, 0)
        spawner.add_ally(10.0001, 0)
        self.assertEqual(spawner.nearby_allies("a"), 0)

    def test_diagonal_boundary_counts(self):
        spawner = Spawner(10, 0)
        spawner.add_point("a", 0, 0)
        spawner.add_ally(6, 8)
        self.assertEqual(spawner.nearby_allies("a"), 1)


class CooldownTest(unittest.TestCase):
    def test_point_in_cooldown_is_skipped(self):
        spawner = Spawner(10, 5000)
        spawner.add_point("a", 0, 0)
        spawner.add_point("b", 100, 0)
        self.assertEqual(spawner.choose(0), "a")
        self.assertEqual(spawner.choose(1), "b")

    def test_all_cooling_returns_none(self):
        spawner = Spawner(10, 5000)
        spawner.add_point("a", 0, 0)
        spawner.choose(0)
        self.assertIsNone(spawner.choose(1))

    def test_cooldown_expires(self):
        spawner = Spawner(10, 5000)
        spawner.add_point("a", 0, 0)
        spawner.choose(0)
        self.assertEqual(spawner.choose(5000), "a")

    def test_cooldown_boundary_still_cooling(self):
        spawner = Spawner(10, 5000)
        spawner.add_point("a", 0, 0)
        spawner.choose(0)
        self.assertIsNone(spawner.choose(4999))


class RotationTest(unittest.TestCase):
    def test_rotation_penalty_rotates_points(self):
        spawner = Spawner(10, 0, rotation_penalty=3)
        spawner.add_point("a", 0, 0)
        spawner.add_point("b", 100, 0)
        self.assertEqual(spawner.choose(0), "a")
        self.assertEqual(spawner.choose(1), "b")

    def test_picks_accumulate_penalty(self):
        spawner = Spawner(10, 0, rotation_penalty=3)
        spawner.add_point("a", 0, 0)
        spawner.add_point("b", 100, 0)
        picks = [spawner.choose(t) for t in range(4)]
        self.assertEqual(picks, ["a", "b", "a", "b"])
        self.assertEqual(spawner.picks("a"), 2)
        self.assertEqual(spawner.picks("b"), 2)

    def test_repeatable_sequence(self):
        def run():
            spawner = Spawner(10, 0)
            spawner.add_point("a", 0, 0)
            spawner.add_point("b", 100, 0)
            spawner.add_ally(1, 0)
            return [spawner.choose(t) for t in range(6)]
        self.assertEqual(run(), run())


class ScanCostTest(unittest.TestCase):
    def test_scanned_does_not_scale_with_chooses(self):
        spawner = Spawner(10, 0)
        spawner.add_ally(1, 0)
        for index in range(3000):
            spawner.add_point("p-%d" % index, index, 0)
        for _ in range(3000):
            spawner.choose(0)
        self.assertLessEqual(spawner.scanned_count(), 6000)
