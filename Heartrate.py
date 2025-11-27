'''
__title__: IoT based Heart rate measurement using Raspberry pi, OpenCV and Thinkspeak Dashboard
__author__ : Ganesh Kumar T K <msm17b034@iiitdm.ac.in> [Modified by Crystal Zhu]
__created.at__: 29.04.2020
__last.modified__: 08.15.2025
'''

import os
import matplotlib
import cv2
import time
import datetime
import picamera2 as cam #If you use picamera use this or leave it
from picamera2 import Picamera2
import numpy as np
from scipy import signal
from scipy.fftpack import fft, fftfreq, fftshift
from sklearn.decomposition import PCA, FastICA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import http.client
import urllib.parse
import urllib.request
import urllib.error
import time as t
from gpiozero import Button


'''
# Thingspeak Dashboard entry function
key = "5VA7JLOGVXWB724R"
def ts(hrate):
    params = urllib.parse.urlencode({'field1': hrate, 'key': key }) 
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = http.client.HTTPConnection("api.thingspeak.com:80")
    try:
         conn.request("POST", "/update", params, headers)
         response = conn.getresponse()
         print (hrate)
         print (response.status, response.reason)
         data = response.read()
         conn.close()
    except:
         print ("connection failed")
def sendData(hr):
    while True:
        t.sleep(15)
        ts(hr)
'''
def runHR():
    class PiCam2Capture:
        def __init__(self, size=(1200,720)):
            self.picam2 = Picamera2()
            cfg = self.picam2.create_preview_configuration( main={"size":size, "format":"RGB886"} )
            self.picam2.start()
        def read(self):
            rgb = self.picam2.capture_array()
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            return True, bgr
        def release(self):
            self.picam2.stop()
            self.picam2.close()
        def is_open(self):
            return self.picam2.started
    try:
        cap = PiCam2Capture()
    except Exception as e:
        print(e)
            
    l = []
    
    #Haar Cascade based Front face & forehead detection
    face_cascade = cv2.CascadeClassifier('/home/rp3/heartpi/haarcascade_frontalface_default.xml') # Full pathway must be used
    firstFrame = None
    time = []
    R = []
    G = []
    B = []
    pca = FastICA(n_components=3)  ## FastICA based Spectra analysis of RGB Components

    '''
    if cap.is_open == False:
        print("Failed to open webcam")
    '''
    frame_num = 0

    #plt.ion()

    for i in range (600):
        ret, frame = cap.read()

        if ret == True:
            frame_num += 1
            if firstFrame is None:            
                start = datetime.datetime.now()
                time.append(0)
                # Take first frame and find face in it
                firstFrame = frame
                cv2.imshow("frame",firstFrame)
                            
                old_gray = cv2.cvtColor(firstFrame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(old_gray, 1.3, 5) 
                if len(faces) == 0:
                    firstFrame = None
                else:
                    for (x,y,w,h) in faces: 
                        x2 = x+w
                        y2 = y+h
                        cv2.rectangle(firstFrame,(x,y),(x+w,y+h),(255,0,0),2)
                        #cv2.imshow("frame",firstFrame)
                        VJ_mask = np.zeros_like(firstFrame)
                        VJ_mask = cv2.rectangle(VJ_mask,(x,y),(x+w,y+h),(255,0,0),-1)
                        VJ_mask = cv2.cvtColor(VJ_mask, cv2.COLOR_BGR2GRAY)
                    ROI = VJ_mask
                    ROI_color = cv2.bitwise_and(ROI,ROI,mask=VJ_mask)
                    #cv2.imshow('ROI',ROI_color)
                    R_new,G_new,B_new,_ = cv2.mean(ROI_color,mask=ROI)
                    R.append(R_new)
                    G.append(G_new)
                    B.append(B_new)
            
            print("analyzing", frame_num)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                #print("break")
                cap.release()
                cv2.destroyAllWindows()
                break
    
            else:
                current = datetime.datetime.now()-start
                current = current.total_seconds()
                time.append(current)
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ROI_color = cv2.bitwise_and(frame,frame)
                cv2.imshow('ROI',ROI_color)
                R_new,G_new,B_new,_ = cv2.mean(ROI_color)
                R.append(R_new)
                G.append(G_new)
                B.append(B_new)
                if frame_num >= 300:
                    N = 300
                    
                    G_std = StandardScaler().fit_transform(np.array(G[-(N-1):]).reshape(-1, 1))
                    G_std = G_std.reshape(1, -1)[0]
                    R_std = StandardScaler().fit_transform(np.array(R[-(N-1):]).reshape(-1, 1))
                    R_std = R_std.reshape(1, -1)[0]
                    B_std = StandardScaler().fit_transform(np.array(B[-(N-1):]).reshape(-1, 1))
                    B_std = B_std.reshape(1, -1)[0]
                    T = 1/(len(time[-(N-1):])/(time[-1]-time[-(N-1)]))
                    X_f=pca.fit_transform(np.array([R_std,G_std,B_std]).transpose()).transpose()
                    N = len(X_f[0])
                    yf = fft(X_f[1])
                    yf = yf/np.sqrt(N)
                    xf = fftfreq(N, T)
                    xf = fftshift(xf)
                    yplot = fftshift(abs(yf))
                    
                    '''
                    print("fftshi abs")
                    plt.figure(1)
                    plt.savefig('/tmp/heartrate_plota'+str(frame_num)+'.png')
                    print("fire")
                    plt.gcf().clear()
                    print("ppppppppp")
                    '''

                    fft_plot = yplot
                    fft_plot[xf<=0.75] = 0
                    data=str(xf[fft_plot[xf<=4].argmax()]*60)+' bpm'
                    
                    l.append(xf[fft_plot[xf<=4].argmax()]*60)
                    
                    '''
                    print(data)
                    plt.plot(xf[(xf>=0) & (xf<=4)], fft_plot[(xf>=0) & (xf<=4)])
                    plt.savefig('/tmp/heartrate_plotb'+str(frame_num)+'.png')
                    plt.pause(0.0001)
                    ts(data)
                    '''
                    
    with open ("output.txt", "w") as f:
        for item in l:
            f.write(str(item) + "\n")
    print("list leng is this:", len(l))
    
    cap.release()
    cv2.destroyAllWindows()
    
#runHR()