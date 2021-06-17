import unittest
from datetime import datetime

from dateutil import tz

import sys
sys.path.insert(1, '..')
from Passaggio import Passaggio


def gen_simple_object():
    return Passaggio(timestamp=datetime.fromtimestamp(1622122598, tz=tz.gettz("Europe/Rome")).isoformat(),
                     persone_contate=2,
                     stanza="Cucina",
                     dispositivo="Kinect")


class PassaggioTest(unittest.TestCase):

    def test_oggetto_passaggio(self):
        entrata = Passaggio(persone_contate=2, stanza="Cucina", dispositivo="Kinect")
        print(entrata)
        self.assertEqual(entrata.persone_contate, 2)
        self.assertEqual(entrata.stanza, "Cucina")
        self.assertEqual(entrata.dispositivo, "Kinect")

    def test_str_passaggio(self):
        entrata = gen_simple_object()

        self.assertEqual(str(entrata),
                         "2021-05-27T15:36:38+02:00 - " +
                         "Persone contate: 2 - " +
                         "Stanza: Cucina - " +
                         "Dispositivo: Kinect")

    def test_serialize(self):
        entrata = gen_simple_object()
        self.assertEqual(entrata.serialize(),
                         "{\"timestamp\": \"2021-05-27T15:36:38+02:00\", " +
                         "\"persone_contate\": 2, " +
                         "\"stanza\": \"Cucina\", " +
                         "\"dispositivo\": \"Kinect\"}")


if __name__ == '__main__':
    unittest.main()
