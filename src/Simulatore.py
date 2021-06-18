import random
import time

from bases.Contapersone import Contapersone

class Simulatore(Contapersone):
    """
        Esempio di implementazione della classe Contapersone.
        L'obiettivo è di simulare un contapersone.
        Ogni x secondi viene inviato un oggetto generato randomicamente e viene inviato al broker
    """
    def __init__(self, id_contapersone, config_file):
        super().__init__(1, "../config/simulatore.json")

    def main_procedure(self):
        """
            Funzione principale che invia dati randomici al server
        """
        while True:
            time.sleep(random.randint(5, 25))
            self.send(self.gen_passaggio_object(random.randint(-9, 10)))

if __name__ == "__main__":
    contapersone = Simulatore(1, "../config/simulatore.json")
    contapersone.main_procedure()
