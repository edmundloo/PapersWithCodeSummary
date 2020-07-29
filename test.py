import unittest

from models.cached_data import CachedData


class TestCachedData(unittest.TestCase):
    def test_all_functions(self):
        return_value = 10

        cache = CachedData(lambda: return_value)
        self.assertEqual(cache.cache_populated, False)
        self.assertEqual(cache.cached_data, None)

        cache.get_data()
        self.assertEqual(cache.cache_populated, True)
        self.assertEqual(cache.cached_data, 10)

        return_value = 5
        cache.update_data()
        self.assertEqual(cache.cache_populated, True)
        self.assertEqual(cache.cached_data, 5)

        cache.get_data()
        self.assertEqual(cache.cache_populated, True)
        self.assertEqual(cache.cached_data, 5)


if __name__ == "__main__":
    unittest.main()
