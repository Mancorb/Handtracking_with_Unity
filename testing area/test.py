import cv2
import HandTrackingModule as htm

def middle(x1,x2,y1,y2):
    x = int((x1+x2)/2)
    y = int((y1+y2)/2)
    return x,y

def isInside(circle_x, circle_y, rad, x, y):
    if ((x - circle_x) * (x - circle_x) +
        (y - circle_y) * (y - circle_y) <= rad * rad):
        return True
    else:
        return False

def indexStraight(x1,x2,y1,y2,tx,ty):
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
    x,y= middle(x1,x2,y1,y2)
    mid =isInside(x,y,rad,tx,ty)
    base = isInside(x,y,rad,x1,y1)
    tip = isInside(x,y,rad,x2,y2)
    
    if mid and not base and not tip:
        #img = cv2.circle(img, middle(x1,x2,y1,y2), rad, color=(0, 0, 255), thickness=1)
        return True
    

wCam, hCam= 1280, 720

cap = cv2.VideoCapture(1)


cap.set(3,wCam)
cap.set(4,hCam)

detector = htm.handDetector(detectionCon= 1)

while True:
    fingers = {"index":False,"middle":False,"ring":False,"pinky":False, "thumb":False}
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img,draw=False)
    
    if len(lmList)!=0:
        x1,x2 =lmList[8][1],lmList[5][1]
        y1,y2 =lmList[8][2],lmList[5][2]
        tx,ty =lmList[6][1],lmList[6][2]

        if indexStraight(x1,x2,y1,y2,tx,ty):
            img = cv2.circle(img, middle(x1,x2,y1,y2), radius=20, color=(0, 0, 255), thickness=1)
        


    cv2.imshow("Image", img)

    print(f"\rIndex:{fingers['index']}\tMiddle:{fingers['middle']}\tRing:{fingers['ring']}\tPinky:{fingers['pinky']}\tThumb:{fingers['thumb']}",end = "")
    
    if cv2.waitKey(1) == 32:
        break