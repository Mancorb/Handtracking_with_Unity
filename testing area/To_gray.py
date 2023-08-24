import os
import numpy as np
from PIL import Image

for j in range(3):
    dir_path = str(j)
    for i in os.listdir(dir_path):

        location = str(j)+"/"+i

        img = Image.open(location)
        img = img.convert("L")
        img = img.save(location)