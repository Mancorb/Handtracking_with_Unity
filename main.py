import cv2
from cvzone.HandTrackingModule import HandDetector
import socket
from threading import Thread
import Finger_detector as fd
import DepthCamera as dca

def getDistance(points,frame, prev_dist = None):
    """Obtain the location of the middle point of the registered hand

    Args:
        points (list): list of points to obtain the middle point from
        frame (cv image): cv frame with info on depth used to locate depth of the desired point

    Returns:
        float: Estimated distance of the middle of the hand 
    """
    
    x = 0
    y = 0
    for point in points:
        x=+ point[0]
        y=+ point[1]
    x = int(x/len(points))
    y = int(y/len(points))

    dist = int((frame[x,y])/10)
    return dist,[x,y],prev_dist

def socketList(n):
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
        sk, serverAddPort = setSocket(5001+i)
        SKs.append(sk)
        SAPs.append(serverAddPort)
    return SKs,SAPs

def setSocket(port):
    """Create a UDP Socket conection to transmit data to unity

    Returns:
        socket,tuple: socket port and tuple with ip and port
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #port to send to (ip, port)
    serverPort = ("127.0.0.1", port)
    return sk,serverPort

def location_Error_Filter (x,y):
    """Reduce the location of x & y to avoid error

    Args:
        x (int): locaiton x of center
        y (int): location y of center

    Returns:
        tuple: location x & y modified.
    """
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
            file.write(f"{loc[0]},{unity_h - loc[1]},{loc[2]}\n")
        file.write(f"{dist}\n{gesture}")

def gesture_interpretor (landMarks,fd_obj)-> str:
    """returns interpretation of the gesture based on the results obtained by the Finger detector class

    Args:
        landMarks (list): list of detected landmarks

    Returns:
        str: Interpretation based on criteria
    """

    flex_list,pinch_flag = fd_obj.detect(landMarks)
    #True= finger streched, False = contracted
    if pinch_flag: return "Pinch"

    #Open hand
    if len(set(flex_list)) == 1 and flex_list[0]: return "Open hand"

    #Fist
    if len(set(flex_list)) == 1 and not flex_list[0]: return "Fist"

    #Open fingers (does not consider thumb)
    if all (flex_list[i]==True for i in range(len(flex_list)-1)): return "Open fingers"

    #Pointing 1 finger
    if flex_list[0]:
        for i in range(1,len(flex_list)):
            if not flex_list[i]:
                pass
            
        return "Pointing"
    
    #L shape hand
    if flex_list[0] and flex_list[1] and all(flex_list[i]==True for i in range(1,len(flex_list)-1)):
        return "L"

    return ""

def saveData(hand,depth_frame,name,n,fd_obj,show = False):
    """Record hand point location and overall distance from camera to a specific file in a corresponding file.
    As soon as the loop reaches the limit the previous file with the same 'n' will be replaced with new data to not
    overwhelm the storage.

    Args:
        hand (list): list of info of the selected hand
        depth_frame (frame): image frame of camera depth perseption
        name (string): name of the Folder to safe the file to
        n (int): iteration of the file
    """
    height = 1200 #Height used to invert the Y axis for unity

    lmlst = hand["lmList"] #List of hand landmarks
    x,y = hand["center"] #Obtain the location of the center of the hand
    
    x,y = location_Error_Filter(x,y)

    try:
        dist = depth_frame[x,y] #Get the estimated distence of the center of the hand from the camera            
    except Exception as e:
        print("Error")
    
    location = f"./Hand_{name}/[{n}].txt" #Hand_A/[0]

    gesture = gesture_interpretor(lmlst,fd_obj)

    write_File(location,lmlst,height,dist, gesture) 
    if show: print(f"Hand {name}: {gesture}")

def filter_Hand_Info(hands:list):
    """Extract only the location of the points of interes and the center of the hand

    Args:
        hands (list): original list of data from detected hands

    Returns:
        list: reduced list containing only list of points and location of the center
    """
    result = []
    temp = {"lmList":None,"center":None}

    for hand in hands:
        temp["lmList"] = hand["lmList"]
        temp["center"] = hand["center"]
        result.append(temp)

    return result

def main(n,LIMIT=500,image=False,verbose = False):
    dc = dca.DepthCamera() #Depth camara access object
    fd_obj = fd.Finger_detector()

    threads = []#List of threads for each hand

    detector = HandDetector(maxHands=n, detectionCon=0.8) #Hand detector object

    #The first 4 elements in the dictionary are the names of the files and the last 4 elements of dictionary are numbers used to obtain the names of the first 4 elements of the diccionary as if it were a list
    files={"A":0,"B":0,"C":0,"D":0,0:"A",1:"B",2:"C",3:"D"}#Folder names and # of files counters and a "list of all the dictionary options"

    print("=============\nBootup complete, looking for hands...\n=============\n")

    while True:
        ret, depth_frame, color_frame = dc.get_frame() #Get the frame objects
        hands, color_frame = detector.findHands(color_frame) #Get the hands info list        
        print(f"\rTracking {len(hands)}, hands.", end="")

        #Filter the info
        hands = filter_Hand_Info(hands)

        #Land mark values = (x,y,z) * 21 (total number of points we have per hand)
        if hands:
            for i in range(len(hands)):
                #For each hand detected store the data
                name = files[i]
                t = Thread(target=saveData,
                                     args=(hands[i],depth_frame,
                                           name,files[name],fd_obj,verbose))
                t.start()
                threads.append(t)
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

if __name__ == "__main__":
    main(1,100,True,True)
    print("Ending program")