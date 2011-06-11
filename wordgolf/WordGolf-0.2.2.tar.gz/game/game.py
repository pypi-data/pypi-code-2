"""The golfer game"""

import golfer
import sys

class FailedShot(Exception): """A shot failed"""


holes = [[
    (1, 3, '.........@'),   
    (2, 3, '..........@'),  
    (3, 2, '......@'),
    (4, 4, '............@'),
    (5, 3, '.........@'),
    (6, 2, '.....@'),
    (7, 5, '.............@'),
    (8, 3, '.........@'),
    (9, 4, '...........@'),
   (10, 4, '.............@'),
   (11, 3, '...........@'),
   (12, 5, '.............@'),
   (13, 3, '.........@'),
   (14, 2, '......@'),
   (15, 4, '............@'),
   (16, 3, '...........@'),
   (17, 4, '............@'),
   (18, 5, '.............@'),  

],[
    (1, 3, '....*....@'),   
    (2, 3, '..*.......@'),  
    (3, 2, '..*...@'),
    (4, 4, '..*.........@'),
    (5, 3, '...*.....@'),
    (6, 2, '.....@'),
    (7, 5, '.........**..@'),
    (8, 3, '..*......@'),
    (9, 4, '...........@'),
   (10, 4, '.......**....@'),
   (11, 3, '..*.*......@'),
   (12, 5, '..*.*...*....@'),
   (13, 3, '...*.....@'),
   (14, 2, '......@'),
   (15, 4, '...**.......@'),
   (16, 3, '....*..*...@'),
   (17, 4, '..*.........@'),
   (18, 5, '.........**..@'),  
  
],[
    (1, 3, '....*....@'),   
    (2, 3, '..*~....~.@'),  
    (3, 2, '..*...@'),
    (4, 4, '..*.....~~..@'),
    (5, 3, '...*..~..@'),
    (6, 2, '.....@'),
    (7, 5, '...~~....**..@'),
    (8, 3, '..*......@'),
    (9, 4, '....~......@'),
   (10, 4, '..~~...**....@'),
   (11, 3, '..*~*......@'),
   (12, 5, '..*~*...*....@'),
   (13, 3, '...*~....@'),
   (14, 2, '......@'),
   (15, 4, '...**....~..@'),
   (16, 3, '...~*..*...@'),
   (17, 4, '..*....~~...@'),
   (18, 5, '..~~~....**..@'),  
]]


class Game(object):
    
    check_spelling = True
    
    result_types = {
        -3 : 'Albatros',
        -2 : 'Eagle',
        -1 : 'Birdie',
         0 : 'Par',
        +1 : 'Bogie', 
        +2 : 'Double bogie',
        +3 : 'Tripple bogie',
    }
    
    def __init__(self, holes, max_holes, min_length):
        """Intialise the game"""
        self.holes = holes
        self.current_hole = 1
        self.scores = []
        self.max_holes = max_holes
        self.min_length = min_length
        self.shots = 0
        #
        # Get the board and solve it
        self.board = golfer.BoardGenerator(5)
        self.solver = golfer.BoggleSolver(self.board.asRawText(), self.min_length)
        self.good_words = self.solver.found_words
        self.used = set()

    def newGame(self, game):
        """Return a new version of this game"""
        return Game(holes[game-1], self.max_holes, self.min_length)

    def startGame(self):
        """Start the game"""
        print 'Playing %d holes, min word length is %d' % (self.max_holes, self.min_length)
        par = sum([p for _, p, _ in self.holes[:self.max_holes]])
        print '-- Par is %d, Words are %d' % (par, len(self.good_words))

    def playHole(self):
        """Play the current hole"""
        #
        # Show the hole
        num, par, hole = self.holes[self.current_hole-1]
        name = 'Unknown'
        length = len(hole)
        print 'Hole %d - %s. Par %d, %d letters\n\n' % (num, name, par, length)
        #
        print 'Board\n\n%s' % self.board.asText()
        #
        shots = 0
        while True:
            if len(hole) < self.min_length:
                print 'On the green - play a word of %d letters' % self.min_length
            else:
                print '%s\t%d to go' % (hole, len(hole))
            word = raw_input('Playing %d >' % shots)
            if word == '?':
                print 'Forfeiting! Taking a tripple bogie (%d)' % (par+3)
                shots += par+3
                break
            shots += 1
            if word in self.used:
                print 'Flubbed it! (already used this)'
            elif word in self.good_words:
                if len(hole) < self.min_length:
                    if len(word) == self.min_length:
                        print 'Sunk that put!'
                        break
                    else:
                        print 'Ooops, the put missed!'
                elif len(word) == len(hole):
                    print 'Sunk it!'
                    break
                elif len(word) >= len(hole):
                    print 'Out of bounds!'
                else:
                    print 'Good shot!'
                    hole = hole[len(word):]
                    self.used.add(word)
            elif not self.solver.dictionary.contains_word(word):
                print 'Flubbed it! (not a word)'
            elif len(word) < self.min_length:
                print 'Flubbed it! (too short)'
            else:
                print 'Flubbed it! (this word is not in the board)'
        #
        if shots == 1:
            print 'A hole in one!!'
        else:
            name = self.result_types.get(shots-par, '?')
            print '%s - you shot %d' % (name, shots)
        #
        self.scores.append(shots)
        self.current_hole += 1
        if self.current_hole > self.max_holes:
            self.endGame()

    def tryHole(self):
        """Try playing the current hole"""
        if self.isEnded():
            return
        self.num, self.par, self.hole = self.holes[self.current_hole-1]
        self.name = 'Unknown'
        self.length = len(self.hole)
        self.shots = 0
        self.distance = len(self.hole)
        par = sum([p for _, p, _ in self.holes[:self.current_hole-1]])
        score = sum(self.scores)
        if par == score:
            self.score = 'Even par'
        elif par > score:
            self.score = '%d under par' % (par - score)
        else:
            self.score = '%d over par' % (score - par)
        
    def tryWord(self, word):
        """Try a word"""
        self.shots += 1
        penalty_time = penalty_shot = 0
        if word in self.used:
            raise FailedShot('%s has already been used' % word)
        elif word.lower() in self.good_words or not self.check_spelling:
            #
            # The word was good
            if len(self.hole) < self.min_length:
                if len(word) == self.min_length:
                    #
                    # Word was a "green" shot
                    self.scores.append(self.shots)
                    self.current_hole += 1
                    over = self.shots-self.par
                    self.tryHole()
                    self.used.add(word)
                    return 'Nice put', over, penalty_time, penalty_shot
                else:
                    #
                    # Word was too long
                    raise FailedShot('%s is too long' % word)
            elif len(word) == len(self.hole):
                #
                # Hit the hole
                self.scores.append(self.shots)
                self.current_hole += 1
                over = self.shots-self.par
                self.used.add(word)
                self.tryHole()
                return 'Sunk that shot', over, penalty_time, penalty_shot
            elif len(word) >= len(self.hole):
                #
                # Was too long
                raise FailedShot('%s is too long' % word)
            else:
                #
                # Good word 
                last = self.hole[len(word)-1]
                if last == '*':
                    penalty_shot = 1
                elif last == '~':
                    penalty_shot = 2
                #
                self.hole = self.hole[len(word):]
                self.used.add(word)
                self.distance = len(self.hole)
                return 'Nice shot', self.shots-self.par, penalty_time, penalty_shot
        elif not self.solver.dictionary.contains_word(word.lower()):
            #
            # Not a word
            raise FailedShot('%s is not a word' % word)
        elif len(word) < self.min_length:
            #
            # Too short
            raise FailedShot('%s is too short' % word)
        else:
            #
            # Not on the board - should not be able to get here
            raise FailedShot('%s is not valid' % word)
        
    def suggestWord(self):
        """Return a suggestion for a word"""
        words = set(self.good_words)
        done = set([w.lower() for w in self.used])
        trial = list(words - done)
        trial.sort(cmp=lambda x, y: cmp(len(x), len(y)))
        return trial[0]
            
    def endGame(self):
        """End the game"""
        score = sum(self.scores)
        par = sum([p for _, p, _ in self.holes[:self.max_holes]])
        diff = abs(score - par)
        if score < par:
            print 'You scored %d, %d under par' % (score, diff)
        elif score > par:
            print 'You scored %d, %d over par' % (score, diff)
        else:
            print 'You scored %d, exactly on par' % score
        #
        print
        for score, (n, p, _) in zip(self.scores, self.holes):
            print '%d - %d (%d)' % (n, score, p)

    def isEnded(self):
        """Return True when the game is ended"""
        return self.current_hole > self.max_holes

    def getResults(self):
        """Return the results"""
        diff = self.getScore()
        results = []
        #
        for score, (n, p, _) in zip(self.scores, self.holes):
            results.append('%d - %s (%d)' % (n, self.result_types.get(score-p, 'Lots!'), score))
        return results

    def getScore(self):
        """Return the score for the game"""
        score = sum(self.scores)
        par = sum([p for _, p, _ in self.holes[:self.max_holes]])
        diff = score - par
        return diff    
    
    def getScoreText(self):
        """Return the score as text"""
        diff = self.getScore()
        if diff == 0:
            return 'even par'
        else:
            return '%d %s par' % (abs(diff), 'over' if diff > 0 else 'under')
                        
if __name__ == '__main__':
    g = Game(holes, int(sys.argv[1]), 3)
    g.startGame()
    while not g.isEnded():
        g.playHole()
            
