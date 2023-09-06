import mediapipe as mp
import cv2

def _get_locations_list (image,detector) ->list:
    """Method that returns the location of found landmarks

    Args:
        image (numpy.ndarray): image captured by the camara
        detector (mediapipe.python.solutions.hands.Hands): Information from the detection algorithim

    Returns:
        list: List of landmarks
    """
    #hight and width of the image
    height = image.shape[0]
    width = image.shape[1]
    results = detector.process(image)
    hands_data=[]#list of landmark lists

    if results.multi_hand_landmarks:#if a hand is found
        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):#for each hand found
            temp = []
            for i in range(21):#obtain ONLY x and Y locations
                res = hand_landmarks.landmark[detector.HandLandmark(i).value]

                #number is multiplied by the width and hight to get the location within the image
                x = int(res.x*width)
                y = int(res.y*height)

                temp.append([x,y])
            hands_data.append(temp)
    
    return hands_data


""" video = cv2.VideoCapture(1)
mp_hands = mp.solutions.hands
detector = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.8)

while True:
    img  = video.read()[1]
    hands_landmarks =_get_locations_list(img,detector) """
