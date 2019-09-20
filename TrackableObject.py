class TrackableObject:
    
    def __init__(self, objectID, centroid):
        
        #Guarda a ID do objeto e inicializa a lista de centroides
        self.objectID = objectID
        self.centroids = [centroid]
        
        #indica se o o bjeto ja foi contado
        self.counted = False