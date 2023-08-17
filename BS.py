from main import DepthCamera
from os import system

dc = DepthCamera()
ret, depth_frame, color_frame = dc.get_frame() #get the frame objects
point = (400,300)
deadpoints =[]
for y in range(480):
    for x in range(470):
        ret, depth_frame, color_frame = dc.get_frame()

        #obtain the distance (y,x)
        try:
            distance = depth_frame[x,y]
            if distance == 0:
                deadpoints.append((x,y))
                res = "No distance..."

        except Exception as e:
            deadpoints.append((x,y))
        
        res += str(x)+","+str(y)
        
        print(res)
        res = ""
    system("cls")
with open("deadpoints.txt","w") as file:
    for row in deadpoints:
        file.write(str(row))