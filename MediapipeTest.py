import mediapipe as mp
import cv2

video = cv2.VideoCapture(1)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)

while True:
    img  = video.read()[1]
    height = img.shape[0]
    width = img.shape[1]
    results = hands.process(img)

    if results.multi_hand_landmarks:
        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):#for each hand found
            res = hand_landmarks.landmark[mp_hands.HandLandmark(0).value]

            print(int(res.x*width))
            print(int(res.y*height))
            