import mediapipe as mp
import cv2

def _get_locations_list (image,detector) ->list:
    height = image.shape[0]
    width = image.shape[1]
    results = detector.process(img)
    hands_data=[]

    if results.multi_hand_landmarks:
        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):#for each hand found
            for i in range(21):
                res = hand_landmarks.landmark[mp_hands.HandLandmark(i).value]

                x = int(res.x*width)
                y = int(res.y*height)

                hands_data.append([x,y])
    
    return hands_data


video = cv2.VideoCapture(1)
mp_hands = mp.solutions.hands
detector = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)

while True:
    img  = video.read()[1]
    hands_landmarks =_get_locations_list(img,detector)
    
    if len(hands_landmarks)>0:
        for i in hands_landmarks:
            img = cv2.circle(img,i,10,(0,255,0),1)
            
    cv2.imshow("image",img)
    if cv2.waitKey(1) == 27: 
            break

            