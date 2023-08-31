from math import sqrt,pow

class Finger_detector:

    def fingerStraight(x1:int,x2:int,y1:int,y2:int,tx:int,ty:int,self) -> bool:
        """
        Obtiene el punto medio entre la localización de la punta del Metacarpo y la punta de la falange intermedia.
        Dibuja un círculo de un radio determinado en dicha localización.
        Si la punta de la falange proximal está entre el radio del círculo , pero la falange intermedia y el metacarpo
        no están dentro del círculo entonces se sabe que el dedo está derecho.
        En dicho caso, será dibujado un círculo.
    
        Args:
            x1 (int): Localización de X de la base del dedo
            x2 (int): Localización de X de la punta del dedo
            y1 (int): Localización de Y de la base del dedo 
            y2 (int): Localización de Y de la punto del dedo 
            tx (int): Localización de X del hueso medio del dedo 
            ty (int): Localización de Y del hueso medio del dedo 

        Returns:
            bool: True si el dedo se encuentra derecho, False si el dedo no está derecho
        """
        rad = 20
        x,y= self.middle(x1,x2,y1,y2)
        mid = self.isInside(x,y,rad,tx,ty)
        base = self.isInside(x,y,rad,x1,y1)
        tip = self.isInside(x,y,rad,x2,y2)
        
        if mid and not base and not tip:
            return True
        else : return False

    
    def thumb_contracted(hand_x, hand_y, thumb_x, thumb_y,self) -> bool:
        """
        Dibuja un círculo entre la mano y el pulgar para detectar si el pulgar está extendido o no

        Args:
            hand_x (int): Localización de X de la mano
            hand_y (int): Localización de Y de la mano
            thumb_x (int): Localización de X de la parte media del pulgar
            thumb_y (int): Localización de Y de la parte media del pulgar

        Returns:
            bool: Retorna True si el pulgar no está extendido, False en caso contrario 
        """
        rad = 35
        x,y = self.middle(hand_x,thumb_x,hand_y,thumb_y)
        return not self.isInside(x,y,rad,thumb_x,thumb_y)


    def detect_pinch(x1:int,y1:int,x2:int,y2:int,x3:int,y3:int, index:bool, thumb:bool,self) -> bool:
        """
        Detecta si la mano está haciendo el gesto similar al de pellizco 
        basándose en la distancia entre el pulgar y el dedo índice
    
        Args:
            x1 (int): Localización de X de la punta del pulgar
            y1 (int): Localización de Y de la punta del pulgar
            x2 (int): Localización de X de la punta del índice
            y2 (int): Localización de Y de la punta del índice
            x3 (int): Localización de X del punto medio del pulgar
            y3 (int): Localización de X del punto medio del pulgar
            index (bool): True, si el dedo está extendido
            thumb (bool): True, si el pulgar no está contraido
    
        Returns:
            bool: True, si el usuario está haciendo el gesto de pellizco
        """
    
        #si el índice está contraido y el pulgar no
        if (not index and thumb):
            d1 = self.dist_2_points(x1,x3,y1,y3) #Distancia entre punto 4 y 3
            d2 = self.dist_2_points(x1,x2,y1,y2) #Distancia entre punto 4 y 8
    
            if d1>d2:
                return True
        
        return False

    
    def detect(lmList, self) -> tuple:
        """
        Retorna una tupla, el 1er elemento es una lista de booleanos indicando si un dedo está contraido 
        basándose en su localización.
        El 2do elemento es un booleano indicando si la mano está haciendo el gesto de pellizco.
    
        Args:
            lmList (array): Arreglo de id, localización de X, localización de Y
                            de un punto en específico en la mano
    
        Returns:
            tupla: tupla con los resultados detectados
        """
        #ID de cada dedo y sus partes
        #[índice, medio, anular, meñique, pulgar]
        #(punta, base, medio)
        locations = [(8,5,6),(12,9,10),(16,13,14),(20,17,18)]
    
        #[índice, medio, anular, meñique, pulgar]
        fingers = [False,False,False,False,False] #True = dedo se encuentra extendido
        counter = 0
        pinch = False
    
        if len(lmList)!=0:
            for i in locations:
                #[(punta, base, medio)]
                x1,x2 =lmList[i[0]][1],lmList[i[1]][1]
                y1,y2 =lmList[i[0]][2],lmList[i[1]][2]
                tx,ty =lmList[i[2]][1],lmList[i[2]][2]
    
                fingers[counter] = self.fingerStraight(x1,x2,y1,y2,tx,ty)
    
                counter += 1
            
            #Encontrar el pulgar
            hand_x, thumb_x=lmList[5][1],lmList[3][1] #Localización de X del punto 5,localización de X del punto 3
            hand_y, thumb_y=lmList[5][2],lmList[3][2] #Lo mismo, pero la localización en Y
                
            fingers[-1] = self.thumb_contracted(hand_x,hand_y,thumb_x,thumb_y) #Asigna el resultado a un arreglo
                
            pinch = self.detect_pinch(lmList[4][1],lmList[4][2],
                                 lmList[8][1],lmList[8][2],
                                 lmList[3][1],lmList[3][2],
                                 fingers[0],
                                 fingers[-1])
            
        return (fingers,pinch)

    
    def middle(x1:int,x2:int,y1:int,y2:int) -> tuple:
        """Estimar el punto medio entre dos puntos
    
        Args:
            x1 (int): localización de x del 1er punto
            x2 (int): localización de x del 2do punto
            y1 (int): localización de y del 1er punto
            y2 (int): localización de y del 2do punto
    
        Returns:
            tupla: La localización aproximada de X y Y del punto medio.
        """
        x = int((x1+x2)/2)
        y = int((y1+y2)/2)
        return x,y

    
    def isInside(circle_x:int, circle_y:int, rad:int, x:int, y:int) -> bool:
        """Encuentra el punto que está dentro de un círculo estimado
    
        Args:
            circle_x (int): Localización de X del centro del círculo
            circle_y (int): Localización de Y del centro del círculo
            rad (int): Radio del círculo en píxeles
            x (int): Localización de X del punto a encontrar
            y (int): Localización de Y del punto a encontrar
    
        Returns:
            bool: Si el punto está dentro del círculo entonces retornará True, de lo contratio retornará False
        """
        if ((x - circle_x) * (x - circle_x) +
            (y - circle_y) * (y - circle_y) <= rad * rad):
            return True
        else:
            return False

    
    def dist_2_points(x1:int, x2:int, y1:int, y2:int) -> int:
        """Encuentra la distancia entre 2 puntos
    
        Args:
            x1 (int): Localización de X del 1er punto
            x2 (int): Localización de X del 2do punto
            y1 (int): Localización de Y del 1er punto
            y2 (int): Localización de Y del 2do punto
    
        Returns:
            int: Resultado en formato de núm. entero
        """
        # _/ (x2-x1)*2 + (y2-y1)*2
        return sqrt(pow((x2-x1),2) + pow((y2-y1),2))


    #detector = htm.handDetector(detectionCon= 1)
    #finger_detector(finger_loc,detector)
    
