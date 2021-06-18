import os

from bases.Passaggio import Passaggio
from bases.InfoManager import InfoManager

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class RealTimeCounter(InfoManager):
    """
        Esempio di implementazione di InfoManager.
        Il compito è quello di mostrare, a terminale, quante persone sono presenti
        all'interno della stanza "Cucina"
    """

    def __init__(self, stanza, current_people_inside = 0):
        super().__init__(stanza)
        self.current_people_inside = current_people_inside
        self.broker_connection.on_message = self.process_message
        
        cls()
        print(f"Persone all'interno della {self.stanza.lower()}: \n{str(self.current_people_inside)}")
        self.broker_connection.loop_forever()

    def process_message(self, client, userdata, msg):
        """
        Per ogni messaggio arrivato, viene aggiornato il numero di persone all'interno della stanza.
        Viene aggiornato anche il numero che viene visualizzato
        """
        movimento = Passaggio.deserialize(msg.payload)
        self.current_people_inside += movimento.persone_contate

        cls()
        print(f"Persone all'interno della {self.stanza.lower()}: \n{str(self.current_people_inside)}")

if __name__ == "__main__":
    device = RealTimeCounter(stanza="Cucina", current_people_inside=1)