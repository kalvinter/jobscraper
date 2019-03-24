import unittest
import os
from tests.unittest_config import TEST_DB_PATH


if __name__ == '__main__':
    if os.path.isfile(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    test_suite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(test_suite)
