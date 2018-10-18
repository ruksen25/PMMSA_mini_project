"""
Desciprtion:
    This program provides a simulated mouse interface using
    eye gaze and a gesture recognition. 
    
Authors:
    Shagen Djanian, Aalborg University
    Marike van den Broek, Aalborg University
"""

import pyautogui
import keyboard
pyautogui.FAILSAFE = True # Drag mouse to upper left corner to trigger failsafe
import win32gui
import gesture_reader 


def grabObject(xy_pos = None):
    #pyautogui.moveTo(xy_pos)
    #pyautogui.mouseDown(button='left')
    pyautogui.click();
    current_window = win32gui.GetForegroundWindow()
    return current_window


def moveWin32Gui(pos, hwnd=None):
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
        win_size,offset,size = getOffset(pos,hwnd)
        x_pos = pos[0]
        y_pos = pos[1]
        x_offset = offset[0]
        y_offset = offset[1]   
        pyautogui.moveTo((x_pos-x_offset+150,y_pos-y_offset+10))
        pyautogui.mouseDown(button='left')
        #print('Moving to',current_position)
        
def getOffset(pos,hwnd = None):
        win_size = win32gui.GetWindowRect(hwnd)
        for i in win_size:
            print(i)
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
    current_position = pyautogui.position()
    return current_position

    
def grabGesture(grabBool = False):
    if keyboard.is_pressed('q'):
        grabBool = True
    return grabBool

if __name__ == "__main__":
    ## Initialization
    # Create a sample listener and controller
    listener = gesture_reader.SampleListener()
    controller = gesture_reader.Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)    
    #pygame.mouse.set_visible(True)
    
    ## Loop
    print('Press Ctrl-C to quit.')

    try:
        grab_bool = False;
        while True:
            fistStatus = listener.getFist(controller)
            print(fistStatus)
            current_position = currentGazePosition()
            if (fistStatus == True):
               current_window_handle = grabObject()
               while (fistStatus==True):
                   fistStatus = listener.getFist(controller) # Update the fistStatus in the while loop
                   current_position = currentGazePosition()
                   movePyAutoGui(current_position,current_window_handle)
            if(fistStatus == False):
                pyautogui.mouseUp(button='left')
                  
             
    except KeyboardInterrupt:
        print('\n Interrupted.')
    
