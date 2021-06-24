class TrackableObject:
	"""
		Rappresenta un oggetto che verrà trackato
	"""
	def __init__(self, objectID, centroid):
		# Assegno un object ID per poterlo riconoscere in futuro
		# Assegno il primo centroide alla lista di possibili centrodi per questo oggetto
		self.objectID = objectID
		self.centroids = [centroid]

		# Booleano che indica se l'oggetto è già stato contato (dalla main_procedure)
		self.counted = False