from threading import Thread
import socket
import sys
import time
import cv2
import Tello3

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
    width  = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # used to determine whether we'll change the drone in x or y axis
    h_diff = height // 2 - center[1]
    w_diff = width // 2 - center[0]

    direction = ""

    # too small difference to make a decision
    if max(abs(h_diff), abs(w_diff)) < 50:
        return None

    # more height difference than horizontal difference
    if abs(h_diff) > abs(w_diff):
        direction = "down 20" if h_diff < 0 else "up 20"
    else:
        direction = "cw 5" if w_diff < 0 else "ccw 5"
    
    return direction


def sendInstruction():
    while True:
        if center != None:
            inst = getInstruction()
            print(inst)
            Tello3.send(inst)
            time.sleep(1)

def readFrames():
    while True:
        ret, f = video.read()
        if ret == True:
            frame = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        
center = None
frame = None
ret = False

stop_data = cv2.CascadeClassifier('frontal.xml') 

Thread(target = sendInstruction).start()

video = cv2.VideoCapture("udp://@0.0.0.0:11111")

Thread(target = readFrames).start()

# video.set(cv2.CAP_PROP_BUFFERSIZE, 0)

while True:
    # print(frame == None)
    try:
        # ret, frame = video.read()
        if ret:
            # print("printing 2")
            found = stop_data.detectMultiScale(frame, minSize = (150, 150))
            
            if len(found) != 0: 
                (x, y, width, height) = getLargest(found)    
                cv2.rectangle(frame, (x, y), (x + height, y + width), (255, 255, 255), 5)
                # this is the center, which will be used to send the correct instruction to the drone
                center = (x + width//2, y + height//2)
                # cv2.circle(frame, center, 2, (255, 255, 255), 5)
            else:
                center = None
        else:
            center = None
        
        if frame != None:
            print("printing")
            cv2.imshow("frame", frame)
            cv2.waitKey(1)
            
    except Exception as err:
        video.release()
        center = None
        cv2.destroyAllWindows()
        print ('\nExit Video . . .\n', err)
        break
