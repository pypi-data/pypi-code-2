# logic.py    [Sudoku Solver 1.0]
# -*- coding: UTF-8 -*-

"""This module is the powerhouse of this app! The functions in this module
determine the performance of this app. These functions are not easy to
understand in one single reading.

Solving a Sudoku puzzle requires two approaches -
    1. Solving it exactly, with no assumptions.
       In this approach, we try to fill the puzzle 'exactly' as far as
       possible. This is the simplest approach and the puzzle won't be
       significantly solved in most cases.
    2. Solving it using assumptions.
       When unable to solve any further using the 1st approach, we resort
       to this approach. In this, we make an assumption. Then try to solve
       it further using the 1st approach.
       Sometimes, we have to take assumptions over assumptions which makes
       things more complicated.
	
	To see the steps taken in solving, refer to documentations of the
        functions Step1 and Stepk
	
EXTRA NOTES:
 1. This module would be much faster if you make all the calculations on temp
 variables and then in the end fill the sudokugrid instead of doing it
 directly on the sudokucells. (Calling everytime the function
 sudokupanel.SetSudokuCellLabel is very expensive, better if it is called only
 once in the end after the solution is found.) But, however, our purpose here
 is to just to be able to solve a Sudoku puzzle in an efficient way, not
 necessarily the fastest way possible.
 Hopefully, I will implement this in the next version of Sudoku Solver

 2. One more feature that can be implemented is -
 Instead of dealing with labels which have only 2 possibilities, we can deal
 with labels with 3,4,5,.. possibilities. In this way we would be able to
 fill even an empty grid! (Think how!) However, this is not required as any
 Sudoku puzzle can be solved using the above approaches.
 
"""

__author__ = "Pushpak Dagade (पुष्पक दगड़े)"
__date__   = "$May 23, 2011 7:59:05 PM$"

from sudokucell import SudokuCell

def printlong(character):
    print character*20, '\n'

# XXX. Change the code of the 2 below functions from the saved copies
# as this is getting slower!
# Also solve the intermixing of Assumption levels and steps!

def SolveSudokuPuzzle(sudokupanel, MaxAssumptionLevel=4):
    """Solves the Sudoku Puzzle with MaxAssumptionLevel.

    MaxAssumptionLevel = 3 can solve almost all sudoku puzzles which have a
    solution. But, just to be on a safe side, keep the MaxAssumptionLevel = 4
    (I have not found any puzzle requiring 4 or more levels of assumption
    to solve it.)

    """
    printlong('=')
    print "Max no of Assumptions: %d\n" %(MaxAssumptionLevel)
    SolveUptoSteps(MaxAssumptionLevel+1, sudokupanel)
    printlong('=')

def SolveUptoSteps(MaxSteps, sudokupanel, tree = []):
    """Solve from steps 1 to MaxAssumptionLevel (including both)"""
    if MaxSteps == 1:
        Step1(sudokupanel)
        
    elif MaxSteps > 1:
        Step1(sudokupanel)

        for k in xrange(2, MaxSteps+1):
            solved = Stepk(k, sudokupanel, tree)
            if solved == 1: break

def Step1(sudokupanel):
    """Try to solve the puzzle "exactly" (as far as possible).

    This is very first step in solving the puzzle and hence the name- 'Step1'.
    It uses 2 algorithms to solve the puzzle exactly.
    -----------------
    1st algorithm -
    -----------------
    Fill all the empty sudokucells which have only 1 permissible label
    other than '' (empty string) (ie a total of 2 permissible
    labels) with the non empty permissible label.

    -----------------
    2nd alogrithm -
    -----------------
    If a particular label (in SudokuCell.Labels) is possible in
    only one sudokucell in a row then that label is can be
    confidently set to that sudokucell. (Note: row, col and box approaches
    are all symmetric, so you can apply this rule by replacing row by
    column (or box) and you will get the same result. But there is no need
    to apply it for both row and column (and/or box) because it will
    unnecssarily waste cpu time. Just one check (either row or column
    or box) is enough (this can be proved.)) This check must be made for every
    possible label in SudokuCell.Labels (except for '' (empty string))
    in every row (or column or box, which ever you used before.)
    Once you get a sure hit, break from this algorithm immediately
    and go for the 1st algorithm (as this one is much more time
    complex.)

    The variable data_changed will let know if the puzzle has been solved
    any further in any of the two algorithms. If data_changed is 1 then loop
    will continue to cycle through algorithms 1 and 2, else it will break.
    
    """
    print '(Solving exactly...)'
    if not sudokupanel.IsPuzzleComplete():        
        data_changed = 1
        
        while data_changed:
            data_changed = 0

            # 1st algorithm -
            for sudokucell in sudokupanel:
                if sudokucell.IsEmpty():
                    labelspermissible = sudokucell.LabelsPermissible()[1:]
                    # labelspermissible[0] is '' (empty string),
                    # hence the slicing.
                    if len(labelspermissible) == 1:
                        sudokupanel.SetSudokuCellLabel(sudokucell,
                                            labelspermissible[0])
                        print '(%d,%d) --> %s' %(sudokucell.posx+1,
                          sudokucell.posy+1, labelspermissible[0])
                        data_changed = 1

            # This might help in improving the time complexity as the
            # 2nd alogrithm is more time complex.
            if data_changed == 1: continue

            # 2nd algorithm -
            labels = SudokuCell.Labels[1:]
            for rowofcells in sudokupanel.sudokucells:
                for label in labels:
                    count = 0
                    for sudokucell in rowofcells:
                        if sudokucell.IsEmpty() and \
                           sudokucell.IsLabelPermissible(label):
                            count += 1
                            if count > 1: break
                            temp_cell = sudokucell
                    if count == 1:
                        sudokupanel.SetSudokuCellLabel(temp_cell, label)
                        print '(%d,%d) --> %s' %(temp_cell.posx+1,
                          temp_cell.posy+1, label)
                        data_changed = 1

            # XXX. 2nd algorithm can be made more efficient by removing from
            # the variable 'labels' those labels which are already filled
            # everywhere.

def Stepk(k, sudokupanel, basetree = []):
    """Try to solve the puzzle using assumptions.

    k --> The step number. (1st step is solving exactly,
          2nd step is solving using 1 assumption,
          3rd step is solving using 2 assumptions and so on.)
    Note: The assumption level of this step will be k-1.
    
    basetree --> list of parent assumption levels.
                 It helps in getting the tree structure of (nested)
                 assumptions.
    Example- basetree = [3,2] --> This means that this Stepk function has been
    called (recursively) from another Stepk function (with k = 3) which was
    itself called from another Stepk function (with k = 4).

    ==============
    Return value:
    ==============
    1 - puzzle was solved in this step.
    0 - puzzle was not solved in this step.

    """
    # Note: If the puzzle being solved does not have a unique solution and
    # the parameter k is large (say 5 or more) then this function will give
    # one of the many possible solutions.
    # But whichever solution it gives, it will be definately correct!

    print('(Checking if complete...)\n')
    if sudokupanel.IsPuzzleComplete():
        return 1
    
    else:
        printlong('-')
        assumptionleveltree = basetree + [k-1]
        print "(Assumption Level Tree: %s)\n"\
          "(Saving puzzle...)\n" %(assumptionleveltree)
        initialpuzzle = sudokupanel.GetPuzzle()
        only2 = sudokupanel.GetSudokuCellsWithOnly2Possibilities()

        for sudokucell in only2:
            labelspermissible = sudokucell.LabelsPermissible()[1:]
            # The first permissible label is '' (empty string),
            # hence the slicing.
            temppuzzle = None

            # This 'for ... loop' is for trying both the labels in
            # labelspermissible as assumptions.
            for label in labelspermissible:
                otherlabel = labelspermissible[labelspermissible.index(label)-1]
                print "Trying %s in cell (%d,%d)\n[Other can be %s]\n" \
                  %(label, sudokucell.posx+1, sudokucell.posy+1, otherlabel)
                sudokupanel.SetSudokuCellLabel(sudokucell, label)
                
                if not k==2: print '(Entering another assumption...)\n'
                SolveUptoSteps(k-1, sudokupanel, assumptionleveltree)
                if not k==2: print '(Exiting from assumption...)\n'

                print '(Checking if complete...)\n'
                if sudokupanel.IsPuzzleComplete():
                    # This means that the assumption taken above was correct
                    # and the puzzle got solved. Hence, return 1.
                    print "Breaking (Assumption Level Tree: %s)\n"\
                      "Puzzle Solved!\n" %(assumptionleveltree)
                    return 1

                else:
                    print '(Checking if correct..)\n'
                    if sudokupanel.IsPuzzleCorrect():
                        # This means that the puzzle is incompletely filled
                        # and it cannot be decided from this point whether
                        # the assumption taken above is correct or
                        # incorrect.
                        print "Can't say anything for the assumption- \n"\
                          "%s in cell (%d,%d)\n"\
                          %(label, sudokucell.posx+1, sudokucell.posy+1)

                        # caching
                        if labelspermissible.index(label) == 0:
                            # This is caching, for speeding up the solve
                            # process. If 'label' is the 1st of the 2
                            # permissible labels then save the solution, it
                            # might be possible that the 2nd of the 2
                            # permissible options is definately incorrect,
                            # (and consequently this assumption is correct)
                            # so we will need this solution!
                            # (better to save it, rather than finding it
                            # again later.)
                            print "Saving solved puzzle temporarily before" \
                              " reverting. It will be useful if the 2nd" \
                              " permissible label is definately incorrect.\n"
                            temppuzzle = sudokupanel.GetPuzzle()

                        # As it cannot be decided standing at this point
                        # whether the above assumption is correct or incorrect,
                        # revert to initial conditions and try the other
                        # options!
                        print "Reverting to the puzzle saved at the beginning"\
                          " of this assumption level...\n"
                        printlong('-')
                        sudokupanel.SetPuzzle(initialpuzzle)

                    else:
                        # This means that puzzle is incorrectly filled, so it is
                        # sure that the above asumption is definately incorrect,
                        # so the other among the 2 permissible labels is
                        # definately correct.
                        print "This choice is definately incorrect-\n" \
                          "%s in cell (%d,%d).\n" \
                          "The other one must be definately correct-\n" \
                          "%s in cell (%d,%d).\n" \
                          %(label, sudokucell.posx+1, sudokucell.posy+1,
                          otherlabel ,sudokucell.posx+1, sudokucell.posy+1)

                        # decide whether label is the 1st of the permissible
                        # labels or the 2nd one.
                        if labelspermissible.index(label) == 1:
                            # This means that the assumption we took ( 2nd of
                            # the 2 permissible labels) is incorrect,
                            # and as this assumption is incorrect, the 1st
                            # of the 2 assumptions is definately correct.
                            # Moreover, the puzzle solution to the 1st
                            # permissible label is already saved in
                            # temppuzzle, so just load it.
                            print "It is good that I had saved the" \
                              " solution puzzle for the 1st assumption." \
                              " I will revert to this puzzle directly.\n"
                            sudokupanel.SetPuzzle(temppuzzle)
                            
                        else:
                            # This means that 2nd of the 2 permissible labels
                            # is correct, so revert to the puzzle that was
                            # at the beginning of the outermost for loop and
                            # then set the 2nd of the 2 permissible labels.
                            sudokupanel.SetPuzzle(initialpuzzle)
                            sudokupanel.SetSudokuCellLabel(sudokucell,
                                                labelspermissible[1])

                        # Delete all the variables defined at this point, as
                        # this function will be going into a recursive loop
                        # from here on, and this data, unnecessarily, will
                        # form a stack.
                        del initialpuzzle
                        del only2
                        del labelspermissible
                        del temppuzzle                        

                        printlong('-')

                        # Now, the puzzle solution has moved one step ahead,
                        # so try to solve it further using the "less complex",
                        # "previous" steps.
                        if not k==2: print '(Entering another assumption...)\n'
                        SolveUptoSteps(k-1, sudokupanel, assumptionleveltree)
                        if not k==2: print '(Exiting from assumption...)\n'

                        # Finally, repeat this step again to solve the puzzle
                        # further. (it is quite possile that in the previous
                        # step itself, the puzzle might have got solved. If so,
                        # it will just enter this function (in recursion) and
                        # return from the very 1st check)
                        return Stepk(k, sudokupanel, basetree)

    # If this part is getting executed means this function did not help
    # in solving the puzzle any further.
    print "Didn't get anything from this Assumption Level Tree: %s ':(' \n" \
      %(assumptionleveltree)
    return 0
