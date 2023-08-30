import cv2
import HandTrackingModule as htm
from math import sqrt,pow

def middle(x1:int,x2:int,y1:int,y2:int):
    """Estimate the middle point between two points

    Args:
        x1 (int): locaiton x of the first point
        x2 (int): location x of the second point
        y1 (int): location y of the first point
        y2 (int): location y of the second point

    Returns:
        tuple: the estimated x and y location of the middle point.
    """
    x = int((x1+x2)/2)
    y = int((y1+y2)/2)
    return x,y

def isInside(circle_x:int, circle_y:int, rad:int, x:int, y:int):
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

def FingerStraight(x1:int,x2:int,y1:int,y2:int,tx:int,ty:int):
    """Obtain the middle point between the location of the tip of the Metacarpal and the tip if the Intermediate phalage,
    Draw a circle of a certain radius in that location.
    if the tip of the proximal phalage is within the radius of the circle, but the Intermediate phalage and the Metacarpal
    aren't inside the circle then we know the finger is straight. 
    If so then it will draw a circle.

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
        return True
    else : return False

def dist_2_points(x1:int, x2:int, y1:int, y2:int):
    """This method returns the distance between two points.

    Args:
        x1 (int): location x of first point
        x2 (int): location x of second point
        y1 (int): location y of first point
        y2 (int): location y of second point

    Returns:
        int: result as an int
    """
    # _/ (x2-x1)*2 + (y2-y1)*2
    return sqrt(pow((x2-x1),2) + pow((y2-y1),2))

def thumb_contracted(hand_x, hand_y, thumb_x, thumb_y):
    rad = 35
    x,y = middle(hand_x,thumb_x,hand_y,thumb_y)
    return not isInside(x,y,rad,thumb_x,thumb_y)

def dist_2_points(x1:int, x2:int, y1:int, y2:int):
    """This method returns the distance between two points.

    Args:
        x1 (int): location x of first point
        x2 (int): location x of second point
        y1 (int): location y of first point
        y2 (int): location y of second point

    Returns:
        int: result as an int
    """
    # _/ (x2-x1)*2 + (y2-y1)*2
    return sqrt(pow((x2-x1),2) + pow((y2-y1),2))

def detect_pinch(x1:int,y1:int,x2:int,y2:int,x3:int,y3:int, index:bool, thumb:bool):
    """Detect if the hand is pitching based on the distance of the thumb and the index finger

    Args:
        x1 (int): x location of the tip of the thumb
        y1 (int): location y of the tip of the thumb
        x2 (int): location x of the tip of the index
        y2 (int): location y of the tip of the index
        x3 (int): location x of the middle point of the thumb
        y3 (int): location y of the middle point of the thumb
        index (bool): True, finger is extended
        thumb (bool): True, the thumb is not contracted

    Returns:
        bool: True, user is pinching
    """

    #if index is contracted and the tumb is not contracted
    if index and not thumb:
        return False
    
    d1 = dist_2_points(x1,x3,y1,y3) #distance between point 4 and 3
    d2 = dist_2_points(x1,x2,y1,y2) #Distance between point 4 and 8

    if d1>d2:
        return True
    


def finger_detector(locations, detect, camara, show = False):


    while True:
        #[Index,middle,ring,pinky,thumb]
        fingers = [False,False,False,False,False] #True = finger is extended
        img = detect.findHands(camara.read()[1])
        lmList = detect.findPosition(img,draw=False)#hand points
        counter = 0

        if len(lmList)!=0:
            for i in locations:
                #[(tip, bottom, middle)]
                x1,x2 =lmList[i[0]][1],lmList[i[1]][1]
                y1,y2 =lmList[i[0]][2],lmList[i[1]][2]
                tx,ty =lmList[i[2]][1],lmList[i[2]][2]

                #verify if the finger is straight
                if  show: cv2.circle(img, middle(x1,x2,y1,y2), radius=20, color=(0, 255, 0), thickness=1)#draw the range
                
                fingers[counter] = FingerStraight(x1,x2,y1,y2,tx,ty)

                counter += 1
        
            #Check for the thumb
            hand_x, thumb_x=lmList[5][1],lmList[3][1] #Location x of point 5, location x of point 3
            hand_y, thumb_y=lmList[5][2],lmList[3][2] #same but y location
            
            fingers[-1] = thumb_contracted(hand_x,hand_y,thumb_x,thumb_y) #assign result to the array

            if show and not fingers[-1]:#Draw line between point 5 and 3 as well as a circle in the middle point to see if it is contracted or not
                cv2.line(img, (hand_x,hand_y), (thumb_x,thumb_y), color=(0,255,0), thickness=1)
                cv2.circle(img, middle(hand_x,thumb_x,hand_y,thumb_y), radius=35, color=(255, 0, 0), thickness=1)


        cv2.imshow("Image", img)

        print(f"{fingers}")

        if cv2.waitKey(1) == 32:
            break

wCam, hCam= 1280, 720

cap = cv2.VideoCapture(1)
cap.set(3,wCam)
cap.set(4,hCam)

detector = htm.handDetector(detectionCon= 1)
            #(tip, bottom, middle)
finger_loc = [(8,5,6),(12,9,10),(16,13,14),(20,17,18)]

finger_detector(finger_loc,detector,cap, False)