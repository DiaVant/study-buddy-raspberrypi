from time import time
from time import sleep
from gpiozero import PWMLED, PhaseEnableMotor, OutputDevice, Button
from enum import Enum
import threading
from pygame import mixer
import sys
sys.path.append("/home/rp3/heartpi")
import Heartrate
import subprocess


_topHeartRate = 120

class S(Enum):
    OFF = -1
    START = 0
    STUDY = 1
    BREAK = 2
    CALM = 3
status = S.OFF
_stopEvent = threading.Event()
_stopReason = None

b1 = PWMLED(17)
b2 = PWMLED(27)
all_r = PWMLED(23)
all_g = PWMLED(24)
all_b = PWMLED(25)
button1 = Button(16, bounce_time = 0.05)
button2 = Button(12, bounce_time = 0.05)
IN1 = OutputDevice(22)
IN2 = OutputDevice(9)
IN3 = OutputDevice(11)
IN4 = OutputDevice(5)
motor_seq = [
    [1,1,0,0],
    [0,1,1,0],
    [0,0,1,1],
    [1,0,0,1]
    ]
rgb_list = [
    (1,1,1), #start
    (.8,.8,.2), #study
    (1,0,0), #break
    (0,0,1) #calm
]
song_list = [
    "Joyful Trills.wav",
    "Chilling in the Rain.wav",
    "Pirate Thunder.wav",
]
mixer.init()

_totalStudyTime = 0 #tracked across 

_maxCycle = 0
_maxStudy = 0
_maxBreak = 0
_curCycle = 0

_startT = 0

#converts seconds -> minutes
def stm(seconds):
    return seconds / 60
def mts(minutes):
    return minutes * 60
#takes the current status and displays corresponding light
def setAll(mode=0):
    AllOff()
    global status
    match mode:
        case 0:
            rgb = rgb_list[status.value]
        case 1: #on
            rgb = (1,1,1)
    #print("rgb", {status}, rgb)
    all_r.value = rgb[0]
    all_g.value = rgb[1]
    all_b.value = rgb[2]
def AllOn():
    b1.on()
    b2.on()
    setAll(1)
def AllOff():
    b1.off()
    b2.off()
    all_r.value = 0
    all_b.value = 0
    all_g.value = 0
    IN1.value = 0
    IN2.value = 0
    IN3.value = 0
    IN4.value = 0

def PrintMsg(mode="off"): #off, all, calm
    global _totalStudyTIme, _curCycle, _maxCycle, _maxStudy, _maxBreak
    match mode: ##when hard quit study session
        case "off":
            print(f"See you next study session~")
        case "all":
            print(f"Congratulations! You've studied {stm(_maxStudy)*_maxCycle} minutes, making your total studied time an impressive {stm(_totalStudyTime)} minutes! WOW!")
            print("Press the bottom button when you're reading to study again <3")
            print("(To say goodbye to study buddy, press the top button\\)")
        case "study":
            print(f"{_curCycle} out of {_maxCycle} cycles finished, awesome Job! You've successfully studied for {stm(_maxStudy)} minutes, now time for a {stm(_maxBreak)} minute break <3")
    
def Off():
    global status, _maxCycle, _maxStudy, _maxBreak, _curCycle, _startT, _stopEvent, _stopReason
    status = S.OFF

    AllOff()
   
    _stopEvent.clear()
    _stopReason = None

    _maxCycle = 0
    _maxStudy = 0
    _maxBreak = 0
    _curCycle = 0
    _startT = 0

def Start():
    global status, _maxStudy, _maxBreak, _maxCycle, _topHeartRate
    status = S.START
    
    setAll()

    if ( _totalStudyTime == 0):
        age = int(input("How old are you? ") )

    _maxStudy = mts(int(input("How long do you want to study today? (minutes) ") )) 
    _maxBreak = mts(int(input("How long do you want to go on break for between study blocks? (minutes) ") )) 
    _maxCycle = int(input("How many times do you want to repeat this study cycle? ") )

    print("Study session starting in...")
    for i in range(1,4):
        print(i)
        sleep(1)
    
    Study(_maxStudy)

_curSongInd = 0
def playSong(ind):
    mixer.music.load(song_list[ind] )
    mixer.music.play(loops=-1)
    print(f"Now playing: {song_list[_curSongInd]}" )
def songController():
    global _curSongInd
    while not _stopEvent.is_set():
        if button2.is_pressed:
            _curSongInd = _curSongInd+1 if _curSongInd < len(song_list)-1 else 0
            playSong(_curSongInd)
            if(_stopEvent.wait(0.3) ):
                break #debounce 
    mixer.music.stop()
def countdown(duration=60):
    global _stopReason, _startT, _stopEvent
    while time() - _startT < duration and not _stopEvent.is_set():
        remaining = int(duration - (time() - _startT) )
        mins, secs = divmod(remaining, 60)
        print(f"{mins:02}:{secs:02}", end="\r")
        if(_stopEvent.wait(1)):
            return     
    if not _stopEvent.is_set():
        print("\nTime's up!")
        _stopEvent.set()
        _stopReason = "finish"

def bpmTracker():
    while not _stopEvent.is_set():
        Heartrate.runHR()

        bpmL = []
        cc = 0
        with open ("output.txt", 'r') as f:   
            for line in f:
                bpm = float(line.strip())
                if (bpm >= _topHeartRate):
                    cc += 1
                bpmL.append(bpm)
        
        if (cc >= len(bpmL)/2):
            b1.pulse(3)
            b2.pulse(3)
        else:
            b1.off()
            b2.of()

def Study(studyT):
    global _startT, status, _stopReason, _stopEvent, _curCycle, _maxCycle, _maxStudy, _maxBreak, _totalStudyTime
    status = S.STUDY

    print(f"Get ready to study! \nPROGRESS: {_curCycle + 1} of {_maxCycle} cycles")
    
    setAll()

    _stopEvent.clear()
    _stopReason = None
    _startT = time()
    
    t1 = threading.Thread(target=songController)
    t2 = threading.Thread(target=countdown, args=(studyT,))
    #OPEN FOR BETA TESTING
    t3 = threading.Thread(target=bpmTracker)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join() ##make sure this breaks when the other ones break
    
    AllOff() #make sure this doesn't mak anything look bad
    stopT = time()
    passedT = stopT - _startT
    _stopEvent.clear()
    match _stopReason:
        case "calm":
            #print("calm")
            Calm(_maxStudy - passedT)
        case _:
            #print("finished@")
            _totalStudyTime += _maxStudy
            _curCycle+=1
            if (_curCycle < _maxCycle): ##middle of a cycle
                PrintMsg("study")
                Break()
            else: ##FINISHED ALL CYCLES!!!!
                PrintMsg("all")
                Off()
    _stopReason = None

def Break ():
    global status, _maxBreak, _maxStudy, _startT
    status = S.BREAK

    #print("at break")
    setAll()
    
    _startT = time()
    countdown(_maxBreak)

    Study(_maxStudy)
    
def BlueShow():
    while not _stopEvent.is_set():
        b1.pulse(4,0)
        b2.pulse(4,0)
        if(_stopEvent.wait(4)): break
        b1.on()
        b2.on()
        if(_stopEvent.wait(4)): break
        b1.pulse(0,4)
        b2.pulse(0,4)
        if(_stopEvent.wait(4)): break
        b1.off()
        b2.off()
        if(_stopEvent.wait(4)): break
    #print("blueshow stop")
def MotorShow():
    while not _stopEvent.is_set():
        for step in motor_seq:
            IN1.value = step[0]
            IN2.value = step[1]
            IN3.value = step[2]
            IN4.value = step[3]
            if(_stopEvent.wait(1)): break
    #print("motorshow stop")
def Calm(studyT=60):
    global status, _stopReason
    status = S.CALM

    print("Calm Mode Activated <3")
    _stopEvent.clear()
    _stopReason = None
    
    setAll()
    
    t1 = threading.Thread(target=BlueShow)
    t2 = threading.Thread(target=MotorShow)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    mins, secs = divmod(studyT, 60) #####MAKE THIS HOURS + MINUTES
    mins = int(mins)
    secs = int(secs)
    print(f"Resuming Study session, you have {mins} minutes and {secs} seconds left!")
    
    _stopEvent.clear()
    _stopReason = None
    Study(studyT)

def Pressed1():
    global _stopReason
    match status:
        case S.STUDY:
            _stopReason = "calm"
            print("printed")
            subprocess.run(["xdotool", "key", "q"])
        case S.CALM:
            _stopReason = "study"
        case S.OFF:
            _stopReason = "start"
    _stopEvent.set()    
def Pressed2():
    global status, _stopReason
    if (status == S.OFF):
        _stopReason = "quit"
        _stopEvent.set()
button1.when_pressed = Pressed1
button2.when_pressed = Pressed2

def main():
    print("Welcome to Studdy Buddy! :)")    
    while True:
        Start()
        
        status = S.OFF
        while not _stopEvent.is_set():
            if (_stopEvent.wait(60)):
                break
        if(_stopReason == "quit"):
            break
        _stopEvent.clear()
        _stopReson = None

    
if __name__=="__main__":
    main()
