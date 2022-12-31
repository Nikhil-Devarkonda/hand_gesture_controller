import cv2
import mediapipe as mp
import numpy as np
import math

import pyautogui as pyg
pyg.FAILSAFE = False
import time
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class HandLandmark:
  """The 21 hand landmarks."""
  WRIST = 0
  THUMB_CMC = 1
  THUMB_MCP = 2
  THUMB_IP = 3
  THUMB_TIP = 4
  INDEX_FINGER_MCP = 5
  INDEX_FINGER_PIP = 6
  INDEX_FINGER_DIP = 7
  INDEX_FINGER_TIP = 8
  MIDDLE_FINGER_MCP = 9
  MIDDLE_FINGER_PIP = 10
  MIDDLE_FINGER_DIP = 11
  MIDDLE_FINGER_TIP = 12
  RING_FINGER_MCP = 13
  RING_FINGER_PIP = 14
  RING_FINGER_DIP = 15
  RING_FINGER_TIP = 16
  PINKY_MCP = 17
  PINKY_PIP = 18
  PINKY_DIP = 19
  PINKY_TIP = 20

class MouseTracker:
  HOLD = 1
  CLICK = 2
  MOVE = 3
  buffer_len = 50
  
  def __init__(self,screen_size,window_size):
    self.tracker_data = []
    self.screen_size = screen_size
    self.window_size = window_size
    self.prev_loc = (0,0)
    self.curr_loc = (0,0)
    self.isInitCordSet = False
  def put(self,cord):
    self.prev_loc = self.curr_loc
    if not self.isInitCordSet:
        self.curr_loc = cord
        self.prev_loc = cord
        self.isInitCordSet = True
    else:
        self.curr_loc = cord
        
            
    if len(self.tracker_data) > MouseTracker.buffer_len :
      self.tracker_data.pop(0)
    self.tracker_data.append(cord)
  def getMouseLocation(self):
    # Velocity
    velocity_X = (self.curr_loc[0]-self.prev_loc[0])
    velocity_Y = (self.curr_loc[1]-self.prev_loc[1])
    if(abs(velocity_X) < 50 and abs(velocity_Y) < 50):
        return self.prev_loc

    # print(velocity_X,velocity_Y)
    return self.curr_loc[0],self.curr_loc[1]

  def isClick(self):
    pass
  def isMouseHold(self):
    pass
  def clearHistory(self):
    self.tracker_data.clear()


    
# For webcam input:
screen_height = pyg.size()[1]
screen_width = pyg.size()[0]
screen_center = (screen_width//3,screen_height//3)

cap = cv2.VideoCapture(0)
cap_height = screen_height//2
cap_width = screen_width//2
cap.set(3,cap_width)
cap.set(4,cap_height)

mouseTrack = MouseTracker(pyg.size(),(cap_width,cap_height))
with mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.4,
    min_tracking_confidence=0.5) as hands:

  while cap.isOpened():

    success, image = cap.read()
    image = cv2.flip(image, 1)

    if not success:
      print("Ignoring empty camera frame.")
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    
    h,w,c = image.shape

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        lm = hand_landmarks.landmark


        firstFinger = lm[HandLandmark.INDEX_FINGER_TIP]
        secondFinger = lm[HandLandmark.MIDDLE_FINGER_TIP]
        fx,fy = int(firstFinger.x*w),int(firstFinger.y*h)
        sx,sy = int(secondFinger.x*w),int(secondFinger.y*h)
        

        # Cursor Active
        dist = round(math.dist([fx,fy],[sx,sy]),1)
        if dist < 50:
            # Use first finger cordinates to move mouse
            xVal = np.interp(fx,[cap_width//2,cap_width],[0,screen_width])
            yVal = np.interp(fy,[0,cap_height-100],[0,screen_height])
            cv2.circle(image,(int(fx),int(fy)),10,(255,255,0),cv2.FILLED)
            mouseTrack.put((xVal,yVal))
            coordinates = mouseTrack.getMouseLocation()
            pyg.moveTo(*mouseTrack.getMouseLocation())  
            cv2.rectangle(image,(cap_width//2,0),(cap_width,cap_height-100),(255,0,0),2)
    else:
        # Reset to Middle
        # pyg.moveTo(screen_center)
        pass

    cv2.imshow('MediaPipe Hands',image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()