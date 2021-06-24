import cv2, threading, queue, freenect

class ThreadingClass:
  """
    Questa classe è necessaria per aumentare il numero di FPS
    che il Raspberry può processare
  """

  def __init__(self):
    self.q = queue.Queue() # Coda dove verranno salvati i frame arrivati, ma non ancora processati

    t = threading.Thread(target=self._reader)
    t.daemon = True
    t.start()

  # read the frames as soon as they are available
  # this approach removes OpenCV's internal buffer and reduces the frame lag
  def _reader(self):
    """
      Legge tutti i frame appena sono disponibili, evitando il buffer
      interno di OpenCV, riducendo il lag tra i frame
    """
    while True:
      frame = freenect.sync_get_depth()[0] # Leggi l'immagine di profondità
      if not self.q.empty():
        try:
          self.q.get_nowait()
        except queue.Empty:
          pass
      self.q.put(frame) # Salva l'immagine di profondità nella coda

  def read(self):
    """
      Ritorna il primo frame della coda, rimuovendolo
      dalla stessa
    """
    return self.q.get()
