import cv2
from time import sleep

location = "C:/Users/CIICCTE/Desktop/DataSet/"
cam = cv2.VideoCapture(1)

print ("Starting new batch...")
sleep(1)

for i in range (2):
    for j in range(300):
        result, image = cam.read()
        final_loc = location+str(i)+"-"+str(j)+".png"
        cv2.imwrite(final_loc, image)
    print (f"Batch {i} DONE")
    if i == 0:
        for j in range (3):
            print(3-j)
            sleep(1)
print("Finnished")
    