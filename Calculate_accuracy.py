import Finger_detector as fd
import mediapipe as mp
from os import listdir
from main import _get_locations_list
import Finger_detector as fd
import cv2
import pandas as pd

    

fd_obj = fd.Finger_detector()
mp_hands = mp.solutions.hands #Hand detector object
detector = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8)
total = 244
location = "C:/Users/CIICCTE/Desktop/DataSet/"

files = listdir(location)

radii = [5,10,15,20,25,30,35,40]
TP_lst= []
FP_lst= []
TN_lst= []
FN_lst= []
Pres = []
Acc = []

for radius in radii:

    results = []
    for file in  files:
        image = cv2.imread(location+file)
        locations = _get_locations_list(image,detector,mp_hands)
        if locations:
            locations = locations[0]
            hand_x, thumb_x=locations[5][0],locations[3][0]
            hand_y, thumb_y=locations[5][1],locations[3][1]

            results.append(fd_obj._thumb_contracted(hand_x,hand_y,thumb_x,thumb_y,radius))
        else:
            results.append(False)



    #verify
    tp=0
    fp=0
    tn=0
    fn=0

    for i in range(len(results)):
        if i<total and results[i]==False:
            tn+=1
        elif i<total and results[i]==True:
            fp+=1
        elif i>total and results[i]==True:
            tp+=1
        elif i>total and results[i]==False:
            fn+=1

    if tp==0 and fp ==0:precision = 0
    else: precision = (tp/(tp+fp))*100
    accuracy = ((tp + tn)/ (tp + tn + fp + fn))*100

    TP_lst.append(tp)
    TN_lst.append(tn)
    FP_lst.append(fp)
    FN_lst.append(fn)
    Pres.append(precision)
    Acc.append(accuracy)

dataframe = {"radius":radii,"True Positive":TP_lst,"True Negative":TN_lst,"False Positive":FP_lst,"False Negative":FN_lst,"Precision":Pres,"Accuracy":Acc}
df = pd.DataFrame(data = dataframe)
df.to_excel("C:/Users/CIICCTE/Desktop/output.xlsx")