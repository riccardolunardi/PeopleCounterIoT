import json
import time
import paho.mqtt.client as mqtt
import dateutil.parser as dp
from influxdb import InfluxDBClient


class RicezioneDati:

   
    """
    Cosruttore che istanzia la connessione con influxDB e mqtt
    client_db: variabile che connette come il client su InfluxDB
    mqtt_connection: variabile che sfrutta i dati ricevuti dal client con mqtt 
    """
    def __init__(self):
        self.client_db = InfluxDBClient(host='localhost', port=8086)
        self.mqtt_connection = self.get_mqtt_client_sub()
        self.persone = {}
        self.mqtt_connection.loop_forever()

    
    def process_message(self, client, userdata, stringa_json):
            """
            Metodo che invia a InfluxDB i dati ricevuti dal contapersone. Viene aggiornato il contatore di 
            persone (self.persone), per stanza, in modo da permettere l'invio al
            server del numero esatto di persone all'interno della stanza.

            stringa_json: stringa che contiene tutte le informazioni sulle persone contate
            """
        
            persone_contate = json.loads(stringa_json.payload)

            try:
                self.persone[persone_contate["tags"]["stanza"]] += persone_contate["fields"]["persone_contate"]
            except KeyError as keyerror: # Il dizionario va inizializzato, prima di essere utilizzato
                self.persone[persone_contate["tags"]["stanza"]] = persone_contate["fields"]["persone_contate"]

            persone_contate["fields"]["persone_contate"] = self.persone # A InfluxDB inviamo il numero di persone presenti nella stanza, non il numero di persone entrate/uscite

            print(persone_contate, type(persone_contate))
            print("Scrivo nel db...")
            print(self.persone)
            
            #self.client_db.write_points([persone_contate], database='contapersone', time_precision='s', protocol='json')


    def get_mqtt_client_sub(self):
        """
        Metodo di inizializzazione di un client MQTT. Viene anche assegnata la funzione process_message,
        che viene eseguita quando arriva un messaggio a cui il client è iscritto
        """
        client = mqtt.Client()
        client.on_message = self.process_message # Assegnamento funzione process_message

        client.connect("localhost", 1883) # Collegamento al broker MQTT
        client.subscribe(f"passaggiodb", qos=0) # Iscrizione al topic

        return client


if __name__ == "__main__":
    ricevitore = RicezioneDati()