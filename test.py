import cv2
import HandTrackingModule as htm

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
        if lmList[8][2] < lmList[6][2]:
            fingers["index"] = True
        if lmList[12][2] < lmList[10][2]:
            fingers["middle"] = True
        if lmList[16][2] < lmList[14][2]:
            fingers["ring"] = True
        if lmList[20][2] < lmList[18][2]:
            fingers["pinky"] = True
        if lmList[4][1]>lmList[3][1]:
            fingers["thumb"] = True


    cv2.imshow("Image", img)

    print(f"\rIndex:{fingers['index']}\tMiddle:{fingers['middle']}\tRing:{fingers['ring']}\tPinky:{fingers['pinky']}\tThumb:{fingers['thumb']}",end = "")
    
    if cv2.waitKey(1) == 32:
        break
