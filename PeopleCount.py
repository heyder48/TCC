#bliotecas necessarias

from centroidtracker import CentroidTracker
from TrackableObject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2
#import socket

#Socket

#Address = "10.60.66.29"
#Port = 625
#
#try:
#    MySocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#    
#    
#except socket.error:
#    print("Socket nao criado")
#    print(socket.error)
#    exit()
    
#argumentos
    
ap = argparse.ArgumentParser()
ap.add_argument("-p","--prototxt", required=True,
                help = "path to Caffe 'deploy' prototxt file")
ap.add_argument("-m","--model", required=True,
                help = "path to Caffe pre-trained model")
ap.add_argument("-c","--confidence", type = float, default = 0.2,
                help = "minimum probability to filter weak detectons")
ap.add_argument("-s", "--skip-frames", type=int, default = 30, help = "# of skip frames btween detections")

args = vars(ap.parse_args())

Classes = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "dinigtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

print("[info] Carregando Modelo...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

#Estancia o objeto de Video

Video = VideoStream(src=0).start()
time.sleep(2.0)

#dimensoes

W = None
H = None

#estancia o tracker dos centroides

ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
trackers = []
trackableObjects = {}

#numero de frames

totalFrames = 0
totalUp = 0
totalDown = 0
total = 0

fps = FPS().start()

#loop principal

while(True):
    
    frame = Video.read()
    frame = imutils.resize(frame, width=400)
    frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    if W is None or H is None:
        (H,W) = frame.shape[:2]
    
    status = "Waiting"
    rects = []
    
    if totalFrames % args["skip_frames"] == 0:
        
        status = "Detecting"
        trackers = []
        
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W,H), 127.5)
        net.setInput(blob)
        detections = net.forward()
        
        for i in np.arange(0, detections.shape[2]):
            
            confidence = detections[0,0,i,2]
            
            if confidence > args["confidence"]:
                
                idx = int(detections[0,0,i,1])
                
                if Classes[idx] != "person":
                    continue
                
                box = detections[0,0,i,3:7]*np.array([W,H,W,H])
                (startX, startY,endX,endY) = box.astype("int")
                
                tracker = dlib.correlation_tracker()
                rect = dlib.rectangle(startX,startY,endX,endY)
                tracker.start_track(frameRGB, rect)
                
                trackers.append(tracker)
    else:
        
        for tracker in trackers:
            
            status="Tracking"
            
            tracker.update(frameRGB)
            pos = tracker.get_position()
            
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())
            
            rects.append((startX, startY, endX, endY))
            
    cv2.line(frame,(0, H//2),(W,H//2),(0,255,255),2)
    
    objects = ct.update(rects)
    
    for (objectID, centroid) in objects.items():
        
        to = trackableObjects.get(objectID, None)
        
        if to is None:
            to = TrackableObject(objectID, centroid)
        
        else:
            
            y = [c[1] for c in to.centroids]
            direction = centroid[1] - np.mean(y)
            to.centroids.append(centroid)
            
            if not to.counted:
                
                if direction < 0 and centroid[1] < H//2:
                    totalUp += 1
                    to.counted = True
                
                elif direction > 0 and centroid[1] > H//2:
                    totalDown += 1
                    to.counted = True
                    
        trackableObjects[objectID] = to
        total = totalUp + totalDown
        text = "ID {}".format(objectID)
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] -10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
        cv2.circle(frame,(centroid[0],centroid[1]), 4, (0,255,0), -1)
        
    info = [
        ("Up",totalUp),
        ("Down", totalDown),
        ("Status",status),
        ]
    
    for(i,(k,v)) in enumerate(info):
        
        text = "{}:{}".format(k,v)
        cv2.putText(frame, text,(10,H-((i*20)+20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
    
    cv2.imshow("Frame", frame)
    
    
#    message = str(total)+''
#    
#    try:
#        MySocket.sendto(message.encode(),(Address,Port))
#    except socket.error:
#        print("Mensagem nao enviada")
#        print(socket.error)
#        exit()
    
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord("q"):
        break
    
    totalFrames +=1
    fps.update()
    
fps.stop()



cv2.DestroyAllWindows()
    
    
        
                
            
        
        
    
    
    






