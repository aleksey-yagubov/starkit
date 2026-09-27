import gc
import math
import random
import tracemalloc
import unittest

import starkit

SIZES = [40.2, 0, 0, 0, 99, 99, 0, 13.7, 23.8, 0]
LIMITS = [[-2666, 2666], [-3199, 444], [-3851, 1481],
          [-5333, 0], [-1333, 2310], [-711, 711]]
POSE = [0, -62, -180, 0, 0, -1, 0]


class SolverTests(unittest.TestCase):
    def test_nominal_matches_upstream(self):
        expected = [-0.03953553826100017, 0.6607929200912015,
                    -1.321585840182403, -0.6607929200912015,
                    -0.03953553826100017, 0.0]
        result = starkit.alpha_calculation(*POSE, SIZES, LIMITS)
        self.assertEqual(len(result), 1)
        for actual, reference in zip(result[0], expected):
            self.assertAlmostEqual(actual, reference, places=12)

    def test_exact_root_fallback(self):
        sizes = SIZES.copy()
        sizes[7] = 0
        limits = [row.copy() for row in LIMITS]
        limits[1] = [-444, 444]
        result = starkit.alpha_calculation(0, -40.2, -180, 0, 0, -1, 0, sizes, limits)
        self.assertTrue(result)
        self.assertAlmostEqual(result[0][4], 0, places=12)

    def test_endpoint_fallback(self):
        sizes = SIZES.copy()
        sizes[7] = 0
        for pair in ([0, 444], [-444, 0], [0, 0]):
            limits = [row.copy() for row in LIMITS]
            limits[1] = pair
            self.assertTrue(starkit.alpha_calculation(0, -40.2, -180, 0, 0, -1, 0, sizes, limits))

    def test_unreachable(self):
        self.assertEqual(starkit.alpha_calculation(1e6, *POSE[1:], SIZES, LIMITS), [])

    def test_bad_arguments(self):
        with self.assertRaises(TypeError):
            starkit.alpha_calculation()
        for sizes, limits in (([], LIMITS), (SIZES, []), (SIZES, [[0]] * 6),
                              (SIZES, [[1, -1]] * 6), ([0] * 10, LIMITS),
                              (SIZES[:-1] + [math.inf], LIMITS)):
            with self.assertRaises(ValueError):
                starkit.alpha_calculation(*POSE, sizes, limits)
        for bad in (math.nan, math.inf, -math.inf):
            with self.assertRaises(ValueError):
                starkit.alpha_calculation(bad, *POSE[1:], SIZES, LIMITS)
        with self.assertRaises(ValueError):
            starkit.alpha_calculation(0, -62, -180, 0, 0, 0, 0, SIZES, LIMITS)
        with self.assertRaises(TypeError):
            starkit.alpha_calculation(*POSE, [object()] * 10, LIMITS)

    def test_solutions_are_independent(self):
        limits = [[-10000, 10000] for _ in range(6)]
        limits[1] = LIMITS[1].copy()
        result = starkit.alpha_calculation(*POSE, SIZES, limits)
        self.assertGreater(len(result), 1)
        self.assertEqual(len(result), len({id(row) for row in result}))
        self.assertTrue(all(len(row) == 6 for row in result))
        previous = result[1].copy()
        result[0][0] = 123
        self.assertEqual(result[1], previous)

    def test_random_finite_and_limited(self):
        rng = random.Random(124)
        for _ in range(5000):
            pose = [rng.uniform(-100, 100), rng.uniform(-100, -20),
                    rng.uniform(-230, -120), rng.uniform(-.3, .3),
                    rng.uniform(-.2, .2), -1, rng.uniform(-.3, .3)]
            result = starkit.alpha_calculation(*pose, SIZES, LIMITS)
            for row in result:
                self.assertEqual(len(row), 6)
                self.assertTrue(all(math.isfinite(x) for x in row))
                for index in range(1, 4):
                    lo, hi = LIMITS[5-index]
                    self.assertTrue(lo <= row[index]*1698 <= hi)

    def test_no_retained_python_allocations(self):
        tracemalloc.start()
        for _ in range(100):
            starkit.alpha_calculation(*POSE, SIZES, LIMITS)
        gc.collect()
        before = tracemalloc.get_traced_memory()[0]
        for _ in range(20000):
            starkit.alpha_calculation(*POSE, SIZES, LIMITS)
        gc.collect()
        after = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        self.assertLess(after-before, 65536)


if __name__ == "__main__":
    unittest.main()
