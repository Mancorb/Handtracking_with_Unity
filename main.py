import cv2
import mediapipe as mp
import socket
from threading import Thread
import Finger_detector as fd
import DepthCamera as dca

def main(n,LIMIT=500,image=False,verbose = False):
    dc = dca.DepthCamera() #Depth camara access object
    fd_obj = fd.Finger_detector()

    threads = []#Lista de hilos para cada mano

    mp_hands = mp.solutions.hands #Hand detector object
    detector = mp_hands.Hands(max_num_hands=n, min_detection_confidence=0.8)

    #Los primeros 4 elementos en el diccionario son los nombres de los archivos y los últimos 4 elementos del diccionario son 
    #núms. utilizados para obtener los nombres de los primeros 4 elementos del dicc. como si fuése una lista
    files={"A":0,"B":0,"C":0,"D":0,0:"A",1:"B",2:"C",3:"D"}
    #Nombres de carpeta y no. de contadores de archivos y una "lista de todas las opciones de diccionario"


    while True:
        ret, depth_frame, color_frame = dc.get_frame() #Obtiene los objs. del frame

        hands = _get_locations_list(color_frame,detector,mp_hands)

        #print(f"\rTracking {len(hands)}, hands.", end="")
        #Land mark values = (x,y) * 21 (total number of points we have per hand)

        if hands:
            for i in range(len(hands)):
                #Por cada mano detectada almacena los datos
                name = files[i]
                t = Thread(target=_saveData,
                                     args=(hands[i],depth_frame,
                                           name,files[name],fd_obj,verbose))
                t.start()
                threads.append(t)
                #Añade uno al contador de la carpeta
                files[name] += 1
                #Resetea el contrador cuando alcanza el límite y empieza a reemplazar archivos viejos
                if files[name] > LIMIT: files[name] = 0

        for t in threads: t.join() #Une todos los hilos
        
        #Mostrar la img. actual captada por la cámara
        if image: cv2.imshow("Image", color_frame)

        key = cv2.waitKey(1)
        if key == 32: break #Cierra el programa si se presiona BARRA ESPACIADORA
    print("\nProcess aborted...")


def _get_locations_list (image,detector,hand_obj) -> list:
    """
    Función que retorna la localización de los puntos encontrados

    Args:
        hand_obj(mediapipe obj): Objeto con todos los datos capturados
        image (numpy.ndarray): Imagen capturada por la cámara
        detector (mediapipe.python.solutions.hands.Hands): Info proveniente del algoritmo de detección

    Returns:
        lista: Lista de puntos localizados
    """
    #Altura y ancho de la imagen
    height = image.shape[0]
    width = image.shape[1]
    results = detector.process(image)
    hands_data=[]#Lista de listas de localizaciones

    if results.multi_hand_landmarks:#En caso de que una mano sea encontrada
        for hand_no, hand_landmarks in enumerate(results.multi_hand_landmarks):#por c/mano encontrada
            temp = []
            for i in range(21):#Obtiene solo las localizaciones en X y Y
                res = hand_landmarks.landmark[hand_obj.HandLandmark(i).value]

                #núm. es multiplicado por el ancho y altura para obtener la localización dentro de la imagen
                x = int(res.x*width)
                y = int(res.y*height)

                temp.append([x,y])
            hands_data.append(temp)
    
    return hands_data


def _socketList(n):
    """
    Crea n cantidad de sockets UDP

    Args:
        n (int): no. de sockets a crear

    Returns:
        lista, tupla: Listas de sockets y puertos
    """
    #Lista de conexiones UDP
    SKs =[]
    SAPs = []
    #Asigna a cada una un puerto diferente con el cual comunicarse
    for i in range(n):
        sk, serverAddPort = _setSocket(5001+i)
        SKs.append(sk)
        SAPs.append(serverAddPort)
    return SKs,SAPs


def _setSocket(port):
    """
    Crear un socket de conexión UDP para transmitir datos a unity

    Returns:
        socket,tuple: Lista de sockets del puerto y tupla con IP y puerto
    """
    sk = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #port to send to (ip, port)
    serverPort = ("127.0.0.1", port)
    return sk,serverPort


def _location_Error_Filter (locations):
    """
    Fitlra valores con errores causados en la detección de profundidad

    Args:
        locations (tupla): Locs. x, y del punto medio

    Returns:
        tupla: Locs. fijas
    """
    x,y = locations
    if x >= 480:
        x = 479
    if y >= 479:
        y=478
    return x,y


def write_File(file_loc, locations,unity_h,dist,gesture):
    """
    Escribe los datos en el archivo txt especificado en la carpeta apropiada

    Args:
        file_loc (string): Path en el que se almacenará el archivo txt
        locations (list): Lista de locs. de los puntos de la mano detectados
        unity_h (int): Píxeles Y invertidos para su reconocimiento en unity
        dist (int): Altura de la mano detectada por el sensor de profundidad
        gesture(str): Gesto interpretado
    """
    with open(file_loc,"w") as file: #Guarda la info. en el archivo correspondiente
        for loc in locations:
            file.write(f"{loc[0]},{unity_h - loc[0]},{loc[1]}\n")
        file.write(f"{dist}\n{gesture}")


def _gesture_interpretor (landMarks,fd_obj)-> str:
    """
    Retorna la interpretación del gesto basándose en los resultados obtenidos por la clase Finger_detector

    Args:
        landMarks (list): Lista de puntos de la mano detectados

    Returns:
        str: Interpretación basada en criterios
    """

    flex_list,pinch_flag = fd_obj.detect(landMarks)
    #True= dedo estirado, False = contraido
    if pinch_flag: return "Pinch"

    #Mano abierta
    if len(set(flex_list)) == 1 and flex_list[0]: return "Open hand"

    #Puño
    if len(set(flex_list)) == 1 and not flex_list[0]: return "Fist"

    #Dedos abiertos (no toma en cuenta el pulgar)
    if all (flex_list[i]==True for i in range(len(flex_list)-1)): return "Open fingers"

    #Apuntando 1 dedo
    if flex_list[0]:
        for i in range(1,len(flex_list)):
            if not flex_list[i]:
                pass
            
        return "Pointing"
    
    #Mano en forma de L
    if flex_list[0] and flex_list[1] and all(flex_list[i]==True for i in range(1,len(flex_list)-1)):
        return "L"

    return ""


def _saveData(hand,depth_frame,name,n,fd_obj,show = False):
    """
    Registra loc. de un punto de la mano y la distancia general de la cámara 
    a un archivo específico en un path correspondiente
    
    Tan pronto como el ciclo alcanza su límite con el archivo previo,
    con la misma 'n' serán reemplazados los
    archivos viejos con datos nuevos para no abrumar el almacenamiento.

    Args:
        hand (list): Lista de info. de la mano seleccionada
        depth_frame (frame): Imagen de la percepción de profundidad de la cámara
        name (string): Nombre del folder en el que se guardará el archivo
        n (int): Iteración del archivo
    """
    height = 1200 #Altura utlizada para invertir el eje Y para unity

    #Obtiene la localización del centro de la mano
    x,y = _location_Error_Filter(fd_obj._middle(hand[9][0],hand[0][0],hand[9][1],hand[0][1]))

    try:
        dist = depth_frame[x,y] #Obtiene la distancia estimada del centro de la mano desde la cámara
    except Exception as e:
        print("Error")
    
    location = f"./Hand_{name}/[{n}].txt" #Hand_A/[0]

    gesture = _gesture_interpretor(hand,fd_obj)

    write_File(location,hand,height,dist, gesture) 
    if show: print(f"\rHand {name}: {gesture}", end="")




if __name__ == "__main__":
    main(1,10000,image=True,verbose=False)
    print("Ending program")
