from matplotlib import pyplot as plt,patches

class DrawPoints():
    def __init__(self) -> None:
        self.fig = plt.figure()
    
    def register(self,centerX, centerY, radius, list_x, list_y):
        self._markDots(list_x,list_y)
        #self._drawCircle(centerX,centerY,radius)

    def saveData(self, Name):
        self.fig.savefig(Name)

    def _drawCircle(self,x,y,rad):
        ax = self.fig.add_subplot()
        circle1 = patches.Circle((x, y), radius=rad,fill=False)
        ax.add_patch(circle1)
        ax.axis('equal')

    def _markDots(self,x:list,y:list):
        plt.scatter(x,y)
        plt.text(x,y)

