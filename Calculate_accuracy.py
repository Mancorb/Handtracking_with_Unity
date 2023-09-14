import Finger_detector as fd
import mediapipe as mp
from os import listdir
from main import _get_locations_list, _gesture_interpretor
import cv2

fd_obj = fd.Finger_detector()
mp_hands = mp.solutions.hands #Hand detector object
detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)

location = "C:/Users/CIICCTE/Desktop/DataSet/"

files = listdir(location)

results = []


for file in  files:
    image = cv2.imread(location+file)
    hands = _get_locations_list(image,detector,mp_hands)
    if hands:
        res = _gesture_interpretor(hands[0],fd_obj)
        if res == "Pointing":
            results.append(True)
        else:
            results.append(False)
    else:
        results.append(False)
        

#verify
tp=0
fp=0
tn=0
fn=0

for i in range(len(results)):
    if i<244 and results[i]==True:
        tp+=1
    elif i<244 and results[i]==False:
        fp+=1
    elif i>244 and results[i]==False:
        tn+=1
    elif i>244 and results[i]==True:
        fn+=1

print(f"\n----------------\nPrecision:{(tp/(tp+fp))*100}\nAccuracy:{((tp + tn)/ (tp + tn + fp + fn))*100}")
print(f"[TP:{tp}\tTN:{tn}]\n[FP:{fp}\tFN:{fn}]")