import random
import time

from Contapersone import Contapersone
from Passaggio import Passaggio


class Simulatore(Contapersone):
    def __init__(self, id_contapersone, config_file):
        super().__init__(1, "config/simulatore.json")

    def main_procedure(self):
        while True:
            time.sleep(random.randint(5, 25))
            self.send(self.gen_passaggio_object(random.randint(-9, 10)))
