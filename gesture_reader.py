################################################################################
# Copyright (C) 2012-2016 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
"""
Desciprtion:
    This script provides an interface to recognize gestures using Leap Motion.
    To install the Python SDK follow https://developer-archive.leapmotion.com/documentation/python/index.html .
    It only runs on Python 2.7. It currently on recognizes a fist by looking at the angles between the fingers.
    An example of how to use it:
            # Create a sample listener and controller
            listener = SampleListener()
            controller = Leap.Controller()

            # Have the sample listener receive events from the controller
            controller.add_listener(listener)
            
            # Check if a fist is currently being made
            fiststatus = listener.getFist(controller)
            print(fiststatus)
    
    Current recognized gestures:
        Fist - getFist(Leap.controller)
    
Authors:
    Shagen Djanian, Aalborg University
    Marike van den Broek, Aalborg University
"""
## Finds the relative path to the correct library needed for Leap.py
import os, sys, inspect
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = '../lib/x64' if sys.maxsize > 2**32 else '../lib/x86'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))


import Leap
import numpy as np
import numpy.linalg as la
import itertools
import operator
import math
import pandas as pd

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    fiveFistArray = [False,False,False,False,False]
    def on_init(self, controller):
        print("Initialized")

    def on_connect(self, controller):
        print("Connected")

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print ("Disconnected")

    def on_exit(self, controller):
        print ("Exited")
        
    def shift2(self,arr,num = 1):
        """
        Shifs the array by 1 using np.roll.
        """
        arr=np.roll(arr,num)
        if num<0:
             np.put(arr,range(len(arr)+num,len(arr)),np.nan)
        elif num > 0:
             np.put(arr,range(num),np.nan)
        return arr

    def shift1(self,arr,num = 1):
        """
        Shifts the array by 1 converting array to panda, shifting and converting to list. 
        """
        data = pd.Series(arr)
        data = data.shift(num)
        return data.tolist()


    def most_common(L):
      """
          Gets the most common occurence in a list. Code from https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list/20872750
      """
      # get an iterable of (item, iterable) pairs
      SL = sorted((x, i) for i, x in enumerate(L))
      # print 'SL:', SL
      groups = itertools.groupby(SL, key=operator.itemgetter(0))
      # auxiliary function to get "quality" for an item
      def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
          count += 1
          min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index
      # pick the highest-count/earliest item
      return max(groups, key=_auxfun)[0]          

      # get an iterable of (item, iterable) pairs
 

    def updateRollingArray(self,arr,new_value):
        """
        Shifts the array and puts the new value in the first index's place
        """
        shifted_arr = self.shift2(arr)
        shifted_arr[0] = new_value
        return shifted_arr

    def unit_vector(self,vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(self,v1, v2):
        """ Returns the angle in radians between vectors 'v1' and 'v2'::
                >>> angle_between((1, 0, 0), (0, 1, 0))
                1.5707963267948966
                >>> angle_between((1, 0, 0), (1, 0, 0))
                0.0
                >>> angle_between((1, 0, 0), (-1, 0, 0))
                3.141592653589793
        """
        v1_u = self.unit_vector(v1)
        v2_u = self.unit_vector(v2)
        return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))
    
    def get_current_angles(self, controller):
        """
        Calculates the angles between the finger bones. The finger bone direction are stored in a Leap.Vector which has to be convected to numpy array.
        Angles are measured in radians.
        """
        frame = controller.frame()
        for hand in frame.hands:

            #handType = "Left hand" if hand.is_left else "Right hand"

            #print ("  %s, id %d, position: %s" % (
            #    handType, hand.id, hand.palm_position))
            # Get fingers
            bone_difference_angle_array = np.zeros(5)
            ii = 0;
            for finger in hand.fingers:
                 #Get bones
                close_finger_dir = finger.bone(0).direction # Metacarpals (first bone)
                close_finger_dir_nparray = self.LeapVectorToNpArray(close_finger_dir)
                
                #print(close_finger_dir_nparray)
                
                far_finger_dir = finger.bone(1).direction # Proximal phalanges (second finger bone)
                far_finger_dir_nparray = self.LeapVectorToNpArray(far_finger_dir)
                #print(far_finger_dir_nparray)

                angle = self.angle_between(close_finger_dir_nparray,far_finger_dir_nparray)
                #print(angle)
                bone_difference_angle_array[ii] = angle
                ii = ii + 1
                
            if frame.hands.is_empty == True:
                #print ("Empty")
                #empty = np.zeros(5)
                return 
            else:
                return bone_difference_angle_array 

    def checkFistGesture(self,angle_array):
        """
        Checks if a fist is made. The mean of the finger angles is taken to ensure that all four fingers are closed for a first. threshold is set imperically
            input:
                angle_array - An array of the angles between the Metacarpals (first bone) and the Proximal phalanges (second finger bone). The first index is the thumb
        """
        if angle_array is None:
            return False
        
        drop_thumb = angle_array[1:-1]
        mean_angle = np.mean(drop_thumb)
        threshold = 1.3
        if mean_angle>threshold:
            fist = True
        else:
            fist = False
        return fist

    def getMajorityBool(self,arr):
        """
            Counts how many trues are in a boolean array. If there are more trues than false, returns true.
        """
        #num_true = arr.count(True)
        num_true = sum(arr)
        if num_true > math.ceil(len(arr)/2.0):
            return True
        else:
            return False

    def getFist(self, controller):
        """
        Get the status of a fist. If no hand is detected it prints no hands. Is uses a rolling mean, so if the 5 most
        recent samples for a fist are true it returns true.
        """
        
        angle_array = self.get_current_angles(controller)
        frame = controller.frame()
        if frame.hands.is_empty == True:
                print ("No hand detected")
                return
        else:
            fist_status = self.checkFistGesture(angle_array)
            self.fiveFistArray = self.updateRollingArray(self.fiveFistArray,fist_status)
            fist_status = self.getMajorityBool(self.fiveFistArray)
            return fist_status
        
    def LeapVectorToNpArray(self,leap_vec):
        """
        Converts a Leap.Vector to a numpy array. Leap.Vector is a class in the Leap package
        """
        tup = leap_vec.to_tuple()
        nparray = np.asarray(tup)
        return nparray
    
    def on_frame(self, controller):
        '''
        Sample code from leap motion. Uncomment all print all values you receive from a hand.
        '''
        # Get the most recent frame and report some basic information
        frame = controller.frame()

#        print ("Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
#              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers)))
#
#        # Get hands
#        for hand in frame.hands:
#
#            handType = "Left hand" if hand.is_left else "Right hand"
#
#            print ("  %s, id %d, position: %s" % (
#                handType, hand.id, hand.palm_position))
#
#            # Get the hand's normal vector and direction
#            normal = hand.palm_normal
#            direction = hand.direction
#
#            # Calculate the hand's pitch, roll, and yaw angles
#            print ("  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
#                direction.pitch * Leap.RAD_TO_DEG,
#                normal.roll * Leap.RAD_TO_DEG,
#                direction.yaw * Leap.RAD_TO_DEG))
#
#            # Get arm bone
#            arm = hand.arm
#            print ("  Arm direction: %s, wrist position: %s, elbow position: %s" % (
#                arm.direction,
#                arm.wrist_position,
#                arm.elbow_position))
#
#            # Get fingers
#            for finger in hand.fingers:
#
#                print ("    %s finger, id: %d, length: %fmm, width: %fmm" % (
#                    self.finger_names[finger.type],
#                    finger.id,
#                    finger.length,
#                    finger.width))
#                
#                 #Get bones
#                for b in range(0, 4):
#                    bone = finger.bone(b)
#                    print ("      Bone: %s, start: %s, end: %s, direction: %s" % (
#                        self.bone_names[bone.type],
#                        bone.prev_joint,
#                        bone.next_joint,
#                        bone.direction))
#
#        if not frame.hands.is_empty:
#            print ("")
        

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print ("Press Enter to quit...")
    try:
        while True:
            #sys.stdin.readline()
            #foo = listener.get_current_angles(controller)
            foo = listener.getFist(controller)
            print(foo)
            #controller.add_listener(listener)
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()
