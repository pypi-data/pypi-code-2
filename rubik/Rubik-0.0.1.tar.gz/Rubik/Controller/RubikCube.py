import visual
import Rubik.Model.Cube
import Rubik.Controller.CubeMover
import Rubik.View.Cube3DView

class RubikCube:
    """ A controller class for Rubik's Cube game.

    Attributes:

    Methods:

    Doctests:

    """
        
    def __init__(self):
        """ Constructor for RubikCube class.

        Parameters:
            -- None

        Side Effects:
            -- All the cube and view objects are created
        
        Results:
            -- None
        """
                
        self.__cube=Rubik.Model.Cube.Cube()
        self.__mover=Rubik.Controller.CubeMover.CubeMover(self.__cube)
        self.__view=Rubik.View.Cube3DView.Cube3DView(self.__cube)

        self.__rate=50

    def run(self):
        """ The main game loop.

        Parameters:
            -- None

        Side Effects:
            -- Control the main loop of the game
        
        Results:
            -- None
        """

        disp=self.__view.getDisplay()
        kb=disp.kb
        
        while True:
            visual.rate(self.__rate)

            k=''
            if kb.keys: # event waiting to be processed?
                k=kb.getkey() # get keyboard info
                if len(k) != 1: 
                    k=''

            if k=='':
                pass            
            elif k=='q':
                self.__view.close()
            elif k=='?':
                self.__view.help()
            elif k=='s':
                self.__mover.shuffle()
                self.__view.show()
            elif k=='x':
                self.__mover.reset()
            else:
                try:
                    self.__mover.move(k)
                    self.__view.show()
                except ValueError:
                    print 'Invalid move'
   
