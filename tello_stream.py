from threading import Thread
import socket
import sys
import time
import cv2
import Tello3
import imutils
import numpy as np
from imutils import video

def getLargest(found):
    out = (0, 0, 0, 0)
    for (x, y, width, height) in found:
        if width + height > out[2] + out[3]:
            out = (x, y, width, height)
    return out

"""
    Returns the instruction to send to the drone,
    given the center position of the face
"""
def getInstruction():
    width  = video.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # used to determine whether we'll change the drone in x or y axis
    h_diff = height // 2 - center[1]
    w_diff = width // 2 - center[0]

    direction = ""

    # too small difference to make a decision
    if max(abs(h_diff), abs(w_diff)) < 100:
        return None

    # more height difference than horizontal difference
    if abs(h_diff) > abs(w_diff):
        direction = "down 20" if h_diff < 0 else "up 20"
    else:
        direction = "cw 10" if w_diff < 0 else "ccw 10"
    
    return direction

def sendInstruction():
    while True:
        if center != None:
            inst = getInstruction()
            Tello3.send(inst)
            time.sleep(0.3)

            if area > 70000:
                Tello3.send("back 20")
                time.sleep(0.5)
            elif area < 30000: 
                Tello3.send("forward 20")
                time.sleep(0.5)

center = None
area = 0

stop_data = cv2.CascadeClassifier('frontal.xml') 

Thread(target = sendInstruction).start()

video = video.WebcamVideoStream("udp://@0.0.0.0:11111").start()

while True:
    try:
        frame = video.read()
        found = stop_data.detectMultiScale(frame, minSize = (100, 100))
        
        if len(found) != 0:
            (x, y, width, height) = getLargest(found)    
            cv2.rectangle(frame, (x, y), (x + height, y + width), (255, 255, 255), 5)

            # this is the center, which will be used to send the correct instruction to the drone
            center = (x + width//2, y + height//2)
            area = width * height
        else:
            center = None

        # draw (with rectangle around the face if found any)
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
    except Exception as err:
        video.stop()
        center = None
        cv2.destroyAllWindows()
        print ('\nExit Video . . .\n', err)
        break
