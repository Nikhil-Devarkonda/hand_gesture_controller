import cv2
import mediapipe as mp

import pyautogui as pyg
import time
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


class SwipeTracker:
  track_len = 200
  LEFT = 1
  RIGHT = 2
  NONE = 0
  def __init__(self):
    self.tracker_data = []
  def put(self,landmarks):
    if len(self.tracker_data) > SwipeTracker.track_len :
      self.tracker_data.pop(0)
    self.tracker_data.append(landmarks[12]) # 12 -> TIP of Middle Finger
  def getDirection(self):
    displace = 0
    for i in range(1,len(self.tracker_data)):
      displace += self.tracker_data[i].x - self.tracker_data[i-1].x 
    
    # print('Displace',displace)

    if displace > 0.45:
      print('RIGHT')
      self.clearHistory()
      return SwipeTracker.RIGHT
    elif displace < - 0.45 :
      print('LEFT')
      self.clearHistory()
      return SwipeTracker.LEFT
      
    else:
      # print('NONE')
      return SwipeTracker.NONE
  def clearHistory(self):
    self.tracker_data.clear()

    
# For webcam input:
cap = cv2.VideoCapture(0)
swipeTrack = SwipeTracker()
with mp_hands.Hands(
    max_num_hands=1,
    model_complexity=0,
    min_detection_confidence=0.1,
    min_tracking_confidence=0.1) as hands:

  while cap.isOpened():

    success, image = cap.read()
   

    if not success:
      print("Ignoring empty camera frame.")
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:

       
      for hand_landmarks in results.multi_hand_landmarks:

        # Track MIDDLE_FINGER_TIP
        swipeTrack.put(hand_landmarks.landmark)
        direction = swipeTrack.getDirection()
        if direction == SwipeTracker.LEFT:
          pyg.press('left')
          time.sleep(1)
          swipeTrack.clearHistory()
        if direction == SwipeTracker.RIGHT:
          pyg.press('right')
          time.sleep(1)
          swipeTrack.clearHistory()



        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()