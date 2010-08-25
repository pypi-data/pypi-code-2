from visual import *
import Rubik.Model.Cube

class Cube3DView:
    """ A rubik's cube view class for 3d representation of the cube.

    Attributes:
        -- __cube - the rubik's cube
        -- __display - the visual display object where all 3D objects are constructed

    Methods:
        -- initScene - Initialize the visual scene for 3D object viewing
        -- initView - Initialize the 3D cube for viewing
        -- show - show the 3D cube for viewing
        -- getDefaultColor - Get the default color for a face
        -- getColor - Get the color for a face
        -- getCube - Getter method for the cube attribute
        -- setCube - Setter method for the cube attribute
        -- getDisplay - Getter method for the display attribute
        -- close - Close the current window
        
    Doctests:
    """

    def __init__(self,cube=None):
        """ Constructor for Cube3DView class.

        Parameters:
            -- cube - the rubik's cube

        Side Effects:
            -- create and initialize the cube mover class

        Results:
            --None
        """

        self.__display=None
        self.initScene()

        if cube is None:
            self.__cube=None
        else:
            self.setCube(cube)


    def initScene(self):
        """ Initialize the visual scene for 3D object viewing.

        Parameters:
            -- None

        Side Effects:
            -- Initialize the visual scene

        Results:
            --None
        """

        if self.__display is not None:
            return
        
        self.__display=display(title='Rubik\'s Cube', x=0, y=0, width=800, height=600)

        self.__display.background=(0.3,0.6,0.9)
        #self.__display.exit=False
        self.__display.cursor.visible=True
    
        self.__display.autoscale=False
        self.__display.range=(5,5,5)
        self.__display.center=(0,0,0)
        self.__display.forward=(1,-1,-1)

        #self.__display.lights=[]
        self.__display.ambient=0.4
        self.__display.material=materials.plastic

        self.__display.userspin=False
        self.__display.userzoom=False

        self.__display.select()        

        #l = local_light(pos=(0,0,0), color=(0,0,1),magnitude=1)
        #lamp=sphere(pos=l.pos,radius=0.5,material=materials.emissive,opacity=1,color=color.red)

    def initView(self):
        """ Initialize the 3D cube for viewing.

        Parameters:
            -- None

        Side Effects:
            -- The cube array is populated 

        Results:
            --None
        """

        if self.__cube is None:
            return

        d=self.__cube.getDimension()

        self.__pieces=[[[None for k in range(d)] for j  in range(d)] for i  in range(d)]
        self.__faces=[[[[[None for n in range(2)] for m in range(3)] for k in range(d)] for j  in range(d)] for i  in range(d)]

        for i in range(d):
            for j in range(d):
                for k in range(d):
                    self.__pieces[i][j][k]=frame(pos=(i-1,j-1,k-1))
                    for m in range(3):
                        for n in range(2):
                            if m==0:
                                f=box(frame=self.__pieces[i][j][k],size=(0.1,0.7,0.7),pos=(0.8*n-0.4,0,0))
                            elif m==1:
                                f=box(frame=self.__pieces[i][j][k],size=(0.7,0.1,0.7),pos=(0,0.8*n-0.4,0))
                            elif m==2:
                                f=box(frame=self.__pieces[i][j][k],size=(0.7,0.7,0.1),pos=(0,0,0.8*n-0.4))

                            f.color=self.getDefaultColor([m,n])

                            v=[i,j,k]
                            if v[m]==n*2:
                                f.opacity=1
                            else:
                                f.color=color.gray(0.7)
                                f.opacity=1

                            self.__faces[i][j][k][m][n]=f

                            for p in range(2):
                                if m==0:
                                    c=cylinder(frame=self.__pieces[i][j][k],axis=(0.7,0,0),pos=(-0.35,0.7*n-0.35,0.7*p-0.35),radius=0.1)
                                elif m==1:
                                    c=cylinder(frame=self.__pieces[i][j][k],axis=(0,0.7,0),pos=(0.7*p-0.35,-0.35,0.7*n-0.35),radius=0.1)
                                elif m==2:
                                    c=cylinder(frame=self.__pieces[i][j][k],axis=(0,0,0.7),pos=(0.7*n-0.35,0.7*p-0.35,-0.35),radius=0.1)

                                c.color=color.gray(0.7)
                                c.opacity=1

                                if m!=2:
                                    s=sphere(frame=self.__pieces[i][j][k],pos=(0.7*m-0.35,0.7*n-0.35,0.7*p-0.35),radius=0.105)
                                    s.color=color.gray(0.7)
                                    s.opacity=1

    def show(self):
        """ show the 3D cube for viewing.

        Parameters:
            -- None

        Side Effects:
            -- The cube is displayed

        Results:
            --None
        """
        
        if self.__cube is None:
            return
        if self.__pieces is None:
            return
        if self.__faces is None:
            return
        
        d=self.__cube.getDimension()

        for i in range(d):
            for j in range(d):
                for k in range(d):
                    for m in range(3):
                        for n in range(2):
                            self.__faces[i][j][k][m][n].color=self.getColor(self.__cube.getPieces()[i][j][k].getSides()[m][n].getColor())

                            v=[i,j,k]
                            if v[m]==n*2:
                                self.__faces[i][j][k][m][n].opacity=1
                            else:
                                self.__faces[i][j][k][m][n].color=color.gray(0.7)
                                self.__faces[i][j][k][m][n].opacity=1


    def help(self):
        """ Shows the help screen.

        Parameters:
            -- None

        Side Effects:
            -- The cube is hidden and help menu is displayed

        Results:
            -- None
        """
        pass
                                
    def getDefaultColor(self,index):
        """ Get the default color for a face.

        Parameters:
            -- index - the index representing the direction of the face

        Side Effects:
            -- None

        Results:
            -- the default color
        """

        if type(index)!=type(list()):
            raise TypeError("The parameter index takes list")
        if len(index)!=2:
            raise ValueError("The parameter index must be a list of 2 indices")
        if index[0]<0 or index[0]>2:
            raise ValueError("The parameter index supplied is not valid")
        if index[1]<0 or index[1]>1:
            raise ValueError("The parameter index supplied is not valid")
            
        return self.getColor(index[0]*2+index[1]+1)

    def getColor(self,index):
        """ Get the color for a face.

        Parameters:
            -- index - the index representing the color type

        Side Effects:
            -- None

        Results:
            -- the default color
        """

        colors=[color.gray(0.7),color.blue,color.green,color.white,color.yellow,color.orange,color.red]
        if type(index)!=type(int()):
            raise TypeError("The parameter index takes integer value")
        if index<0 or index>6:
            raise ValueError("The parameter index supplied is not valid")
            
        return colors[index]
                                                
    def getCube(self):
        """ Getter method for the cube attribute.

        Parameters:
            -- None

        Side Effects:
            -- None
            
        Results:
            -- the cube
        """

        return self.__cube            

    def setCube(self,cube):
        """ Setter method for the cube attribute.

        Parameters:
            -- cube - the rubik's cube

        Side Effects:
            -- None
            
        Results:
            -- the cube
        """

        if type(cube)!=type(Rubik.Model.Cube.Cube()):
            raise TypeError('The parameter cube takes Cube object')

        self.__cube=cube
        self.initView()

    def getDisplay(self):
        """ Getter method for the display attribute.

        Parameters:
            -- None

        Side Effects:
            -- None
            
        Results:
            -- the scene
        """

        return self.__display 

    def close(self):
        """ Close the current window.

        Parameters:
            -- None

        Side Effects:
            -- The display is closed and the program exits
            
        Results:
            -- None
        """

        if self.__display is not None:
            self.__display.visible=False
