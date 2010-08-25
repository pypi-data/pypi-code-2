import Rubik.Model.Side

class Piece:
    """ A piece in a Rubik's cube.

    Attributes:
        -- __dimension - the dimension of the cube
        -- __position - the position of the piece referenced to the centre of the cube
        -- __initialPosition - the intial position
        -- __sides - a matrix of size 3x2 that contains all the sides of the piece

    Methods:
        -- move - rotate the piece around an axis clockwise multiple times
        -- moveOnce - rotate the piece around an axis clockwise once
        -- getIndex - get the index of the position of the piece in the cube
        -- setIndex - set the index of the position of the piece in the cube
        -- getDefaultColor - get the default color for a side in the piece
        -- getSides - get an array containing all the sides
        -- indexToPosition - converts the index of the position of the piece in the cube to the actual position of the piece
        -- directionToindex - converts the actual position of the piece to the index of the position of the piece in the cube

    Doctests:
        >>> p=Piece()
        >>> p.getIndex()
        [0, 0, 0]
        >>> p.getDefaultColor([0,0])
        1
        >>> p.move(1,1)
        >>> p.getIndex()
        [2, 0, 0]
        >>> p.moveOnce(2)
        >>> p.getIndex()
        [0, 0, 0]
        >>> p.move(2,3)
        >>> p.getIndex()
        [2, 0, 0]
        >>> p.move(0,3)
        >>> p.getIndex()
        [2, 2, 0]
        >>> p.move(1,3)
        >>> p.getIndex()
        [0, 2, 0]
        >>> p.move(2,3)
        >>> p.getIndex()
        [0, 0, 0]
        >>> p=Piece(3,[2,1,2])
        >>> p.getIndex()
        [2, 1, 2]
        >>> p.moveOnce(0)
        >>> p.move(0,3)
        >>> p.getIndex()
        [2, 1, 2]
        >>> p.indexToPosition([2,0,0])
        [1.0, -1.0, -1.0]
        >>> p.indexToPosition([1,1,2])
        [0.0, 0.0, 1.0]
        >>> p.positionToIndex([0,0,1])
        [1, 1, 2]
        >>> p.positionToIndex([-1,-1,-1])
        [0, 0, 0]
        >>> p.positionToIndex([1,-1,-1])
        [2, 0, 0]
    """
    
    def __init__(self,dimension=3,index=[0,0,0]):
        """ Constructor for the Piece class.

        Parameters:
            -- index - the index of the position of the piece in the cube
            
        Side Effects:
            -- create and initialize the piece  

        Results:
            -- None
        """
        
        self.__dimension=dimension
        self.setIndex(index)
        self.__initialPosition=self.__position[:]
        self.__sides=[[Rubik.Model.Side.Side([i,j],self.getDefaultColor([i,j])) for j in range(0,2)] for i in range(0,3)]        

    def move(self,axis,moves):
        """ Rotate the piece around an axis clockwise multiple times.

        Parameters:
            -- axis - the axis around which the piece is rotated
            -- moves - number of times the piece is rotated

        Side Effects:
            -- the position is changed

        Results:
            -- None
        """

        for i in range(moves):
            self.moveOnce(axis)
            
    def moveOnce(self,axis):
        """ Rotate the piece around an axis clockwise once

        Parameters:
            -- axis - the axis around which the piece is rotated

        Side Effects:
            -- the position is changed

        Results:
            -- None
        """
        
        if axis==0:
            t=self.__position[1]
            self.__position[1]=self.__position[2]
            self.__position[2]=-t
        elif axis==1:
            t=self.__position[2]
            self.__position[2]=self.__position[0]
            self.__position[0]=-t
        elif axis==2:
            t=self.__position[0]
            self.__position[0]=self.__position[1]
            self.__position[1]=-t

        s=[[None for j in range(0,2)] for i in range(0,3)]
        for i in range(0,3):
            for j in range(0,2):
                s[i][j]=self.__sides[i][j]
                s[i][j].move(axis)
        for i in range(0,3):
            for j in range(0,2):
                (m,n)=s[i][j].getIndex()
                self.__sides[m][n]=s[i][j]
    
    def getIndex(self):
        """ Getter method for index attribute.
        """

        index=self.positionToIndex(self.__position)
        return index

    def setIndex(self,index):
        """ Setter method for index attribute.
        """

        try:
            self.__position=self.indexToPosition(index)
        except:
            raise
                       
    def getDefaultColor(self,index):
        """ Get the default color for a side in the piece.

        Parameters:
            -- index - the index of the position of the piece in the cube

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
            
        if self.__position[index[0]]==index[1]*(self.__dimension-1)-(self.__dimension-1)/2.0:
            return index[0]*2+index[1]+1
        else:
            return 0

    def getSides(self):
        """ Getter method for the sides attribute.

        Parameters:
            -- None

        Side Effects:
            -- None
            
        Results:
            -- an array containing all the sides
        """

        return self.__sides
    
    def indexToPosition(self,index):
        """ Converts the index of the position of the piece in the cube to the actual position of the piece.

        Parameters:
            -- index - the index of the position of the piece in the cube

        Side Effects:
            -- None

        Results:
            -- the actual position of the piece
        """
        
        if type(index)!=type(list()):
            raise TypeError("The parameter index takes list")
        if len(index)!=3:
            raise ValueError("The parameter index must be a list of 3 indices")

        return [-(self.__dimension-1)/2.0+i for i in index]
        
    def positionToIndex(self,position):
        """ Converts the actual position of the piece to the index of the position of the piece in the cube.

        Parameters:
            -- position - the actual position of the piece

        Side Effects:
            -- None

        Results:
            -- the index of the position of the piece in the cube
        """

        if type(position)!=type(list()):
            raise TypeError("The parameter position takes list")
        if len(position)!=3:
            raise ValueError("The parameter position must be a list of x,y,z values")

        return [int(p+(self.__dimension-1)/2.0) for p in position]

