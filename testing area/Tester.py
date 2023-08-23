import cv2 
import mediapipe as mp
import pickle
import numpy as np
from os import system


cap  = cv2.VideoCapture(1)

model_dict = pickle.load(open("testing area\model.p","rb"))
model = model_dict['model']

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

labels_dict = {0: "one finger", 1: "right pinch", 2: "two fingers"}

while True:
    data_aux = []

    ret, frame = cap.read()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
        )

        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x)
                data_aux.append(y)
        
        prediction = model.predict([np.asarray(data_aux)])

        predicted_result = labels_dict[int(prediction[0])]

        cv2.putText(frame,predicted_result, (100,50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0,255,0),3,cv2.LINE_AA)

    cv2.imshow("frame",frame)
    if cv2.waitKey(1) == 32:
        break


cap.release()
cv2.destroyAllWindows()