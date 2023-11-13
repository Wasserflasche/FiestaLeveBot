import cv2
import ctypes
import os
import pyautogui
import time
import datetime
import numpy as np
from ctypes import windll
from ctypes import wintypes
from multiprocessing import Process
from pynput import keyboard
from typing import Tuple

resolution = (1920, 1080)
currentPath = os.path.dirname(os.path.realpath(__file__))

#################################################### Help Functions ####################################################### 

def CheckPixel(color: Tuple[int, int, int], lowValue: int, highValue: int, y: int, percent: int, screenshot: np.ndarray) -> bool:
    target_color = GetPixel((round(lowValue + (highValue - lowValue) * percent/100), y), screenshot)
    return not all(lower <= target <= upper for target, lower, upper in zip(target_color, [c - 5 for c in color], [c + 5 for c in color]))

def GetColorFromCoords(position: Tuple [int, int]) -> Tuple[int, int, int]:
    return Screenshot().getpixel(position)

def GetCoordsFromDetection(image: np.ndarray) -> Tuple [int, int]:
    screenshot = ScreenshotNp()
    result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
    sorted_result_indices = np.argsort(result, axis=None)[::-1]
    max_val_index = sorted_result_indices[0]
    second_max_val_index = sorted_result_indices[1]
    max_loc = np.unravel_index(max_val_index, result.shape)
    second_max_loc = np.unravel_index(second_max_val_index, result.shape)
    if result[max_loc] > 0.9:
        return (max_loc[1], max_loc[0]), (second_max_loc[1], second_max_loc[0])
    else:
        return (0, 0), (0, 0)

def GetPixel(position: Tuple [int, int], screenshot: np.ndarray) -> Tuple[int, int, int]:
    return screenshot.getpixel(position)

def ReadFromFile(fileName: str) -> str:
    with open(fileName) as file:
        return file.read()

def ScreenshotNp() -> np.ndarray:
    return cv2.cvtColor(np.array(pyautogui.screenshot().convert('RGB')), cv2.COLOR_RGB2BGR)

def Screenshot():
    return pyautogui.screenshot().convert('RGB')

def WriteToFile(fileName: str, input: str):
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
esc = 0x1B
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
    x_normalized = int(65535 * (position[0] / resolution[0]))
    y_normalized = int(65535 * (position[1] / resolution[1]))
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
    if any([key in z for z in [{keyboard.Key.shift}]]):
        if ReadFromFile("stop.txt") == "0":
            WriteToFile("stop.txt", "1")
        else:
            WriteToFile("stop.txt", "0")      
 
def InputSleep():
    time.sleep(0.02) 

 #################################################### Config ####################################################### 

baseCoords, baseCoords2 = GetCoordsFromDetection(cv2.imread(currentPath + "\\WindowDetect.png"))
if baseCoords[1] < baseCoords2[1]:
    saveCoords = baseCoords
    baseCoords = baseCoords2
    baseCoords2 = saveCoords
MoveMouseTo((baseCoords[0] + 14, baseCoords[1] + 250))
MouseClick()
MouseClick()
toplist, winlist = [], []
hpZero = (baseCoords[0] + 181, baseCoords[1] + 64)
hpFull = (hpZero[0] + 85, hpZero[1])
mpZero = (hpZero[0] + 4, hpZero[1]  + 33)
mpFull = (mpZero[0] + 85,hpZero[1] + 33)
hpZero2 = (baseCoords2[0] + 181, baseCoords2[1] + 64)
hpFull2 = (hpZero2[0] + 85, hpZero2[1])
mpZero2 = (hpZero2[0] + 4, hpZero2[1]  + 33)
mpFull2 = (mpZero2[0] + 85,hpZero2[1] + 33)
enemyCoords, enemyCoords2 = GetCoordsFromDetection(cv2.imread(currentPath + "\\enemy.png"))
if enemyCoords[1] < enemyCoords2[1]:
    enemyCoords = enemyCoords2
enemyPosition = (enemyCoords[0] -97 , enemyCoords[1] + 5)
enemyPositionExit = (enemyCoords[0] -5 , enemyCoords[1] - 4)
partyPosition = (baseCoords2[0] + 14, baseCoords2[1] + 250)
fighterPosition = (hpZero[0], hpZero[1] + 802)
healerPosition = hpZero2
hpColor = GetColorFromCoords(hpZero)
mpColor = GetColorFromCoords(mpZero)
enemyHpColor = GetColorFromCoords(enemyPosition)
enemyExitColor = GetColorFromCoords(enemyPositionExit)
PressKey(esc)

############################################################################################### Main Functions #####################################################################################################

def Attack():
    ts = datetime.datetime.now()
    screenshot = Screenshot()
    while MonsterNotHit(screenshot):
        PressKey(one)
        PressKey(two)
        time.sleep(0.1)
        RefreshProcess(50, screenshot)
        screenshot = Screenshot()
        if CheckStuck(ts):
            return 1
    while True:
        for i in range(5):
            PressKey(skills[i])
            screenshot = Screenshot()
            if enemyExitColor != GetPixel(enemyPositionExit, screenshot):
                return 0
            PressKey(two)
            RefreshProcess(50, screenshot)
        if CheckStuck(ts):
            return 1

def CheckStuck(ts):
    if (datetime.datetime.now() - ts).total_seconds() > 20 or PlayerWasSelect():
        PressKey(esc)
        KeyDown(s)
        KeyDown(s)
        time.sleep(3)
        ReleaseKey(s)
        time.sleep(0.1)
        Rotate()
        Rotate()
        Rotate()
        return True
    return False

def FiestaBot():
    WriteToFile("stop.txt", "1")
    while True:
        if ReadFromFile("stop.txt") == "0":
            #CheckStuck(datetime.datetime.now()- datetime.timedelta(seconds=21))
            if FindMonster():
                Attack()
            else:
                Rotate()
        else:
            InputSleep()    
        1111111111111111
def FindMonster():
    PressKey(k)
    return GetPixel(enemyPositionExit, Screenshot()) == enemyExitColor

def MonsterNotHit(screenshot): 
    return GetPixel(enemyPosition, screenshot) != enemyHpColor

def PlayerWasSelect():
    return GetPixel((enemyCoords[0] + 3, baseCoords[1] + 3), Screenshot()) == (255, 243, 68)

def RefreshProcess(percent, screenshot):
    # Healer healq
    if CheckPixel(hpColor, hpZero[0], hpFull[0], hpFull[1], percent + 20, screenshot):
        TargetHealer()
        PressKey(one)     
        TargetFighter()
    # Stone heal
    if CheckPixel(hpColor, hpZero[0], hpFull[0], hpFull[1], percent, screenshot):
        PressKey(q)
    if CheckPixel(mpColor, mpZero[0], mpFull[0], mpFull[1], (percent - 20), screenshot):
        PressKey(e)
    # Healer heal
    if CheckPixel(hpColor, hpZero2[0], hpFull2[0], hpFull2[1], percent, screenshot):
        TargetHealer()
        PressKey(esc)
        PressKey(one)
        MoveMouseTo(partyPosition)
        MouseClick()
        TargetFighter()
        if CheckPixel(mpColor, mpZero2[0], mpFull2[0], mpFull2[1], percent, screenshot):
            PressKey(e)
        TargetFighter()
    elif CheckPixel(mpColor, mpZero2[0], mpFull2[0], mpFull2[1], (percent - 20), screenshot):
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
