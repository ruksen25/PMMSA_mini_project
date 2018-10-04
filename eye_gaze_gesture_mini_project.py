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

def grabObject(xy_pos):
    pyautogui.moveTo(xy_pos)
    pyautogui.mouseDown(button='left')
    return


def currentGazePosition():
    current_position = pyautogui.position()
    return current_position

    
def grabGesture(grabBool = False):
    if keyboard.is_pressed('q'):
        grabBool = True
    return grabBool

if __name__ == "__main__":
    print('Press Ctrl-C to quit.')

    try:
        while True:
           # TODO: Get and print the mouse coordinates.
           gesture_bool = grabGesture()
           current_position = currentGazePosition();
           if gesture_bool == True:
               grabObject(current_position)
           else:
               pyautogui.mouseUp()
           print(current_position)

    except KeyboardInterrupt:
        print('\n Interrupted.')
    
