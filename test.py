import numpy as np
import pandas as pd
from PIL import Image
def obtainData():
    with open("deadpoints.txt","r") as f:
        data =f.read()
        lst = data.replace("(","").split(")")

    for row in range(len(lst)):
        x = lst[row]
        x= x.split(",")
        lst[row]=x

    df = pd.DataFrame(lst,columns=["x","y"])
    df["x"] = pd.to_numeric(df['x'], errors='coerce').fillna(0).astype(int)
    df["y"] = pd.to_numeric(df['y'], errors='coerce').fillna(0).astype(int)
    return df

df= obtainData()
width = df["x"].max()+1
height = df["y"].max()+1
img = Image.new(mode="1",size=(width,height))

for indx in df.index:
    img.putpixel( (df["x"][indx], df["y"][indx]), 1)
    
img.show()
img.save("Blind spot.png")