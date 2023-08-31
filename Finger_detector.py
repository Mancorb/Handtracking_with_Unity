from math import sqrt,pow

class Finger_detector:
    
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
    
    def fingerStraight(x1:int,x2:int,y1:int,y2:int,tx:int,ty:int,self):
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
        x,y= self.middle(x1,x2,y1,y2)
        mid = self.isInside(x,y,rad,tx,ty)
        base = self.isInside(x,y,rad,x1,y1)
        tip = self.isInside(x,y,rad,x2,y2)
        
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
    
    def thumb_contracted(hand_x, hand_y, thumb_x, thumb_y,self):
        """Make a circle between the hand and the thumb to detect if the thumb is extended or not

        Args:
            hand_x (int): location x of the hand
            hand_y (int): location y of the hand
            thumb_x (int): location x of the middle part of the thumb
            thumb_y (int): location y of the middle part of the thumb

        Returns:
            bool: True, Thumb is not extended away from the  hand; False oposite
        """
        rad = 35
        x,y = self.middle(hand_x,thumb_x,hand_y,thumb_y)
        return not self.isInside(x,y,rad,thumb_x,thumb_y)
    
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
    
    def detect_pinch(x1:int,y1:int,x2:int,y2:int,x3:int,y3:int, index:bool, thumb:bool,self):
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
        if (not index and thumb):
            d1 = self.dist_2_points(x1,x3,y1,y3) #Distance between point 4 and 3
            d2 = self.dist_2_points(x1,x2,y1,y2) #Distance between point 4 and 8
    
            if d1>d2:
                return True
        
        return False
        
    def detect(lmList,self):
        """Return a tuple, first element is a list of bools indicating if a fingers is contracted based on it's location
        The Second element is a bool indicating if the hand is pinching.
    
        Args:
            lmList (array): Array of id,location x, location y of a specific point in fhte hand.
    
        Returns:
            tuple: tuple with detected results
        """
        #id of each finger and their parts
        #[index finger, middle finger, ring finger, pinky, thumb]
        #(tip, bottom, middle)
        locations = [(8,5,6),(12,9,10),(16,13,14),(20,17,18)]
    
        #[Index,middle,ring,pinky,thumb]
        fingers = [False,False,False,False,False] #True = finger is extended
        counter = 0
        pinch = False
    
        if len(lmList)!=0:
            for i in locations:
                #[(tip, bottom, middle)]
                x1,x2 =lmList[i[0]][1],lmList[i[1]][1]
                y1,y2 =lmList[i[0]][2],lmList[i[1]][2]
                tx,ty =lmList[i[2]][1],lmList[i[2]][2]
    
                fingers[counter] = self.fingerStraight(x1,x2,y1,y2,tx,ty)
    
                counter += 1
            
            #Check for the thumb
            hand_x, thumb_x=lmList[5][1],lmList[3][1] #Location x of point 5, location x of point 3
            hand_y, thumb_y=lmList[5][2],lmList[3][2] #same but y location
                
            fingers[-1] = self.thumb_contracted(hand_x,hand_y,thumb_x,thumb_y) #assign result to the array
                
            pinch = self.detect_pinch(lmList[4][1],lmList[4][2],
                                 lmList[8][1],lmList[8][2],
                                 lmList[3][1],lmList[3][2],
                                 fingers[0],
                                 fingers[-1])
            
        return (fingers,pinch)
    
    #detector = htm.handDetector(detectionCon= 1)
    #finger_detector(finger_loc,detector)