import json
from datetime import datetime
from dateutil import tz


class Passaggio:

    def __init__(self,
                 timestamp=datetime.now(tz.gettz('Europe/Rome')).isoformat(),
                 persone_contate=0,
                 stanza="default",
                 dispositivo="default"):
        """
        Costruttore di classe principale.
        Inizializza l'oggetto contenente i dati principali
        """
        self.timestamp = timestamp
        self.persone_contate = persone_contate
        self.stanza = stanza
        self.dispositivo = dispositivo

    def serialize(self) -> str:
        return json.dumps(self.__dict__, default=str)

    def __str__(self) -> str:
        return (f"{self.timestamp} - "
                f"Persone contate: {self.persone_contate} - "
                f"Stanza: {self.stanza} - "
                f"Dispositivo: {self.dispositivo}")
