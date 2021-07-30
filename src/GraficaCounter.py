mport os
from tkinter import Canvas, Message, Tk, CENTER
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

    
        print(f"Persone all'interno della {self.stanza.lower()}: \n{str(self.current_people_inside)}")
        self.broker_connection.loop_start()
        

    def process_message(self, client, userdata, msg_mqtt):
        """
        Per ogni messaggio arrivato, viene aggiornato il numero di persone all'interno della stanza.
        Viene aggiornato anche il numero che viene visualizzato
        """
        movimento = Passaggio.deserialize(msg_mqtt.payload)
        self.current_people_inside += movimento.persone_contate
        print(movimento)
        cv.itemconfigure('rand', text=device.current_people_inside)

        if self.current_people_inside >= 2:
            cv.config(bg="red")
            msg.config(bg="red")
            root['bg']='red'
        else:
            cv.config(bg="green")
            msg.config(bg="green")
            root['bg']='green'
        
        root.update()
         
if __name__ == "__main__":
    device = RealTimeCounter(stanza="Cucina", current_people_inside=0)
    root = Tk()
    root.geometry("800x600")
    root['bg']='green'
    
    cv = Canvas(root, width=800, height=600, bg="green",highlightthickness=0)
    #styles = Font(family="calibri",size=30,weight="bold")
    textId = cv.create_text(400, 300, font=("Josefin Sans", 200), fill="white", tag='rand', justify="center")  # added a tag
    cv.itemconfigure('rand', text=device.current_people_inside)

    msg = Message(root, text="Limite di persone = 10", width= "600", bg= "green", foreground="white", font=("Josefin Sans", 20), justify=CENTER)
    msg.pack()
    cv.pack()
    root.attributes('-fullscreen', True)
    root.mainloop()
