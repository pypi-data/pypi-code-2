import Rubik.Model.Piece

class Cube:
    """ A rubik's cube class.

    Attributes:
        -- __dimension - the dimension of the cube
        -- __pieces - a three dimensional array to hold all the pieces of the cube

    Methods:
        -- move - rotate aone slice of the cube around an axis clockwise multiple times
        -- check - check if the side is in its initial state
        -- getPieces - get an array containing all the pieces
        -- getDimension - get the dimension of the cube
        
    Doctests:
        >>> c=Cube()
        >>> c.check()
        True
        >>> c.move(0,2,1)
        >>> c.check()
        False
        >>> c.move(0,2,3)
        >>> c.check()
        True
        >>> c=Cube(2)
        >>> c.check()
        True
        >>> 
        >>> c.move(1,1,1)
        >>> c.check()
        False
    """

    def __init__(self,dimension=3):
        """ Constructor for Cube class.

        Parameters:
            -- dimension - the dimension of the cube

        Side Effects:
            -- create and initialize the cube

        Results:
            --None
        """
        
        self.__dimension=dimension
        self.__pieces=[[[Rubik.Model.Piece.Piece(dimension,[i,j,k]) for k in range(0,dimension)] for j in range(0,dimension)] for i in range(0,dimension)]

    def move(self,axis,distance,moves):
        """ Rotate one slice of the cube around an axis clockwise multiple times.

        Parameters:
            -- axis - the axis around which the slice of the cube is rotated
            -- distance - the distance of the slice from the BDL piece
            -- moves - number of times the slice of the cube is rotated
            
        Side Effects:
            -- the pieces are rearranged

        Results:
            -- None
        """
        
        d=self.__dimension

        p=[[None for j in range(0,d)] for i in range(0,d)]

        if axis==0:
            for i in range(0,d):
                for j in range(0,d):
                    p[i][j]=self.__pieces[distance][i][j]
                    p[i][j].move(axis,moves)
        elif axis==1:
            for i in range(0,d):
                for j in range(0,d):
                    p[i][j]=self.__pieces[j][distance][i]
                    p[i][j].move(axis,moves)
        elif axis==2:
            for i in range(0,d):
                for j in range(0,d):
                    p[i][j]=self.__pieces[i][j][distance]
                    p[i][j].move(axis,moves)

        for i in range(0,d):
            for j in range(0,d):
                (m,n,k)=p[i][j].getIndex()
                self.__pieces[m][n][k]=p[i][j]

    def check(self):
        """ Check to see if the cube is in its initial state.

        Parameters:
            -- None

        Side Effects:
            -- None

        Results:
            -- Boolean value representing if the cube is in its initial state
        """

        d=self.__dimension
        
        for i in range(0,3):
            for j in range(0,2):
                v=[j*(d-1),0,0]
                v1=v[3-i:]
                v1.extend(v[0:3-i])
                for m in range(0,d):
                    for n in range(0,d):
                        v=[j*(d-1),m,n]
                        v2=v[3-i:]
                        v2.extend(v[0:3-i])

                        p1=self.getPieces()[v1[0]][v1[1]][v1[2]]
                        p2=self.getPieces()[v2[0]][v2[1]][v2[2]]
                        if p2.getSides()[i][j].getColor()!=p1.getSides()[i][j].getColor():
                            return False
        return True
    
    def getPieces(self):
        """ Getter method for the pieces attribute.

        Parameters:
            -- None

        Side Effects:
            -- None
            
        Results:
            -- an array containing all the pieces
        """

        return self.__pieces

    def getDimension(self):
        """ Getter method for the dimension attribute.

        Parameters:
            -- None

        Side Effects:
            -- None
            
        Results:
            -- the dimension of the cube
        """

        return self.__dimension
