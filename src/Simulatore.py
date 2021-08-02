import random
import time
from datetime import datetime, timedelta
from dateutil import tz
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
            Funzione principale che invia dati randomici al server. All'interno vi sono frammenti di codice che
            non sono usati, ma lasciamo per mostrare quello che era il file prima della versione finale e di 
            come potrebbe essere impostato per simulare un guasto ad un sensore.
        """
        # Il seguente codice è stato usato fino alla fine, per avere una data leggibile da umani
        #time_atm = datetime.now(tz.gettz('Europe/Rome'))
        #timestamp = datetime.now(tz.gettz('Europe/Rome'))- timedelta(days=7, minutes=0)
        #pad = timedelta(seconds=20)

        # Per la versione finale utilizziamo il tempo in formato UNIX, che è più facile da gestire
        # Il seguente codice genera un dato generato da un contapersone, ogni 2 minuti, per una settimana
        time_atm = int(time.time())
        timestamp = int(time.time()) - 604800
        pad = 120
        persone = 0 # Questo contatore ci serve per permetterci di non far uscire mai più persone di quante ne sono entrate

        while timestamp < time_atm:
            # Il codice commentato sottostante è servito per simulare
            # la versione del PIR guasto che si può leggere nella sezione 
            # di Grafana presente nella relazione
            
            #if persone < 70:
            #    persone_passate = random.randint(0, 1)
            #    persone += persone_passate
            #else:
            #    persone_passate = 0
            self.send(self.gen_passaggio_object_with_time(random.randint(persone*-1, 20), timestamp))
            persone += persone_passate

            timestamp += pad
            print("Sent:", timestamp)

            # Inviare dati senza nessun tipo di limitatore potrebbe causare perdita di dati
            # dalla parte del ricevitore: una velocità del genere sarebbe raggiungibile nel
            # mondo reale solo da un'insieme molto grande di contapersone, che non è il nostro caso.
            # Abbiamo deciso di ritardare quindi l'invio di ogni dato di 0.3 secondi.
            time.sleep(0.3) 

if __name__ == "__main__":
    contapersone = Simulatore(1, "../config/simulatore.json")
    contapersone.main_procedure()
