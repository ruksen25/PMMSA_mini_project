"""
Desciprtion:
    This program uses the tobii eye tracker and leap motion to get the users gaze and gestures being made. Currently it
    can only drag a window when the user makes a fist.
    
Authors:
    Shagen Djanian, Aalborg University
    Marike van den Broek, Aalborg University
"""

import pyautogui
import keyboard  
pyautogui.FAILSAFE = True # Drag mouse to upper left corner to trigger failsafe
import win32gui
import gesture_reader 
import tobii_research as tr

from pygaze.display import Display
from pygaze.eyetracker import EyeTracker
import time
import sys
from pynput.mouse import Button, Controller
import numpy as np
import pandas as pd


global mouse
mouse = Controller()


def calibrateEyeTrackerPyGaze():
    """
        Runs the callibration process using PyGaze and tobii eye trackers.
    """

    disp = Display()
    tracker = EyeTracker(disp,resolution=(1600,900),  trackertype='tobii')
    
    tracker.calibrate()
    
    #tracker.close() 
    disp.close()
    return tracker



def avaliableEyeTrackers():
    """
        Checks for the available eye trackers connected using tobii SDK
    """
# <BeginExample>
    eyetrackers = tr.find_all_eyetrackers()

    for eyetracker in eyetrackers:
        print("Address: " + eyetracker.address)
        print("Model: " + eyetracker.model)
        print("Name (It's OK if this is empty): " + eyetracker.device_name)
        print("Serial number: " + eyetracker.serial_number)
    # <EndExample>
    return eyetrackers


def grabObject(xy_pos = None):
    """
        Clicks on the current position to get the window to be the window in the foreground
        and returns that windows handle
    """
    #pyautogui.moveTo(xy_pos)
    #pyautogui.mouseDown(button='left')
    #pyautogui.click();
    mouse.press(Button.left)
    mouse.release(Button.left)
    current_window = win32gui.GetForegroundWindow()
    return current_window


def moveWin32Gui(pos, hwnd=None):
    
    """
        Moves the window by using the Win32Gui. This produces a bug where the window is flashing because it is
        being put on top of the window stack all the time. Only works with windows.
    
    """
    pos = (int(pos[0]),int(pos[1]))
    win_size,offset,size = getOffset(pos, hwnd)
    x_pos = pos[0]
    y_pos = pos[1]
    x_offset = offset[0]
    y_offset = offset[1]   
    w_window = size[0]
    h_window = size[1]
    win32gui.MoveWindow(hwnd,x_pos+x_offset,y_pos+y_offset,w_window,h_window, False)
    #print('Moving to',current_position)
        
def movePyAutoGui(pos, hwnd=None):
    """
        Moves the window using PyAutoGui. This is platform independents, but PyAutoGui bugs when used with PyGaze, so
        until that bug is removed it is unusable.
    """
    #pos = (int(pos[0]),int(pos[1]))
    win_size,offset,size = getOffset(pos,hwnd)
    x_pos = pos[0]
    y_pos = pos[1]   
    x_offset = offset[0]
    y_offset = offset[1]   
    #mouse.release(Button.left)
    pyautogui.moveTo((x_pos-x_offset+size[1]/2,y_pos-y_offset+10))
    pyautogui.mouseDown(button='left')
    print('old pos',pos[0],pos[1])
    print('new x and y pos to move to',x_pos-x_offset+size[1]/2,y_pos-y_offset+10)
    #mouse.position = ((x_pos-x_offset+size[1]/2,y_pos-y_offset+10))
    #mouse.position = ((x_pos,y_pos))
    #mouse.press(Button.left)
        
def movePynput(pos, hwnd=None):
    """
        Moves the window using Pynput. This is the current implementation as is does not bug when used with PyGaze
    """
    x_pos = pos[0]
    y_pos = pos[1]
    print('position: ',pos[0],pos[1])
    #print('new x and y pos to move to',x_pos-x_offset+size[1]/2,y_pos-y_offset+10)
    #mouse.position = ((x_pos-x_offset+size[1]/2,y_pos-y_offset+10))
    mouse.position = ((x_pos,y_pos))
    mouse.press(Button.left)

def shift1(arr,num = 1):
    """
    Shifts the array by 1 converting array to panda, shifting and converting to list. 
    """
    data = pd.Series(arr)
    data = data.shift(num)
    return data.tolist()

def shift2(arr,num = 1):
    """
    Shifs the array by 1 using np.roll.
    """
    arr=np.roll(arr,num)
    if num<0:
         np.put(arr,range(len(arr)+num,len(arr)),np.nan)
    elif num > 0: 
         np.put(arr,range(num),np.nan)
    return arr

def updateRollingArray(arr,new_value):
    """
    Shifts the array and puts the new value in the first index's place
    """
    shifted_arr = shift1(arr)
    shifted_arr[0] = new_value
    return shifted_arr

    

        
def getOffset(pos,hwnd = None):
    """
    Calculates the offset from the mouse to the top left corner of a window.
    
    input:
        pos = a tuple of x and y coordinates of the current position
        
    return:
        win_size = top left corner and bottom right corner of a window using Win32Gui
        offset = The x and y offset from the mouse to the window corner
        size = height and width of the window
        
    """
    win_size = win32gui.GetWindowRect(hwnd)
    #for i in win_size:
    #    print(i)
    x_pos = pos[0]
    y_pos = pos[1]
    x_window = win_size[0]
    y_window = win_size[1]
    w_window = win_size[2] - x_window
    h_window = win_size[3] - y_window
    x_offset = x_pos - x_window
    y_offset = y_pos - y_window
    
    offset=(x_offset,y_offset)
    size = (h_window,w_window)
    return win_size,offset,size
            
def currentGazePosition():
    """
        Emulates a gaze position by simply getting the current mouse position. 
    """
    #current_position = pyautogui.position()
    current_position = mouse.position
    return current_position

    
def grabGesture(grabBool = False):
    """
        An function used during develpment that no longer is relevan
    """
    if keyboard.is_pressed('q'):
        grabBool = True
    return grabBool

if __name__ == "__main__":
    ## Initialization
    # Create a sample listener and controller
    listener = gesture_reader.SampleListener()
    controller = gesture_reader.Leap.Controller()

    # Have the sample listener receive events  from the controller
    controller.add_listener(listener)    
    #pygame.mouse.set_visible(True)
    eyetracker = calibrateEyeTrackerPyGaze()
    eyetracker.start_recording()
    #gaze_array = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    gaze_array = range(1,30)

    
    ## Loop
    print('Press Ctrl-C to quit.')

    try:
        grab_bool = False;
        while True:
            fistStatus = listener.getFist(controller)
            print('fist status is: ',fistStatus)
            #print('current gaze is at: ',current_gaze_sample)
            current_sample = eyetracker.sample()
            gaze_array = updateRollingArray(gaze_array,current_sample)

            print('Gaze is at:  ',current_sample)          
            #current_position = currentGazePosition()
            if (fistStatus == True):
               current_window_handle = grabObject()
               while (fistStatus==True):
                   print('fist status is: ',fistStatus)
                   #current_position = currentGazePosition()
                   current_sample = eyetracker.sample()
                   gaze_array = updateRollingArray(gaze_array,current_sample)
                   current_gaze_mean = np.mean(gaze_array,axis=0)
                   print('Gaze mean is at:  ',current_gaze_mean)
                   movePynput(current_gaze_mean,current_window_handle)
                   fistStatus = listener.getFist(controller) # Update the fistStatus in the while loop

            if(fistStatus == False):
                #pyautogui.mouseUp(button='left')
                mousePressCheck=False
                mouse.release(Button.left)
                  
             
    except KeyboardInterrupt:
        print('\n Interrupted.')
        eyetracker.stop_recording()
        eyetracker.close()
    
