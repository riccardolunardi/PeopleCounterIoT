import cv2
import dlib
import freenect
import imutils
import numpy as np
import imutils.video

from tracking_src import thread, frame_convert2
from bases.Contapersone import Contapersone
from tracking_src.centroidtracker import CentroidTracker
from tracking_src.trackableobject import TrackableObject


class Kinect(Contapersone):
    """
    Classe che gestisce il contatore di persone realizzato con Kinect e OpenCV
    """

    def __init__(self, id_contapersone=1, config_file="../config/configurazione.json", debug=1):
        if not debug:
            self.grafica_necessaria = False # Si sta avviando lo script da terminale
            print("DEBUG: NO")
        else:
            self.grafica_necessaria = True # Si sta avviando lo script a video/VNC, in modo da poter vedere il feed video del kinect
            print("DEBUG: SI")

        super().__init__(id_contapersone, config_file)

    @staticmethod
    def get_depth():
        """
        Ritorna l'immagine di profondità rilevata dal kinect
        """
        return freenect.sync_get_depth()[0]
        # return mylib.frame_convert2.pretty_depth_cv(freenect.sync_get_depth()[0])

    def main_procedure(self):
        skip_frames = 10

        # Le variabili w e h indicano le dimensione dei frame
        # ricevuti dal kinect; il valore verrà inizializzato
        # al primo frame ricevuto
        w = None
        h = None

        # Inizializziamo il tracker dei centroidi, con i quali tracciamo il movimento degli oggetti sotto al Kinect
        # Inizializziamo un lista per salvare tutti i "dlib correlation trackers" che verrano generati
        # Inizializziamo un dizionario per mappareun ID univoco con un oggetto tracciato (TrackableObject)
        ct = CentroidTracker(max_disappeared=25, max_distance=60)
        trackers = []
        trackable_objects = {}

        # Inizializziamo il numero totale di frame inizializzati, che servirà per capire ogni quanto iniziare il
        # rilevamento di oggetti nell'immagine. Inizializziamo anche il numero di oggetti/persone che sono passate (cioè 0)
        total_frames = 0
        
        total_down = 0
        total_up = 0
        x = []
        empty = []
        empty1 = []

        # Necessario per stabilire il frame rate quando si esce dalla modalità di debug
        fps = imutils.video.FPS().start()

        # Quanto dev'essere piccolo l'area "bianca" (quindi l'area dove si trova qualcosa) prima di iniziare a tracciare un oggetto? E quanto dev'essere grande?
        min_countour_area = 4000
        max_countour_area = 40000

        # Per fare la detection degli oggetti, usiamo la tecnica del "background subtraction".
        # Dopo vari tentativo, createBackgroundSubtractorKNN è risultato essere la migliore funzione per il nostro caso
        back_sub = cv2.createBackgroundSubtractorKNN(history=70, dist2Threshold=200, detectShadows=False)

        # Inizializzazione della classe di thread, da dove leggeremo i frame
        vs = thread.ThreadingClass()
        self.broker_display_connection.loop_start()
        while True:
            frame = vs.read()

            # Se il frame è nullo, c'è un errore, quindi si esce dal ciclo
            if frame is None:
                break

            # Ridimensioniamo il frame, in modo da velocizzare il
            # processing dell'immagine
            frame = imutils.resize(frame, width=300)

            # THRESHOLDING

            # La sogliatura che effettuiamo viene fatta con 2 limiti, e vogliamo far risaltare il range che si trova
            # al loro interno. Questo perché vogliamo evitare di rilevare oggetti troppo bassi (carrelli, animali, etc..) e oggetti troppo alti (porte)

            # Usiamo questo valore per la sogliatura dopo aver effettuato fari test
            # Va ricordato che ogni pixel dell'immagine di profondità ha un valore che va da 0 a 1024 
            current_depth = 715
            threshold = 200

            # L'espressione "frame >= current_depth - threshold" ritorna un array di booleani
            # Facendo l'end con i booleani di questi 2 array
            # otteniamo una sogliatura. 

            # L'array booleano finale rappresenta l'immagine in bianco (True) e nero (False). Tale booleano
            # viene moltiplicato per 255, per poterlo rappresentare come immagine
            frame = 255 * np.logical_and(frame >= current_depth - threshold,
                                         frame <= current_depth + threshold)
            frame = frame.astype(np.uint8)
            frame = back_sub.apply(frame) # Viene applicata la background subtraction

            # Otteniamo un frame da poter mostrare a video, nel caso serva
            if self.grafica_necessaria:
                drawing_frame = frame_convert2.pretty_depth(frame)

            frame = cv2.medianBlur(frame, 11) # Il blur elimina bordi bianchi che potrebbero interferire con la detection

            # Inizializzazione di "h" e "w"
            if w is None or h is None:
                (h, w) = frame.shape[:2]

            # Status rappresenta lo stato in cui è il sistema in un certo momento
            # Inizilializziamo l'array che conterrà i rettangoli ritornati 
            # dal (1) object detector o dal correlation trackers (2)
            status = "Waiting"
            rects = []

            # Controlliamo se è ora di far partire la detection.
            # Non viene sempre attiavata per le limitazioni del Raspberry
            if total_frames % skip_frames == 0:
                # Nuovo stato e inizializzazione dell'array che conterrà i trackers
                status = "Detecting"
                trackers = []

                # Applichiamo una operazione di image processing 
                # all'immagine, chiamata "chiusura", che unisce le operazioni
                # di dilatazione e, successivamente, di erosione.
                # Questo, a livello pratico, va ad "unire" gli oggetti bianchi rilevati uno vicino all'altro:
                # in questo modo verranno riconosciuti come uno stesso oggetto e non rilevati più volte
                kernel = np.ones((10, 10), np.uint8)
                frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, kernel)

                cnts = cv2.findContours(frame.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                # Per ogni oggetto rilevato da cv2.findContours
                for c in cnts:
                    # Se l'area contornata è troppo pocco0la o trop
                    if cv2.contourArea(c) < min_countour_area or cv2.contourArea(c) > max_countour_area:
                        continue
                    
                    print("------------------------------------------------------------")
                    print(cv2.contourArea(c))

                    # Disegna un rettangolo attorno all'oggetto
                    (start_x, start_y, end_x, end_y) = cv2.boundingRect(c)

                    # Dati i vertici del rettangolo, creiamo un tracker tramite dlib
                    # e lo facciamo partire con start_track
                    tracker = dlib.correlation_tracker()
                    rect = dlib.rectangle(start_x, start_y, start_x + end_x, start_y + end_y)
                    tracker.start_track(frame, rect)

                    # Il tracker viene salvato, per potrelo utilizzare
                    # nelle fasi "skip-frame", quindi quando non si è in "Detecting"
                    trackers.append(tracker)

            # Se non siamo in fase di detecting, allora gestiamo i trackers per vedere
            # dove si stanno muovendo gli oggetti
            else:

                for tracker in trackers:
                    # Nuovo stato 
                    status = "Tracking"

                    # Aggiornamento dei tracker e assegnamo la nuova posizione dei vertici del rettangolo
                    tracker.update(frame)
                    pos = tracker.get_position()

                    # Assegnamento dei vertici
                    start_x = int(pos.left())
                    start_y = int(pos.top())
                    end_x = int(pos.right())
                    end_y = int(pos.bottom())

                    # Aggiungiamo il rettangolo aggiornato alla lista globale dei
                    # rettangoli dell'immagine
                    rects.append((start_x, start_y, end_x, end_y))

            # Se si è in debug, una linea viene inserita al centro dell'immagine.
            # Se un oggetto la supera, allora vuol dire che sta entrando/uscendo
            if self.grafica_necessaria:
                cv2.line(drawing_frame, (0, h // 2), (w, h // 2), (255, 255, 255), 3)

            # Tramite i centroidi, associamo il vecchio oggetto a quello nuovo, che si è mosso
            objects = ct.update(rects)

            for (objectID, centroid) in objects.items():
                # Assegnamo il tracker se l'oggetto è già stato salvato nei trackers...
                to = trackable_objects.get(objectID, None)

                # ...altrimenti lo creiamo nuovo
                if to is None:
                    to = TrackableObject(objectID, centroid)

                # Se era già stato salvato, è il momento di controllare la sua direzione
                else:
                    # La differenza tra le cooordinate y ci dirà se l'oggetto
                    # si sta muovendo verso l'alto o verso il basso
                    y = [c[1] for c in to.centroids]
                    direction = centroid[1] - np.mean(y)
                    to.centroids.append(centroid)

                    # L'oggetto in questione è già stato calcolato? 
                    # Altrimenti posso scartarlo per non contarlo più volte
                    if not to.counted:
                        # La direzione dell'oggetto dipende anche da self.direzione_entrata

                        # Se la direzione è negativa (la persona si muove verso il basso)
                        # e il centroide è sopra la riga centrale, lo conto
                        moved_people = 0
                        if direction < 0 and centroid[1] < h // 2:
                            total_up += 1
                            empty.append(total_up)
                            to.counted = True
                        
                            if self.direzione_entrata == "down":
                                moved_people = 1
                            else:
                                moved_people = -1
                            

                        # Se la direzione è positiva (la persona si muove verso l'alto) 
                        #e il centroide è sotto la linea centrale, conta l'oggetto
                        elif direction > 0 and centroid[1] > h // 2:
                            total_down += 1
                            empty1.append(total_down)
                            x = [len(empty1) - len(empty)]
                            to.counted = True

                            if self.direzione_entrata == "down":
                                moved_people = -1
                            else:
                                moved_people = 1
                        
                        # Invio del messaggio MQTT, se effettivamente qualcuno è passato
                        if moved_people:
                            print("Ricezione del messaggio andata a buon fine?", self.send(self.gen_passaggio_object(moved_people)))

                # Salva il tracker per il futuro
                trackable_objects[objectID] = to

                # Se si è in debug, viene disegnato sul frame sia l'id dell'oggetto che il punto "centroide" e viene
                # printato il frame a video
                if self.grafica_necessaria:
                    text = "ID {}".format(objectID)
                    
                    cv2.putText(drawing_frame, text, (centroid[0] - 10, centroid[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.circle(drawing_frame, (centroid[0], centroid[1]), 4, (255, 255, 255), -1)

            if self.grafica_necessaria:
                info = [
                    ("Exit", total_up),
                    ("Enter", total_down),
                    ("Status", status),
                ]

                info2 = [("Total people inside", x), ]

                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(drawing_frame, text, (10, h - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)

                for (i, (k, v)) in enumerate(info2):
                    text = "{}: {}".format(k, v)
                    cv2.putText(drawing_frame, text, (265, h - ((i * 20) + 60)), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                (255, 255, 255), 2)
            
            
                cv2.imshow("Real-Time Monitoring/Analysis Window", drawing_frame)

            key = cv2.waitKey(1) & 0xFF

            # Incrementa il numero totale di frame processati fino ad ora e
            # aggiorna il contatore degli fps
            total_frames += 1
            fps.update()

            # Se la "q" viene premuta, il programma si ferma
            if key == ord("q"):
                break

        # Informazioni sulle performance
        fps.stop()
        print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

        # Chiusura di tutte le fineste (es. feed video di debug)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    device = Kinect(id_contapersone=2)
    device.main_procedure()
