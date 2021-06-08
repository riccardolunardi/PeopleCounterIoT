import paho.mqtt.client as mqtt


class InfoManager:
    """
        InfoManager è la classe che ogni classe che si occupa di gestire punti di informazione
        dovrebbe estendere. Questa classe non dovrebbe mai essere instanziata, perché process_message non
        è stato implementato
    """

    def __init__(self, stanza):
        # Imposta subscription per la stanza
        self.broker_connection = InfoManager.get_mqtt_client_sub(stanza)

    @classmethod
    def process_message(client, userdata, mid):
        raise NotImplementedError

    @classmethod
    def get_mqtt_client_sub(cls, sub):
        client = mqtt.Client()

        def connect_msg(client, userdata, flags, rc):
            print(f"Connessione al broker ({str(rc)})")

        client.on_connect = connect_msg
        client.on_message = InfoManager.process_message

        client.connect("127.0.0.1", 1883)

        client.subscribe(f"passaggio/{sub}", qos=0)

        return client
