from cv2 import imwrite,VideoCapture
from os import mkdir, system
from time import sleep

cam = VideoCapture(1)

gestures = 3
start = 200
photos= 300
for i in range(gestures):#Folder
    location = f"./{i}"

    try:
        mkdir(location)
    except Exception as e:
        print("Folder already exists...\n")

    for j in range(start,photos+1):#Image
        result, image = cam.read()
        imwrite(f"{location}/{j}.jpg", image)
        print(f"Photo: {j}")
        sleep(0.05)
        print("Done")
        system("cls")
    print("Folder completed...\n")

    for x in range(3):
        print(f"\rStarting folder {i} in {3-x}",end="")
        sleep(0.8)
    system("cls")