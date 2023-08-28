import cv2
import HandTrackingModule as htm


def isInside(circle_x, circle_y, rad, x, y):
    """Find of a point is inside an estimated circle

    Args:
        circle_x (int): location x of the circle's center
        circle_y (int): location y of the circle's center
        rad (int): raius of the circle in pixels
        x (int): location of the point to find
        y (int): location y of the point to find

    Returns:
        bool: If the point is inside the circle then it will return True, else it will return False
    """
    if ((x - circle_x) * (x - circle_x) +
        (y - circle_y) * (y - circle_y) <= rad * rad):
        return True
    else:
        return False

def FingerStraight(x1,x2,y1,y2,tx,ty):
    """Make a circle located between the location of the beggining of the index finger and the tip if the middle bone
    of the finger is within the radius of the circle, but neither the tip nor the bottom are in the range then we know 
    the finger is straight. If so then it will draw a circle in the

    Args:
        x1 (int): location x of the base of the finger
        x2 (int): location x of the tip of the finger
        y1 (int): location y of the base of the finger
        y2 (int): location y of the tip of the finger
        tx (int): locaiton x of the middle bone of the finger
        ty (int): location y of the middle bone of the finger
    """
    rad = 20
    x,y= (lambda x1,x2,y1,y2: (int((x1+x2)/2),int((y1+y2)/2))) (x1,x2,y1,y2) #Estimate the middle point between two points

    mid =isInside(x,y,rad,tx,ty)
    base = isInside(x,y,rad,x1,y1)
    tip = isInside(x,y,rad,x2,y2)
    
    if mid and not base and not tip:
        return True
    

wCam, hCam= 1280, 720

cap = cv2.VideoCapture(1)
cap.set(3,wCam)
cap.set(4,hCam)

detector = htm.handDetector(detectionCon= 1)
            #(tip, bottom, middle)
finger_loc = [(8,5,6),(12,9,10),(16,13,14),(20,17,18)]
#For the thumb just check if the middle part of the thumb is near the base of the index finger

while True:
    fingers = [False,False,False,False,True]
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)
    counter = 0
    
    if len(lmList)!=0:
        for i in finger_loc:
            #[(tip, bottom, middle)]
            x1,x2 =lmList[i[0]][1],lmList[i[1]][1]
            y1,y2 =lmList[i[0]][2],lmList[i[1]][2]
            tx,ty =lmList[i[2]][1],lmList[i[2]][2]

            if FingerStraight(x1,x2,y1,y2,tx,ty):
                img = cv2.circle(img, middle(x1,x2,y1,y2), radius=20, color=(0, 0, 255), thickness=1)
                fingers[counter] = True
                
            counter += 1

        #look for the thumb
        x1 = lmList[5][1]
        y1 = lmList[5][2]
        tx,ty = lmList[3][1],lmList[3][2]

        if isInside(x1,y1,30,tx,ty):
            img = cv2.circle(img,(x1,y1),radius=10,color=(0,0,255),thickness=1)
            fingers[counter] = False


    cv2.imshow("Image", img)

    print(fingers)

    if cv2.waitKey(1) == 32:
        break