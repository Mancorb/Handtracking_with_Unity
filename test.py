import cv2
import time
import os
import HandTrackingModule as hm

wCam, hCam= 1280, 720

cap = cv2.VideoCapture(1)

folderpath= "Hand_Images"
lstDir = os.listdir(folderpath)
OverlayLst = []

cap.set(3,wCam)
cap.set(4,hCam)


for imPath in lstDir:
    image = cv2.imread(f"{folderpath}/{imPath}")
    OverlayLst.append(image)

pTime = 0
while True:

    success, img = cap.read()

    #show hand image on screen
    h, w, c = OverlayLst[0].shape
    img[0:h, 0:w] = OverlayLst[0]

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime= cTime

    cv2.putText(img, f"FPS: {int(fps)}", (400,70), cv2.FONT_HERSHEY_PLAIN,
                3,(255,0,0),3)

    cv2.imshow("Image", img)
    
    if cv2.waitKey(1) == 32:
        break
