import json
import paho.mqtt.client as mqtt

from .Passaggio import Passaggio


class ContapersoneNotFound(Exception):
    """
    Eccezione alzata quando il Contapersone non viene trovato

    Attributes:
        campo -- campo con cui si ha cercato il Contapersone
        message -- Spiegazione dell'errore
    """

    def __init__(self, campo, message="Non è stato trovato il Contapersone tramite questo valore"):
        self.campo = campo
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.campo}'


class Contapersone:
    """
        Contapersone è la classe che ogni classe che si occupa di contare effettivamente le persone che entrano/escono
        dovrebbe estendere. Questa classe non dovrebbe mai essere instanziata, perché main_procedure non
        è stato implementato
    """

    def __init__(self, id_contapersone, config_file):
        with open(config_file, "r") as config:
            settings = json.load(config)

        display_ip = ""
        for stanza, info_stanza in settings.items():
            for contapersone in info_stanza["contapersone"]:
                if contapersone["id"] == id_contapersone:
                    display_ip = info_stanza["broker"]
                    self.id_contapersone = id_contapersone
                    self.nome = contapersone["nome"]
                    self.stanza = stanza
                    self.dispositivo = contapersone["dispositivo"]

                    try:
                        self.direzione_entrata = contapersone["direzione_entrata"]
                    except:
                        pass

                    break
            else:
                raise ContapersoneNotFound(id_contapersone,
                                           "Non è stato possibile trovare il Contapersona tramite questo id")

        assert display_ip != ""
        self.broker_display_connection = Contapersone.get_mqtt_client("Display", display_ip)

    def send(self, nuovo_passaggio: Passaggio):
        """
        Invia il messaggio contenente l'oggetto Passaggio al broker.
        Se il risultato, dopo l'invio, ha un valore che non è di successo, il client prova a riconnettersi.
        Questo dopo alcuni test, sembra sistemare gli errori che possono accadere più comunemente.
        """
        # QoS = 0, retain = False
        print(f"Trying to publish {nuovo_passaggio.serialize()}...")

        (result, _) = self.broker_display_connection.publish(f"passaggio/{self.stanza}", nuovo_passaggio.serialize(), qos=0)

        if result == mqtt.MQTT_ERR_SUCCESS:
            return True
        
        print("Errore:",result," - Riconnessione...")
        self.broker_display_connection.reconnect()
        return False # Ritorna false in caso serva al chiamante

    def gen_passaggio_object(self, movimenti):
        """
        Genera un'oggetto Passaggio a partire dall'argomento 'movimenti' e l'oggetto corrente
        """
        return Passaggio(persone_contate=movimenti, stanza=self.stanza, dispositivo=self.dispositivo)

    def main_procedure(self):
        """
        main_procedure è la funzione principale, dove la classe che estende questa
        implementerà le funzionalità del contapersone
        """
        return NotImplementedError

    @classmethod
    def get_mqtt_client(cls, pub_id, ip_client):
        """
        Genera e ritorna un client MQTT e setta le funzioni on_connect e on_publish
        """
        client = mqtt.Client(client_id=pub_id)

        def connect_msg(client, userdata, flags, rc):
            print('Connected to Broker (%s)' % str(rc))

        def publish_msg(client, userdata, mid):
            print(f"Message published!")

        client.on_connect = connect_msg
        client.on_publish = publish_msg

        broker = ip_client.split(":")[0]
        port = int(ip_client.split(":")[1])

        client.connect(broker, port)

        return client
