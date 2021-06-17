import random
import unittest
from datetime import datetime

from dateutil import tz

import sys
sys.path.insert(1, '..')
from Contapersone import Contapersone, ContapersoneNotFound
from Passaggio import Passaggio
from Simulatore import Simulatore


def gen_simple_object():
    return Passaggio(timestamp=datetime.fromtimestamp(1622122598, tz=tz.gettz("Europe/Rome")).isoformat(),
                     persone_contate=2,
                     stanza="Cucina",
                     dispositivo="Kinect")


class ContapersoneTest(unittest.TestCase):

    def test_contapersone(self):
        contapersone = None

        try:
            contapersone = Contapersone(0, "../config/simulatore.json")
        except ContapersoneNotFound as e:
            print(e)
        else:
            contapersone = Contapersone(1, "../config/simulatore.json")

        self.assertEqual(True, contapersone.send(gen_simple_object()))

    def test_simulatore(self):
        contapersone = Simulatore(1, "../config/simulatore.json")
        contapersone.main_procedure()
        self.assertEqual(True, bool(random.randint(0, 1)))


if __name__ == '__main__':
    unittest.main()
