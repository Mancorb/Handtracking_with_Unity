import cv2
import mediapipe as mp
import socket
from threading import Thread
import Finger_detector as fd
import DepthCamera as dca
import DeleteFiles

def main(n,LIMIT=500,image=False,verbose = False):
    dc = dca.DepthCamera() #Depth camara access object
    fd_obj = fd.Finger_detector()

    threads = []#List of threads for each hand

    mp_hands = mp.solutions.hands #Hand detector object
    detector = mp_hands.Hands(max_num_hands=n, min_detection_confidence=0.8)

    #The first 4 elements in the dictionary are the names of the files and the last 4 elements of dictionary are numbers used to obtain the names of the first 4 elements of the diccionary as if it were a list
    files={"A":0,"B":0,"C":0,"D":0,0:"A",1:"B",2:"C",3:"D"}#Folder names and # of files counters and a "list of all the dictionary options"


    while True:
        ret, depth_frame, color_frame = dc.get_frame() #Get the frame objects

        hands = _get_locations_list(color_frame,detector,mp_hands)

        #print(f"\rTracking {len(hands)}, hands.", end="")
        #Land mark values = (x,y) * 21 (total number of points we have per hand)

        if hands:
            for i in range(len(hands)):
                #For each hand detected store the data
                name = files[i]
                #t = Thread(target=_saveData,
                #                     args=(hands[i],depth_frame,
                #                           name,files[name],fd_obj,verbose))
            
                #t = Thread(target=_send_Data, 
                #                     args=(hands[i],sockets[i],depth_frame,
                #                           height,saps[i]))
                #t.start()
                #threads.append(t)

                _save_n_send(name,hands[i],depth_frame,files[name],fd_obj,verbose,sockets[i],height,saps[i])
                
                #Add one to the folder counter
                files[name] += 1
                #Reset counter when it reaches the limit to start replaceing old files
                if files[name] > LIMIT: files[name] = 0

        for t in threads: t.join() #Join all the threads
        
        #Show the current image of the camera
        if image: cv2.imshow("Image", color_frame)

        key = cv2.waitKey(1)
        if key == 32: break #Close program if SPACEBAR is pressed
    print("\nProcess aborted...")


def _get_locations_list (image,detector,hand_obj) ->list:
    """Method that returns the location of found landmarks

    Args:
        hand_obj(mediapipe obj): object with all captured data
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
                res = hand_landmarks.landmark[hand_obj.HandLandmark(i).value]

                #number is multiplied by the width and hight to get the location within the image
                x = int(res.x*width)
                y = int(res.y*height)

                temp.append([x,y])
            hands_data.append(temp)
    
    return hands_data


def _socketList(n):
    """Create n ammount of UDP sockets

    Args:
        n (int): number of sockets to create

    Returns:
        list tuple: socket and port lists
    """
    #List of udp connections
    SKs =[]
    SAPs = []
    #Assign each a different port to comunicate to
    for i in range(n):
        sk, serverAddPort = _setSocket(5001+i)
        SKs.append(sk)
        SAPs.append(serverAddPort)
    return SKs,SAPs


def _setSocket(port):
    """Create a UDP Socket conection to transmit data to unity

    Returns:
        socket,tuple: socket port and tuple with ip and port
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #port to send to (ip, port)
    serverPort = ("127.0.0.1", port)
    return sk,serverPort


def _location_Error_Filter (locations):
    """Filter error causing values for depth detection

    Args:
        locations (tuple): x,y locations of the middle point

    Returns:
        tuple: fixed locations
    """
    x,y = locations
    if x >= 480:
        x = 479
    if y >= 479:
        y=478
    return x,y


def write_File(file_loc, locations,unity_h,dist,gesture):
    """Write the data into the specified txt file in the apropriate folder

    Args:
        file_loc (string): location to store the txt file
        locations (list): list of locations of detected hand points
        unity_h (int): inverted y pixels for unity recognition
        dist (int): height of the hand detected by the depth sensor
        gesture(str): interpretated gesture
    """
    with open(file_loc,"w") as file: #Save the info in the corresponding file
        for loc in locations:
            file.write(f"{loc[0]},{unity_h - loc[0]},{loc[1]}\n")
        file.write(f"{dist}\n{gesture}")


def _gesture_interpretor (landMarks,fd_obj)-> str:
    """returns interpretation of the gesture based on the results obtained by the Finger detector class

    Args:
        landMarks (list): list of detected landmarks

    Returns:
        str: Interpretation based on criteria
    """

    flex_list,pinch_flag = fd_obj.detect(landMarks)
    #True= finger streched, False = contracted
    if pinch_flag: return "Pinch"

        #L shape hand
    if flex_list[0] and flex_list[1]:
        for i in range(1,len(flex_list)-1):
            if flex_list[i]==True:
                break
        return "L"
    
    
    #Pointing 1 finger
    if flex_list[0]:
        for i in range(1,len(flex_list)):
            if not flex_list[i]:
                break
            
        return "Pointing"

    return "                "


def _saveData(hand,depth_frame,name,n,fd_obj,show = False):
    """Record hand point location and overall distance from camera to a specific file in a corresponding file.
    As soon as the loop reaches the limit the previous file with the same 'n' will be replaced with new data to not
    overwhelm the storage.

    Args:
        hand (list): Lista de info. de la mano seleccionada
        depth_frame (frame): Imagen de la percepción de profundidad de la cámara
        name (string): Nombre del folder en el que se guardará el archivo
        n (int): Iteración del archivo
    """
    height = 1200 #Height used to invert the Y axis for unity

    #Obtain the location of the center of the hand
    x,y = _location_Error_Filter(fd_obj._middle(hand[9][0],hand[0][0],hand[9][1],hand[0][1]))

    try:
        dist = depth_frame[x,y] #Get the estimated distence of the center of the hand from the camera            
    except Exception as e:
        print("Error")
    
    location = f"./Hand_{name}/[{n}].txt" #Hand_A/[0]

    gesture = _gesture_interpretor(hand,fd_obj)

    write_File(location,hand,height,dist, gesture) 
    if show: print(f"\rHand {name}: {gesture}", end="")


def _send_Data (hand,sk,depth_frame,height,SAP):
    data = []
    #get landmark list
    lmlst = hand["lmList"]
    loc = hand["center"]
    
    #get the estimated distence of the center of the hand from the camera            
    dist = int((depth_frame[loc[1],loc[0]])/1)
    
    for lm in lmlst:
        #Save the data with the oposite value since unity saves data oposite to open cv
        data.extend([lm[0],height - lm[1],lm[2],dist])
        
    sk.sendto(str.encode(str(data)), SAP)
    #print(f"-----\nsent: {data}\nto:{SAP}")

#========== LA FUNCIÓN DE ABAJO TODAVÍA ESTÁ EN ETAPA DE PRUEBAS============
def _save_n_send (name, hands[i],depth_frame,files[name],fd_obj,verbose,sockets[i],height,saps[i]) -> void:
    t = Thread(target=_saveData,
                args=(hands[i],depth_frame,
                name,files[name],fd_obj,verbose))

    t.start()
    threads.append(t)
            
    t = Thread(target=_send_Data, 
                args=(hands[i],sockets[i],depth_frame,
                height,saps[i]))
                
    t.start()
    threads.append(t)


if __name__ == "__main__":
    try:
        print("[+] Bootup complete!!!")
        main(1,100,image=False,verbose=True)
        print("\n[+] Ending program")
    except KeyboardInterrupt:
        print("\n[-]Program Interrupted by user")
    
    DeleteFiles.delete_it_all()

