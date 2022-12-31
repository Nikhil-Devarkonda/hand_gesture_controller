import cv2
import mediapipe as mp
import numpy as np
from win32gui import GetWindowText, GetForegroundWindow
from cvzone.HandTrackingModule import HandDetector
import pyautogui as pyg
pyg.FAILSAFE = False
import time
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hand_detector = HandDetector(detectionCon=0.5,maxHands=1)

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

class SwipeTracker:
    track_len = 100
    LEFT = 1
    RIGHT = 2
    NONE = 0
    def __init__(self):
        self.tracker_data = []

    def put(self,mark):
        if len(self.tracker_data) > SwipeTracker.track_len :
            self.tracker_data.pop(0)
        self.tracker_data.append(mark)
    def getDirection(self):
        displace = 0
        for i in range(1,len(self.tracker_data)):
            displace += self.tracker_data[i].x - self.tracker_data[i-1].x 
        
        # print('Displace',displace)

        if displace > 0.40:
            print('RIGHT')
            self.clearHistory()
            return SwipeTracker.RIGHT
        elif displace < - 0.40 :
            print('LEFT')
            self.clearHistory()
            return SwipeTracker.LEFT
        else:
            # print('NONE')
            return SwipeTracker.NONE
    def clearHistory(self):
        self.tracker_data.clear()

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

class StopGestureDetector:
    stop_time = 0.7 # seconds
    STOP = 1
    RESUME = 2
    CONTIUNE = 3
    def __init__(self,fps):
        self.fps = fps
        self.isStopGesture = False
        self.count_fps = 0
    def call(self):
        self.count_fps += 1
        # print(self.count_fps,end="_")
        if  self.count_fps > (StopGestureDetector.stop_time*self.fps):
            self.count_fps = 0
            self.isStopGesture = not self.isStopGesture
            # print("Detection Active",self.isStopGesture)
            if self.isStopGesture:
                return StopGestureDetector.STOP
            else:
                return StopGestureDetector.RESUME
            
        return StopGestureDetector.CONTIUNE
    def hasGestureStop(self):
        return self.isStopGesture
    def resetTimer(self):
        self.count_fps = 0
def isSlideShowActive():
    return 'PowerPoint Slide Show' in GetWindowText(GetForegroundWindow())

def launchGestureControl():
    yield 'Launching Camera please wait...'    
    # For webcam input:
    screen_height = pyg.size()[1]
    screen_width = pyg.size()[0]
    screen_center = (screen_width//3,screen_height//3)

    cap = cv2.VideoCapture(0)
    cap_height = screen_height//2
    cap_width = screen_width//2
    cap.set(3,cap_width)
    cap.set(4,cap_height)
    hasCameraLaunced = False

    mouseTrack = MouseTracker(pyg.size(),(cap_width,cap_height))
    swipeTrack = SwipeTracker()
    stopDetector =  StopGestureDetector(30)

    with mp_hands.Hands(
        max_num_hands=1,
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:

        while cap.isOpened():

            success, image = cap.read()
            image = cv2.flip(image, 1)
            # time.sleep(0.5)

            if hasCameraLaunced == False:
                hasCameraLaunced = True
                yield 'Camera Active'

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
            
            # Settings for PPT
            resetControls = False
            
            
            handsX,image = hand_detector.findHands(image)
            if handsX:
                hand = handsX[0]
                fingers = hand_detector.fingersUp(hand)
                resetControls = True
                # print(fingers)

                lm = hand['lmList']

                firstFinger = lm[HandLandmark.INDEX_FINGER_TIP]
                fx,fy = int(firstFinger[0]),int(firstFinger[1])
                
                # secondFinger = lm[HandLandmark.MIDDLE_FINGER_TIP]
                # sx,sy = int(secondFinger[0]),int(secondFinger[1])
                
                
                
                # Check for Cursor Active
                if fingers == [0,1,1,0,0] and not stopDetector.hasGestureStop():
                    # Use first finger cordinates to move mouse
                    xVal = np.interp(fx,[cap_width//2,cap_width],[0,screen_width])
                    yVal = np.interp(fy,[0,cap_height-100],[0,screen_height])
                    cv2.circle(image,(int(fx),int(fy)),10,(255,255,0),cv2.FILLED)
                    mouseTrack.put((xVal,yVal))

                    coordinates = mouseTrack.getMouseLocation()
                    if(isSlideShowActive()):
                        pyg.keyDown('ctrl')
                        pyg.mouseDown()
                    pyg.moveTo(*mouseTrack.getMouseLocation())
                    
                    cv2.rectangle(image,(cap_width//2,0),(cap_width,cap_height-100),(255,0,0),2)
                # Check for Swipe Direction
                elif fingers == [1,1,1,1,1] and not stopDetector.hasGestureStop():
                    pyg.keyUp('ctrl')
                    if results.multi_hand_landmarks:
                        swipeTrack.put(results.multi_hand_landmarks[0].landmark[HandLandmark.INDEX_FINGER_TIP])
                        direction = swipeTrack.getDirection()

                        if direction == SwipeTracker.LEFT:
                            pyg.press('left')
                            time.sleep(1)
                            swipeTrack.clearHistory()
                        if direction == SwipeTracker.RIGHT:
                            pyg.press('right')
                            time.sleep(1)
                            swipeTrack.clearHistory()
                elif fingers == [0,1,1,1,1]:
                    if stopDetector.call() in [StopGestureDetector.STOP,StopGestureDetector.RESUME]:
                        
                        print('Gesture Detections ',not stopDetector.hasGestureStop())
                        time.sleep(1)
                        stopDetector.resetTimer()
                        
                # mp_drawing.draw_landmarks(
                #     image,
                #     hand_landmarks,
                #     mp_hands.HAND_CONNECTIONS,
                #     mp_drawing_styles.get_default_hand_landmarks_style(),
                #     mp_drawing_styles.get_default_hand_connections_style())
            else:
                if resetControls:
                    pyg.keyUp('ctrl')
                    pyg.mouseUp()
                    resetControls = False        
                        
                
                
            image = cv2.resize(image, (0, 0), fx = 0.9, fy = 0.9)
            cv2.imshow('MediaPipe Hands',image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
    cv2.destroyAllWindows()
    yield 'Launch'

if __name__ == '__main__':
    for i in launchGestureControl():
        pass