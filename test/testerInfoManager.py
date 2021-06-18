import unittest
import sys

sys.path.insert(1, '../src/bases')
from InfoManager import InfoManager


class InfoManagerTest(unittest.TestCase):

    def test_costruttore_infomanager(self):
        InfoManager("Cucina")


if __name__ == '__main__':
    unittest.main()
