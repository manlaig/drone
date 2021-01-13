import threading 
import socket
import sys
import time
import cv2
from matplotlib import pyplot as plt

def getLargest(found):
    out = (0, 0, 0, 0)
    for (x, y, width, height) in found:
        if width + height > out[2] + out[3]:
            out = (x, y, width, height)
    return out

video = cv2.VideoCapture("udp://@0.0.0.0:11111")
video.set(cv2.CAP_PROP_FPS, 1)

stop_data = cv2.CascadeClassifier('frontal.xml') 

print ('\r\n\r\nTello Python3 Video Stream.\r\n')

while True:
    try:
        ret, frame = video.read()
        if ret:
            img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
            found = stop_data.detectMultiScale(img_gray, minSize = (150, 150))
            
            if len(found) != 0: 
                (x, y, width, height) = getLargest(found)    
                cv2.rectangle(frame, (x, y), (x + height, y + width), (255, 255, 255), 5)
                # this is the center, which will be used to send the correct instruction to the drone
                cv2.circle(frame, (x + width//2, y + height//2), 2, (255, 255, 255), 5)

            """       
            # Creates the environment of  
            # the picture and shows it 
            plt.subplot(1, 1, 1) 
            plt.imshow(img_rgb) 
            plt.show() 
            """
            cv2.imshow("frame", frame)
            cv2.waitKey(1)
    except Exception as err:
        video.release()
        cv2.destroyAllWindows()
        print ('\nExit Video . . .\n', err)
        break
