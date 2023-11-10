import cv2
import ctypes
import pyautogui
import time
import datetime
import numpy
from ctypes import windll
from ctypes import wintypes
from multiprocessing import Process
from pynput import keyboard

#################################################### Config ####################################################### 

classes = None
with open("coco.names", "r") as f:
    classes = f.read().strip().split("\n")
net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")
toplist, winlist = [], []
hpZero = (194, 188)
hpFull = (hpZero[0] + 92, hpZero[1])
mpZero = (hpZero[0] + 4, hpZero[1]  + 33)
mpFull = (mpZero[0] + 92,hpZero[1] + 33)
hpZero2 = (194, 70)
hpFull2 = (hpZero2[0] + 92, hpZero2[1])
mpZero2 = (hpZero2[0] + 4, hpZero2[1]  + 33)
mpFull2 = (mpZero2[0] + 92,hpZero2[1] + 33)
enemyPosition = (hpZero[0] + 523,hpZero[1] - 15)
enemyHpPosition = (hpZero[0] + 518,hpZero[1] - 5)
fighterPosition = (hpZero[0], hpZero[1] + 802)
healerPosition = hpZero2

#################################################### Help Functions ####################################################### 

def CheckPixel(index, value, lowValue, highValue, y, percent, screenshot):
    return GetPixel((round(lowValue + (highValue - lowValue) * percent/100), y), screenshot)[index] < value
  
def GetPixel(position, screenshot):
    return screenshot.getpixel(position)
   
def ReadFromFile(fileName):
    with open(fileName) as file:
        return file.read()

def Screenshot():
    return pyautogui.screenshot().convert("RGB")

def WriteToFile(fileName, input):
    with open(fileName, "w") as file:
        file.write(str(input))   
   
############################################################################################### Mouse and Keyboard ##############################################################################################################    
      
#Keyboard: keyboard.Controller = keyboard.Controller()   
MOUSEEVENTF_RIGHTDOWN = 0x0008 
MOUSEEVENTF_RIGHTUP = 0x0010 
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000
one = 0x31
two = 0x32
three = 0x33
four = 0x34
five = 0x35
six = 0x36
seven = 0x37
e = 0x45
k = 0x4B
q = 0x51
s = 0x53
skills = [three, four, five, six, seven]
user32 = ctypes.WinDLL('user32', use_last_error=True)

INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_UNICODE     = 0x0004
KEYEVENTF_SCANCODE    = 0x0008

MAPVK_VK_TO_VSC = 0

wintypes.ULONG_PTR = wintypes.WPARAM

class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        # some programs use the scan code even if KEYEVENTF_SCANCODE
        # isn't set in dwFflags, so attempt to map the correct code.
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))

LPINPUT = ctypes.POINTER(INPUT)

def _check_count(result, func, args):
    if result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return args

user32.SendInput.errcheck = _check_count
user32.SendInput.argtypes = (wintypes.UINT, # nInputs
                             LPINPUT,       # pInputs
                             ctypes.c_int)  # cbSize  
  
def MouseClick():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    InputSleep()
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    InputSleep()
   
def MoveMouseTo(position):
    x_normalized = int(65535 * (position[0] / 1920))
    y_normalized = int(65535 * (position[1] / 1080))
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, x_normalized, y_normalized, 0, 0)   
    InputSleep()
   
def MouseRightDown():
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
    InputSleep()
    
def MouseRightUp():   
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
    InputSleep()
   
def MouseMove():
    windll.user32.mouse_event(1, 100, 0, 0, 0)
    InputSleep()
    windll.user32.mouse_event(1, 100, 0, 0, 0)
    InputSleep()
    windll.user32.mouse_event(1, 100, 0, 0, 0)
   
def KeyDown(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    time.sleep(0.035)
   
def PressKey(hexKeyCode):
    KeyDown(hexKeyCode)
    ReleaseKey(hexKeyCode)

def ReleaseKey(hexKeyCode):
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode,
                            dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))
    time.sleep(0.035)
    
def On_press(key):
    if any([key in z for z in [{keyboard.Key.shift, keyboard.KeyCode(char='ö')}, {keyboard.Key.shift, keyboard.KeyCode(char='Ö')}]]):
        if ReadFromFile("stop.txt") == "0":
            WriteToFile("stop.txt", "1")
        else:
            WriteToFile("stop.txt", "0")      
 
def InputSleep():
    time.sleep(0.02) 
     
############################################################################################### Main Functions #####################################################################################################

def Attack():
    #ts = datetime.datetime.now()
    screenshot = Screenshot()
    #while MonsterNotHit(screenshot):
        #PressKey(one)
        #PressKey(two)
        #RefreshProcess(50, screenshot)
        #screenshot = Screenshot() 
        #if CheckStuck(ts):
            #return 1
    ts = datetime.datetime.now()
    rgb = GetPixel(enemyPosition, screenshot)
    while True:
        for i in range(5):
            PressKey(skills[i])
            screenshot = Screenshot()
            rgb = GetPixel(enemyPosition, screenshot)
            if rgb[0] < 220 or rgb[1] < 220 or rgb[2] < 220:
                return 0
            PressKey(two)
        RefreshProcess(50, screenshot)
        if CheckStuck(ts):
            return 1

def CheckStuck(ts):
    if (datetime.datetime.now() - ts).total_seconds() > 20:
        KeyDown(s)
        time.sleep(3)
        ReleaseKey(s)
        time.sleep(0.1)
        Rotate()
        return True
    return False

def FiestaBot():
    WriteToFile("stop.txt", "1")
    while True:
        if ReadFromFile("stop.txt") == "0":
            if FindMonster():
                Attack()
            else:
                Rotate()
        else:
            InputSleep()    
        
def FindMonster():
    PressKey(k)
    pixel = GetPixel(enemyPosition, Screenshot())
    return pixel[0] > 220 and pixel[1] > 220 and pixel[2] > 220 

def MonsterNotHit(screenshot): 
    return GetPixel(enemyHpPosition, screenshot)[0] > 60  

def RefreshProcess(percent, screenshot):
    # Healer healq
    if CheckPixel(0, 120, hpZero[0], hpFull[0], hpFull[1], percent + 20, screenshot):
        TargetHealer()
        PressKey(one)     
        TargetFighter()
    # Stone heal
    if CheckPixel(0, 120, hpZero[0], hpFull[0], hpFull[1], percent, screenshot):
        PressKey(q)
    if CheckPixel(2, 120, mpZero[0], mpFull[0], mpFull[1], (percent - 20), screenshot):
        PressKey(e)
    # Healer stone heal
    if CheckPixel(0, 120, hpZero2[0], hpFull2[0], hpFull2[1], percent, screenshot):
        TargetHealer()
        PressKey(q)
        if CheckPixel(2, 120, mpZero2[0], mpFull2[0], mpFull2[1], percent, screenshot):
            PressKey(e)
        TargetFighter()
    elif CheckPixel(2, 120, mpZero2[0], mpFull2[0], mpFull2[1], (percent - 20), screenshot):
        TargetHealer()
        PressKey(e)
        TargetFighter()
        
def Rotate():
    MoveMouseTo((760, 200))
    MouseRightDown()
    MouseMove()
    MouseRightUp()
      
def TargetFighter():
    MoveMouseTo(fighterPosition)
    MouseClick()
   
def TargetHealer():
    MoveMouseTo(healerPosition)
    MouseClick()  

############################################################################################### Start ##############################################################################################################      
       
if __name__ == '__main__':    
    processBot = Process(target = FiestaBot)
    processListener = keyboard.Listener(on_press=On_press)
    processBot.start()
    processListener.start()
    processBot.join()
    processListener.join()