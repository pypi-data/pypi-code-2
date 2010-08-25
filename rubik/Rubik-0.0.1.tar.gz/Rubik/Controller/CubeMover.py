import Rubik.Model.Cube

class CubeMover:
    """ A class to control movement of the cube.

    Attributes:
        -- __cube - the rubik's cube to move
        -- __movesHistory - a list of all applied moves

    Methods:
        -- move - move the cube
        -- shuffle - shuffle the cube
        -- getCube - get the rubik's cube linked with the mover    
        -- setCube - set the rubik's cube linked with the mover

    Doctests:
        >>> cm=CubeMover(Cube())
        >>> cm.getCube().check()
        True
        >>> cm.move(['r'])
        >>> cm.getCube().check()
        False
        >>> cm.move(['ri'])
        >>> cm.getCube().check()
        True
        >>> cm.move(['r','ri'])
        >>> cm.getCube().check()
        True
    """

    Moves={'r':[0,1,1],'ri':[0,1,3],'r2':[0,1,2],'l':[0,0,3],'li':[0,0,1],'l2':[0,0,2], 
       'u':[1,1,1],'ui':[1,1,3],'u2':[1,1,2],'d':[1,0,3],'di':[1,0,1],'d2':[1,0,2], 
       'f':[2,1,3],'fi':[2,1,1],'f2':[2,1,2],'b':[2,0,1],'bi':[2,0,3],'b2':[2,0,2]}
    MoveInverse={}
    
    def __init__(self,cube=None):
        """ Constructor for CubeMover class.

        Parameters:
            -- cube - the rubik's cube

        Side Effects:
            -- create and initialize the cube mover class

        Results:
            --None
        """

        if cube is None:
            self.__cube=None
        else:
            self.setCube(cube)

        self.__movesHistory=[]

    def move(self,moveNotation):
        """ Translate move notation and apply to the cube.

        Parameters:
            -- moveNotation - the notation of the move to apply to the cube
            
        Side Effects:
            -- the cube is rearranged

        Results:
            -- None
        """
        
        if self.__cube is None:
            return

        c=self.__cube
        d=c.getDimension()

        if type(moveNotation)!=type(str()):
            raise TypeError('The parameter moveNotations takes a string')

        try:
            m=CubeMover.Moves[moveNotation]
            #for m in mv:
            c.move(m[0],m[1]*(d-1),m[2])
            self.__movesHistory.extend(moveNotation)
        except:
            raise ValueError('invalid move '+str(moveNotation))

    def shuffle(self,moves=50):
        """ Shuffle the cube by applying random moves.

        Parameters:
            -- moves - the number of moves to apply
            
        Side Effects:
            -- the cube is rearranged

        Results:
            -- None
        """
        
        import random

        if self.__cube is None:
            return

        for i in range(moves):
            mv=random.choice(CubeMover.Moves.keys())
            self.move(mv)
                        
    def reset(self):
        """ Resets the cube to its original position.

        Parameters:
            -- None
            
        Side Effects:
            -- the cube is reset

        Results:
            -- None
        """
        
        pass
                        
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
