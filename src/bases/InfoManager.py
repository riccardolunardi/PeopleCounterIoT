import paho.mqtt.client as mqtt


class InfoManager:
    """
        InfoManager è la classe che ogni classe che si occupa di gestire punti di informazione
        dovrebbe estendere. Questa classe non dovrebbe mai essere instanziata, perché process_message non
        è stato implementato
    """

    def __init__(self, stanza):
        # Imposta subscription per la stanza
        self.broker_connection = self.get_mqtt_client_sub(stanza)
        self.stanza = stanza

    def process_message(self, client, userdata, mid):
        """
        process_message è la funzione principale, dove la classe che estende questa
        implementerà le funzionalità dell'applicazione informativa
        """
        raise NotImplementedError

    def get_mqtt_client_sub(self, sub):
        """
        Genera e ritorna un parzialie client MQTT
        (Parziale perchè la funzione .on_message verrà settata dalla classe che implementerà questa)
        """
        client = mqtt.Client()

        def connect_msg(client, userdata, flags, rc):
            pass # print(f"Connessione al broker ({str(rc)})")

        client.on_connect = connect_msg
        # client.on_message = self.process_message -> Questa scelta dovà essere fatta dalla classe concreta

        client.connect("127.0.0.1", 1883)

        client.subscribe(f"passaggio/{sub}", qos=0)

        return client


if __name__ == '__main__':
    InfoManager("Cucina")
