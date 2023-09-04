from matplotlib import pyplot as plt,patches
from numpy import array
import pandas as pd

class DrawPoints():
    def __init__(self) -> None:
        self.fig = plt.figure()
    
    def start(self,centerX, centerY, radius, list_x, list_y, File_name ='test.png'):
        self._markDots(list_x,list_y)
        self._drawCircle(centerX,centerY,radius)
        self._saveData(File_name)
        print(f"File saved as: {File_name}")

    def _saveData(self, Name):
        self.fig.savefig(Name)

    def _drawCircle(self,x,y,rad):
        ax = self.fig.add_subplot()
        circle1 = patches.Circle((x, y), radius=rad,fill=False)
        ax.add_patch(circle1)
        ax.axis('equal')

    def _markDots(self,x:list,y:list):
        plt.scatter(x,y)
        plt.grid(axis = "both")

