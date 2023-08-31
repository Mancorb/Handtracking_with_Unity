import cv2
from cvzone.HandTrackingModule import HandDetector
import socket
import threading
import Finger_detector as fd
import DepthCamera as dca


def socketList(n) -> list, tuple:
    """
    Crea una n cantidad de sockets UDP

    Args:
        n (int): Núm. de sockets a crear

    Returns:
        list, tupla: Listas de sockets y puertos
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


def setSocket(port) -> Socket, tuple:
    """
    Crea una conexión con el socket UDP para transmitir datos a Unity

    Returns:
        socket, tupla: Puerto de socket y tupla con IP y puerto 
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #port to send to (ip, port)
    serverPort = ("127.0.0.1", port)
    return sk,serverPort


def location_Error_Filter (x,y) -> tuple:
    """
    Reduce la localización de X & Y para prevenir un error

    Args:
        x (int): Loc. X del centro
        y (int): Loc. Y del centro

    Returns:
        tupla: Localización X & Y modificada
    """
    if x >= 480:
        x = 479
    if y >= 479:
        y=478
    return x,y


def write_File(file_loc, locations,unity_h,dist,gesture) -> void:
    """
    Escribe datos en el archivo .txt especificado en el folder apropiado

    Args:
        file_loc (string): Path en el que se almacenará el archivo .txt
        locations (list): Lista de localizaciones de puntos de mano detectados
        unity_h (int): Píxeles Y invertidos para el reconocimiento en Unity
        dist (int): Altura de la mano detectada por el sensor de profundidad
        gesture(str): Gesto interpretado
    """
    with open(file_loc,"w") as file: #Save the info in the corresponding file
        for loc in locations:
            file.write(f"{loc[0]},{unity_h - loc[1]},{loc[2]}\n")
        file.write(f"{dist}\n{gesture}")


def gesture_interpretor (landMarks) -> str:
    """
    Retorna interpretación del gesto basándose en los resultados obtenidos por
    la clase de detección del dedo

    Args:
        landMarks (list): Lista de marcas detectadas

    Returns:
        str: Interpretación basada en criterios
    """

    fd_obj = fd.Finger_detector()
    flex_list,pinch_flag = fd_obj.detect(landMarks)

    if pinch_flag: return "Pinch"

    #Fist if all True
    if len(set(flex_list)) == 1 and set(flex_list): return "Fist"

    #Open hand
    if len(set(flex_list)) == 1 and not set(flex_list): return "Open hand"

    #Open fingers (does not consider thumb)
    if all (flex_list[i]==False for i in range(len(flex_list)-1)): return "Open fingers"

    #Pointing 1 finger
    if flex_list[0] and all(flex_list[i]==True for i in range(1,len(flex_list))):
        return "Pointing"
    
    #L shape hand
    if flex_list[0] and flex_list[1] and all(flex_list[i]==False for i in range(1,len(flex_list)-1)):
        return "L"

    return ""


def saveData(hand,depth_frame,name,n) -> void:
    """
    Registra la localización del punto de la mano y la distancia general desde la cámra a un archivo específico
    Tan pronto el ciclo alcanza el límite que el archivo previo con la misma 'n' será reemplazado 
    con datos nuevos para no abrumar el almacenamiento

    Args:
        hand (list): Lista de info. de la mano seleccionada
        depth_frame (frame): Imagen de la percepción de profundidad de la cámara
        name (string): Nombre del folder en el que se guardará el archivo
        n (int): Iteración del archivo
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

    gesture = gesture_interpretor(lmlst)

    write_File(location,lmlst,height,dist, gesture) 


def filter_Hand_Info(hands:list) -> list:
    """
    Extrae solo la localización de los puntos de interés y el centro de la mano

    Args:
        hands (list): Lista original de datos de las manos detectadas

    Returns:
        list: Lista reducida conteniendo solo la lista de puntos y la loc. del centro
    """
    result = []
    temp = {"lmList":None,"center":None}

    for hand in hands:
        temp["lmList"] = hand["lmList"]
        temp["center"] = hand["center"]
        result.append(temp)

    return result


def main(n,LIMIT=500,image=False) -> void:
    dc = dca.DepthCamera() #Depth camara access object

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
                t = threading.Thread(target=saveData,
                                     args=(hands[i],depth_frame,
                                           name,files[name]))
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
    main(4,100,False)
    print("Ending program")
