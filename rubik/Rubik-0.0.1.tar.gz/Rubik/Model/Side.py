class Side:
    """ A side or label of a piece in Rubik's cube.

    Attributes:
        -- __direction - a vector from the centre of the piece to the centre of the side
        -- __initialDirection - it holds the initial direction
        -- __color - color of the side

    Methods:
        -- move - move the side
        -- getIndex - get the index of the position of the side in the piece
        -- setIndex - set the index of the position of the side in the piece
        -- getColor - get the color of the side
        -- setColor - set the color of the side
        -- indexToDirection - converts index of the position of the side in the piece to direction
        -- directionToindex - converts direction to index of the position of the side in the piece

    Doctests:
        >>> s=Side()
        >>> s.getIndex()
        [0, 0]
        >>> s.getColor()
        0
        >>> s.move(0)
        >>> s.getIndex()
        [0, 0]
        >>> s.move(1)
        >>> s.getIndex()
        [2, 0]
        >>> s.setIndex([1,1])
        >>> s.getIndex()
        [1, 1]
        >>> s.move(0)
        >>> s.getIndex()
        [2, 0]
        >>> s.setColor(6)
        >>> s.getColor()
        6
        >>> s.setColor(0)
        >>> s.getColor()
        0
        >>> s=Side([2,0],3)
        >>> s.getIndex()
        [2, 0]
        >>> s.getColor()
        3
        >>> s.move(1)
        >>> s.getIndex()
        [0, 1]
        >>> s.move(2)
        >>> s.getIndex()
        [1, 0]

    """
    
    def __init__(self,index=[0,0],color=0):
        """ Constructor of Side class.

        Parameters:
            -- index - the index of the position of the side in the piece
            -- color - the color of the side
            
        Side Effects:
            -- create and initialize the side  

        Results:
            -- None
        """

        self.setIndex(index)
        self.__initialDirection=self.__direction[:]
        self.setColor(color)

    def move(self,axis):
        """ Rotate the side or label around the axis clockwise.

        Parameters:
            -- axis - the axis (0=x,1=y,2=z) around which the side or label is rotated
        Side Effects:
            -- the direction is changed
        Results:
            -- None
        """

        if type(axis)!=type(int()):
            raise TypeError('The parameter axis takes int value')
        if axis<0 or axis>2:
            raise ValueError('The parameter axis can take values from (0,1,2)')
                
        for i in range(0,3):
            if self.__direction[i]!=0:
                if axis!=i:
                    j=3-(i+axis)
                    self.__direction[j]=self.__direction[i]*((axis-i+1) % 3 -1)
                    self.__direction[i]=0
                    return

    def getIndex(self):
        """ Getter method for index attribute.
        """

        index=self.directionToIndex(self.__direction)
        return index

    def setIndex(self,index):
        """ Setter method for index attribute.
        """

        try:
            self.__direction=self.indexToDirection(index)
        except:
            raise

    def getColor(self):
        """ Getter method for color attribute.
        """
        
        return self.__color

    def setColor(self,color):
        """ Setter method for color attribute.
        """

        if type(color)!=type(int()):
            raise TypeError('The parameter color takes int value')
        if color<0 or color>6:
            raise ValueError('The parameter color can take values from (0-6)')

        self.__color=color
    
    def indexToDirection(self,index):
        """ Converts the index of the position of the side in the piece to direction

        Parameters:
            -- index - the index of the position of the side in the piece

        Side Effects:
            -- None

        Results:
            -- the direction

        Doctests:
            >>> s=Side()
            >>> s.indexToDirection([0,0])
            [-1, 0, 0]
            >>> s.indexToDirection([1,1])
            [0, 1, 0]
            >>> s.indexToDirection([2,0])
            [0, 0, -1]
        """
        
        if type(index)!=type(list()):
            raise TypeError("The parameter index takes list")
        if len(index)!=2:
            raise ValueError("The parameter index must be a list of 2 indices")

        direction=[0,0,0]
        try:
            direction[index[0]]=index[1]*2-1
        except:
            raise ValueError("The parameter index values given are not valid")
        return direction
        
    def directionToIndex(self,direction):
        """ Converts the direction to the index of the position of the side in the piece.

        Parameters:
            -- direction - the direction

        Side Effects:
            -- None

        Results:
            -- the index of the position of the side in the piece

        Doctests:
            >>> s=Side()
            >>> print s.directionToIndex([1,0,0])
            [0, 1]
            >>> s.directionToIndex([-1,0,0])
            [0, 0]
            >>> s.directionToIndex([0,1,0])
            [1, 1]
        """

        if type(direction)!=type(list()):
            raise TypeError("The parameter direction takes list")
        if len(direction)!=3:
            raise ValueError("The parameter direction must be a list of x,y,z values")

        index=[0,0]
        for i in range(0,3):
            if direction[i]!=0:
                index[0]=i
                index[1]=int(direction[i]>0)
        return index
