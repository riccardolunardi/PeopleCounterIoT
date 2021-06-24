from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker:
	def __init__(self, max_disappeared=50, max_distance=50):
		# Inizializzazione del contatore di ID, che parte da 0.
		# Si incrementarà ogni volta che si aggiunge un nuovo oggetto
		self.next_object_id = 0
		
		# Teniamo traccia degli oggetti tramite OrderedDict (dizionari che tengono conto dell'ordine di inserimento) 
		self.objects = OrderedDict()
		# Teniamo traccia anche degli oggetti che spariscono (e per quanti frame)
		self.disappeared = OrderedDict()

		# Limite di frame che un oggetto può sparire dal feed video prima che sia considerato "sparito"
		# Se sparisce lo eliminiamo dagli oggetti di cui teniamo traccia
		self.max_disappeared = max_disappeared
		
		# Massima distanza tra un centroide e un oggetto.
		# Se la distanza è superiore, l'oggetto sarà considerato "sparito"
		self.max_distance = max_distance

	def register(self, centroid):
		# Salvataggio di un oggetto (tramite il suo centroide)
		self.objects[self.next_object_id] = centroid
		self.disappeared[self.next_object_id] = 0
		self.next_object_id += 1 # Il prossimo oggetto avrà un ID diverso

	def deregister(self, object_id):
		# Cancelliamo il centroide di tale oggetto, perché probabilemnte considerato "sparito"
		del self.objects[object_id]
		del self.disappeared[object_id]

	def update(self, rects):
		# Se la lista dei rettangoli è vuota...
		if len(rects) == 0:
			# ...cicla su tutti gli oggetti e segnamo che per un frame sono spariti
			for object_id in list(self.disappeared.keys()):
				self.disappeared[object_id] += 1

				# Se un oggetto è sparito per più frame di quello che è
				# il limite consentito, allora viene eliminato
				if self.disappeared[object_id] > self.max_disappeared:
					self.deregister(object_id)

			# Ritorna gli oggetti aggiornati ed esci subito dalla funziona,
			# perché tanto non c'è niente da aggiornare
			return self.objects

		# Inizializzazione di un array per i centrodi di questo frame
		input_centroids = np.zeros((len(rects), 2), dtype="int")

		# Per ogni rettangolo...
		for (i, (startX, startY, endX, endY)) in enumerate(rects):
			# Deriva il centroide tramite i vertici
			cX = int((startX + endX) / 2.0)
			cY = int((startY + endY) / 2.0)
			input_centroids[i] = (cX, cY)

		# Se non si stanno tracciando altri 
		# oggetti, salviamo i centroidi appena calcolati
		if len(self.objects) == 0:
			for i in range(0, len(input_centroids)):
				self.register(input_centroids[i])

		# Altrimenti, se ce ne sono altri, con i
		# dati che abbiamo raccolto in questo frame, dobbiamo
		# aggiornare la posizione dei centrodi del frame
		# precedente
		else:
			# Otteniamo la lista degli ID dei centroidi correnti
			object_ids = list(self.objects.keys())
			object_centroids = list(self.objects.values())

			# Dati i vecchi centroidi e i nuovi, calcoliamo
			# la distanza tra di loro. Il nostro obiettivo è quello di
			# accoppiare i centroidi vecchi con quelli nuovi
			distance = dist.cdist(np.array(object_centroids), input_centroids)

			# Per fare un accoppiamento corretto, dobbiamo prima trovare
			# il valore (della distanza) più piccolo per ogni riga (asse x),
			# poi ordinare gli indici dal più piccolo al più grande
			rows = distance.min(axis=1).argsort()

			# Ripetiamo la stessa cosa sulle colonne, 
			# i valori per la rispettiva riga (asse X)
			cols = distance.argmin(axis=1)[rows]

			# In questo modo otteniamo gli indici corretti per identificare poi, nel ciclo for, la distanza.

			# Usiamo i set per tenere traccia delle colonne e delle righe
			# di cui abbiamo già tenuto conto
			used_rows = set()
			used_cols = set()

			# Iteriamo ogni coppia di riga e colonna. Possiamo farlo in
			# questo modo perché le righe e le colonne sono ordinate in modo tale
			# che l'i-esimo elemento di rows corrisponde al punto dell'i-esimo
			# elemento di cols 
			# Ogni iterazione significa una elaborazione del centroide di un certo oggetto
			for (row, col) in zip(rows, cols):
				# Ignoriamo la riga e la colonna se è già stata esaminata
				if row in used_rows or col in used_cols:
					continue

				# Se la distanza tra i due è più grande della distanza
				# massima consentita, allora prosegui. Non ha senso
				# associare i centroidi allo stesso oggetto
				if distance[row, col] > self.max_distance:
					continue

				# A questo punto, associa l'ID dell'oggetto della
				# row corrente e associa il nuovo centroide
				object_id = object_ids[row]
				self.objects[object_id] = input_centroids[col]
				self.disappeared[object_id] = 0  # L'oggetto è appena apparso, quindi va 0

				# Salviamo la riga e la colonna correnti per non
				# processarli di nuovo
				used_rows.add(row)
				used_cols.add(col)

			# Computiamo la differenza tra il centroide corrente, con
			# le righe e le colonne non ancora elaborate 
			unused_rows = set(range(0, distance.shape[0])).difference(used_rows)
			unused_cols = set(range(0, distance.shape[1])).difference(used_cols)

			# Nel caso il numero di centroidi dei frame precedenti
			# sia maggiore o uguale del numero di centroidi corrente,
			# dobbiamo aggiornare accordatamente self.disappeared
			if distance.shape[0] >= distance.shape[1]:

				for row in unused_rows:
					object_id = object_ids[row]
					self.disappeared[object_id] += 1

					# Deregistriamo se necessario
					if self.disappeared[object_id] > self.max_disappeared:
						self.deregister(object_id)

			# Se il numero è maggiore, aggiungiamo i nuovi centroidi
			else:
				for col in unused_cols:
					self.register(input_centroids[col])

		# Viene ritornato il set di centroidi aggiornati
		return self.objects