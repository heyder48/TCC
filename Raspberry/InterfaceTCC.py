################ People count Using Tensorflow Classifier ################################
#Author: Heyder Araujo
#Description:
#This program uses a Tensorflow classifier to peerform people detection
#and count the number of people in the video feed.
#The model used is the ssdlite_mobilenet_v2_coco_2018_05_09 downloaded from the Tensorflow model zoo.
#This code is based on the exemple code from the Tensorflow repositori on Github:
# https://github.com/tensorflow/models/blob/master/research/object_detection/object_detection_tutorial.ipynb


# import packages

import os
import cv2
import numpy as np
import tensorflow.compat.v1 as tf
import argparse
import sys
import socket



import serial

tf.disable_v2_behavior()
scoreMin = 0.4
tempRoomAux = 20
tempExtAux = 20
tempExtRoomAux = 20
powerAux = 1.5

#Serial Comunication
try:
    ser = serial.Serial('/dev/ttyACM0', 9600)
    ser.reset_input_buffer()

except:
    print("Serial Error")
    exit()
    

#UDP comunication

Address = "192.168.1.114"
Port = 9090
MyAddress = "192.168.1.117"
MyPort = 25000

try:
    MySocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
   
   
except socket.error:
   print("Socket nao criado")
   print(socket.error)
   exit()



#Camera constants
# Normal resolution:
IM_WIDTH = 1280
IM_HEIGHT = 720
#Smaller Resolution for a litle better FPS rate:
#IM_WIDTH = 640    
#IM_HEIGHT = 480

sys.path.append('..')

# Import utilites
from utils import label_map_util


# Name of the directory containing the object detection module we're using
MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'

# Grab path to current working directory
CWD_PATH = os.getcwd()

# Path to frozen detection graph .pb file, which contains the model that is used
# for object detection.
PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

# Path to label map file
PATH_TO_LABELS = os.path.join(CWD_PATH,'data','mscoco_label_map.pbtxt')

# Number of classes the object detector can identify
NUM_CLASSES = 90

## Load the label map.
# Label maps map indices to category names, so that when the convolution
# network predicts `1`, we know that this corresponds to `person`.
# Here we use internal utility functions, but anything that returns a
# dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

# Load the Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    sess = tf.Session(graph=detection_graph)


# Define input and output tensors (i.e. data) for the object detection classifier

# Input tensor is the image
image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

# Output tensors are the detection boxes, scores, and classes
# Each box represents a part of the image where a particular object was detected
detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

# Each score represents level of confidence for each of the objects.
# The score is shown on the result image, together with the class label.
detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

# Number of objects detected
num_detections = detection_graph.get_tensor_by_name('num_detections:0')

# Initialize frame rate calculation
frame_rate_calc = 1
freq = cv2.getTickFrequency()
font = cv2.FONT_HERSHEY_SIMPLEX

#This function perform the detection and return the boxes, the scores, the classes and thenumber of detections


def detect(image):
    image_np_expanded = np.expand_dims(image, axis=0)
    (boxes, scores, classes, num) = sess.run(
        [detection_boxes, detection_scores, detection_classes, num_detections],
        feed_dict={image_tensor: image_np_expanded}) # Using the model for detection

    im_height, im_width,_ = image.shape
    boxes_list = [None for i in range(boxes.shape[1])]
    for i in range(boxes.shape[1]):
        boxes_list[i] = (int(boxes[0,i,0] * im_height),
                    int(boxes[0,i,1]*im_width),
                    int(boxes[0,i,2] * im_height),
                    int(boxes[0,i,3]*im_width))

    return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])
    
def Arduino(sensores):
    
    
    if(sensores.in_waiting > 0):
        Data = sensores.readline()
        #data = ''.join(chr(i) for i in Data)
        data = Data.decode()
        data = data.split('\t')
        
        
        tempRoom = float(data[0])
        tempExt = float(data[1])
        tempExtRoom = float(data[2])
        power = float(data[3].split()[0])/1000
    
    return tempRoom, tempExt, tempExtRoom, power

def Send2Arduino(sensores,comand):
    
    sensores.write(str(comand).encode())
    
    
    

def UDPsend(message):
    
    try:
        
        MySocket.sendto(message.encode(),(Address,Port))
        
    except socket.error:
        print("Mensagem nao enviada")
        print(socket.error)
        exit()

def UDPreceive(Myaddress,MyPort):
    try:
                
        command, addr = MySocket.recvfrom(1024)
        
        return command.decode()
    except:
        print("Unable to recive")
        exit()
    
    
    

# Initialize USB webcam feed
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
ret = camera.set(3,IM_WIDTH)
ret = camera.set(4,IM_HEIGHT)
# MySocket.bind((Myaddress,MyPort))

while(True):

    t1 = cv2.getTickCount()
    count = 0

    # Acquire frame 
    ret, frame = camera.read()
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #uses the detect fuction to expand the dimensions  of the frame and perform the object detection
    boxes, scores, classes, num = detect(frame_rgb)
    
    #if the detected object is a person the count variable is increased and boxes are put around the person
    for i in range(len(boxes)):
        if np.any(classes[i] == 1) and np.any(scores[i]>scoreMin):
            
            box = boxes[i]
            cv2.rectangle(frame, (int(box[1]),int(box[0])),(int(box[3]),int(box[2])),(25,30,200),2)
            cv2.putText(frame,'Score = {0:.2f} %'.format(scores[i]*100),(box[1],box[0]),cv2.FONT_HERSHEY_SIMPLEX, 1.25,(255,255,0),2,cv2.LINE_AA)
            count+=1
    
    # Show the results
    
    print("Valor predito: {}".format(count))
    
    cv2.putText(frame,'Count = '+str(count),(10,400),cv2.FONT_HERSHEY_SIMPLEX, 1.25,(255,255,0),2,cv2.LINE_AA)
    cv2.putText(frame,"FPS: {0:.2f}".format(frame_rate_calc),(30,50),font,1,(255,255,0),2,cv2.LINE_AA)
    
    try:
        
        tempRoom, tempExt, tempExtRoom, power = Arduino(ser)  
            
        tempRoomAux = tempRoom
        tempExtAux = tempExt
        tempExtRoomAux = tempExtRoom
        powerAux = power
        
        print("Temperatura Sala ={0:.2f} C".format(tempRoom))
        print("Temperatura Extena ={0:.2f} C" .format(tempExt))
        print("Temperatura Sala Externa ={0:.2f} C".format(tempExtRoom))
        print("Potencia ={0:.2f} kW \n".format(power))
        
        message = str(tempRoom)+' '+str(tempExt)+' '+str(tempExtRoom)+' '+str(power)+' '+str(count)
            
    except:
        print("Temperatura Sala ={0:.2f} C".format(tempRoomAux))
        print("Temperatura Extena ={0:.2f} C" .format(tempExtAux))
        print("Temperatura Sala Externa ={0:.2f} C".format(tempExtRoomAux))
        print("Potencia ={0:.2f} kW \n".format(powerAux))
        
        message = str(tempRoomAux)+' '+str(tempExtAux)+' '+str(tempExtRoomAux)+' '+str(powerAux)+' '+str(count)
        pass
    

    
    
         
    UDPsend(message)
        
    cv2.imshow('Object detector', frame)
    
    t2 = cv2.getTickCount()
    time1 = (t2-t1)/freq
    frame_rate_calc = 1/time1
    
    # Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break
    

camera.release()

cv2.destroyAllWindows()
    

    
    
    
    
    









