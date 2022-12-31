import cv2

cap = cv2.VideoCapture(0) 


width  = cap.get(3)  # float `width`
height = cap.get(4)  # float `height`

# it gives me 0.0 :/
fps = cap.get(5)
LEFT = 1
RIGHT = 2
print(width,height,fps)
hand_queue = []
HAND = -1
frame_count = 0 
hand_clear_threshold = fps*4
object_detector = cv2.createBackgroundSubtractorMOG2(history=50,varThreshold=50)
while True:
    success,frame = cap.read()
    frame_count+=1

    if frame_count % hand_clear_threshold == 0:
        hand_queue.clear()
        print("HAND CLEARED")

    # Object Detection 
    mask = object_detector.apply(frame)

    # _,mask = cv2.threshold(mask,254,255,cv2.THRESH_BINARY)
    contours,_= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area > 100:
            # cv2.drawContours(frame,[cnt],-1,(0,255,0),2)
            x,y,w,h = cv2.boundingRect(cnt)
            if x < 120 and HAND != LEFT :
                hand_queue.append(LEFT)
                HAND = LEFT
                print(hand_queue)
            elif x > (width-120) and HAND != RIGHT: 
                hand_queue.append(RIGHT)
                HAND = RIGHT
                print(hand_queue)

            
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),3)
            # cv2.drawContours(mask,[cnt],-1,(0,255,0),2)
    frame = cv2.line(frame, (120,0), (120,480), (0,0,255), 3)
    frame = cv2.line(frame, (int(width-120),0), (int(width-120),480), (0,0,255), 3)
    
    if len(hand_queue) >= 2:
        if hand_queue[0] == LEFT and hand_queue[1] == RIGHT:
            print('LEFT SWIPPED')
        if hand_queue[0] == RIGHT and hand_queue[1] == LEFT:
            print('RIGHT SWIPPED')
        hand_queue.clear()

        
    cv2.imshow("Frame",frame)
    cv2.imshow("Black",mask)
    if cv2.waitKey(30) == 27:
        break
cap.release()
cv2.destroyAllWindows()