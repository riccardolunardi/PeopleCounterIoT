import json
import copy
from datetime import datetime
from dateutil import tz


class Passaggio:
    """
        Rappresenta il passaggio di una persona rilevato dal contapersone.
        Contiene altri dati rilevanti che potranno essere utili nell'aggregazione dei dati (stanza, dispostivo, timestamp)
    """

    def __init__(self,
                 timestamp=None,
                 persone_contate=0,
                 stanza="default",
                 dispositivo="default"):
        """
        Costruttore di classe principale.
        Inizializza l'oggetto contenente i dati principali
        """
        if not timestamp:
            self.time = datetime.now(tz.gettz('Europe/Rome')).isoformat()
        else:
            self.time = timestamp
            
        self.persone_contate = persone_contate
        self.stanza = stanza
        self.dispositivo = dispositivo

    def serialize_db(self) -> str:
        passaggio_dict = copy.deepcopy(self.__dict__)
        passaggio_dict["measurement"] = "contapersone"
        passaggio_dict["fields"] = {"persone_contate": passaggio_dict["persone_contate"]}
        passaggio_dict["tags"] = {"stanza": passaggio_dict["stanza"], "dispositivo": passaggio_dict["dispositivo"]}
        del passaggio_dict["persone_contate"]
        del passaggio_dict["stanza"]
        del passaggio_dict["dispositivo"]

        return json.dumps(passaggio_dict, default=str)

    def serialize(self) -> str:
        return json.dumps(self.__dict__, default=str)
        
    @staticmethod
    def deserialize(json_object):
        """
        Il JSON ricevuto viene deserializzato, ritornando un oggetto
        di tipo Passaggio. Le 'keys' dell'oggetto JSON sono i nomi degli attributi
        dell'oggetto Passaggio
        """
        x = json.loads(json_object, object_hook=lambda d: Passaggio(**d))
        return x

    def __str__(self) -> str:
        """
        Ritorna l'oggetto Passaggio sottoforma di stringa, leggibile in modo umano
        """
        return (f"{self.timestamp} - "
                f"Persone contate: {self.persone_contate} - "
                f"Stanza: {self.stanza} - "
                f"Dispositivo: {self.dispositivo}")
