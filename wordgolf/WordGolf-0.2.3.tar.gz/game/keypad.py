"""Represents the set of letters displayed"""

import pygame
import time
import os

import serge.visual
import serge.actor
import serge.common 
import serge.sound
import serge.blocks.effects
import serge.blocks.layout
import game 
import gameover
import common
from theme import get as G



class KeyPad(serge.actor.Actor, common.MoveableBackground):
    """Represents the keypad of letters"""
    
    can_suggest = False
    
    def __init__(self, world, game):
        """Intialise the pad"""
        super(KeyPad, self).__init__('keypad', 'keypad')
        self.game = game
        self.world = world
        self.keyboard = serge.engine.CurrentEngine().getKeyboard()
        self.mouse = serge.engine.CurrentEngine().getMouse()
        #
        number_of_keys = len(self.game.board.board)
        self.key_grid = serge.blocks.layout.Grid('grid', 
                size=(number_of_keys, number_of_keys), width=number_of_keys*G('key-width'), height=number_of_keys*G('key-height'))
        self.key_grid.setLayerName('keys')
        self.key_grid.setOrigin(G('key-offset-x'), G('key-offset-y'))
        world.addActor(self.key_grid)
        #
        for x, row in enumerate(self.game.board.board):
            for y, letter in enumerate(row):
                k = serge.actor.Actor('letter')
                k.visual = serge.blocks.visualblocks.TextToggle(letter.upper(), G('key-colour'), 'letter', font_size=G('key-text-size'))
                k.resizeTo(G('key-width'), G('key-height'))
                k.linkEvent('left-click', self.handleClicks, (k, (x, y)))
                self.key_grid.addActor((x, y), k)
        self.clicked = []
        #
        # The button for going
        self.go = serge.actor.Actor('button')
        self.go.setSpatial(G('key-offset-x'), G('key-offset-y') + 
                (len(self.game.board.board))*G('key-height'), len(self.game.board.board)*G('key-width'), G('key-height'))
        self.go.visual = serge.blocks.visualblocks.SpriteText('Go', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        self.go.linkEvent('left-click', self.handleGo)
        self.go.setLayerName('keys')
        world.addActor(self.go)
        #
        # The score UI
        self.ui = serge.blocks.layout.VerticalBar('ui-grid', width=G('key-width'), height=G('ui-height'))
        self.ui.setOrigin(G('ui-offset-x'), G('ui-offset-y'))
        self.ui.setLayerName('ui')
        self.ui_parts = {}
        for name in ('score', 'hole', 'par', 'shots', 'distance', 'time'):
            t = serge.actor.Actor('text', name)
            t.visual = serge.visual.Text(name, G('text-button-colour'), font_size=G('large-text-size'), justify='left')
            self.ui.addActor(t)
            self.ui_parts[name] = t
        world.addActor(self.ui)
        #
        self.result = serge.actor.Actor('keypad')
        self.result.visual = serge.visual.Text('', G('result-text-colour'), font_size=G('large-text-size'))
        self.result.setSpatial(G('result-offset-x'), G('result-offset-y'), 0, 0)
        self.result.setLayerName('ui')
        world.addActor(self.result)
        #
        # The fading effect for text
        self.effect = serge.blocks.effects.AttributeFade(self.result.visual, 'alpha', 1.0, 0.0, 5, persistent=True)
        self.effect.pause()
        self.world.addActor(self.effect)
        #
        self.course = serge.actor.Actor('course')
        self.course.setSpriteName('course')
        self.course.moveTo(320, 240)
        self.course.setLayerName('course')
        world.addActor(self.course)
        #
        self.hole_display = serge.blocks.layout.Grid('hole-display', 'hole-display',
                size=(16, 1), width=G('hole-width'), height=G('hole-height'))
        self.hole_display.setLayerName('keys')
        self.hole_display.setOrigin(G('hole-offset-x'), G('hole-offset-y'))
        world.addActor(self.hole_display)
        #
        self.setText('Let\'s play')
        #
        self.clock = 0.0
        self.this_score = None

    def updateHoleDisplay(self):
        """Update the display of the hole"""
        #
        # Clear all old display
        self.hole_display.clearGrid()
        #
        # Put the hole there
        for i, char in enumerate(self.game.hole + '++'):
            a = serge.actor.Actor('hole-square', 'square-%d' % i)
            image = {'.':'grass', '@':'hole', '*':'sand', '~':'water', '+':'hole'}[char]
            a.visual = serge.blocks.visualblocks.SpriteText('', G('text-button-colour'), image, font_size=G('hole-text-size'))
            a.visual.setAlpha(0.75)
            if char == '+':
                a.visual.setAlpha(0.1)
            self.hole_display.addActor((i, 0), a)
        #
        self.at_character = 0

    def showGreen(self):
        """Show that the green is on"""
        #
        # Make new hole visible
        self.hole_display.getActorAt((self.at_character+2, 0)).visual.setAlpha(0.85)
        #
        # Dim out the old hole
        self.hole_display.getActorAt((self.at_character+self.game.distance-1, 0)).visual.setAlpha(0.1)
        
    def showLetter(self, char):
        """Update the word display"""
        letter = self.hole_display.getActorAt((self.at_character, 0))
        letter.setText(char.upper())
        self.at_character += 1
    
    def clearLetter(self):
        """Clear a letter from the word display"""
        self.at_character -= 1
        self.hole_display.getActorAt((self.at_character, 0)).setText('')

    def clearWord(self, word):
        """Clear a whole word"""
        for char in word:
            self.clearLetter()

    def highlightWord(self, word):
        """Highligh the word"""
        ###############
        # Currently this is too slow
        return
        ###############
        for i in range(len(word)):
            letter = self.hole_display.getActorAt((self.at_character-i-1, 0))
            effect = serge.blocks.effects.AttributeFade(letter.visual, 'alpha', 1.0, 0.25, 5, persistent=False)
            self.world.addActor(effect)
                   
    def handleClicks(self, obj, (key, pos)):
        """Handle a click from a key"""
        #
        # Clicked on an already clicked letter?
        if key.visual.isOn(): 
            if key == self.clicked[-1]:
                # Deselect the last one
                key.visual.setOff()
                self.clicked = self.clicked[:-1]
                self.clearLetter()
                serge.sound.Register.playSound('unletter')
            else:
                # Invalid deselection
                self.log.debug('Cannot deselect this one - not last letter')
                serge.sound.Register.playSound('bad-letter')
        elif len(self.clicked) == self.game.distance+2:
            self.log.debug('Reached end of characters')
            serge.sound.Register.playSound('bad-letter')
        else:
            if self.clicked:
                # Clicking on a new letter - make sure if is valid
                last_x, last_y = self.key_grid.findActorLocation(self.clicked[-1])
                x, y = pos
                dx = abs(last_x-x)
                dy = abs(last_y-y)
                if dx>1 or dy>1:
                    self.log.debug('Invalid letter clicked on')
                    serge.sound.Register.playSound('bad-letter')
                    return
            #
            # Ok, a good letter was clicked                
            key.visual.setOn()
            self.showLetter(key.visual.text)
            self.clicked.append(key)
            serge.sound.Register.playSound('letter')


    def handleGo(self, obj, arg, debug_word=None):
        """Handle the user clicking on Go"""
        if len(self.clicked) >= self.game.min_length or debug_word:
            word = debug_word if debug_word else ''.join([key.visual.text for key in self.clicked])
            self.log.info('Your word is "%s"' % word)
            try:
                result, over_score, penalty_time, penalty_shot = self.game.tryWord(word)
            except game.FailedShot, err:
                self.log.error('A failed shot: %s' % err)
                self.setText(str(err))
                self.clearWord(word)
                serge.sound.Register.playSound('error')
            else:
                self.log.info('Shot resulted in: %s, %d' % (result, over_score))
                self.log.info('Penalties are %d, %d' % (penalty_time, penalty_shot))
                #
                if penalty_shot == 1:
                    result = result + '. You hit a bunker (+1 shot)' 
                    self.game.shots += penalty_shot
                    serge.sound.Register.playSound('sand')
                elif penalty_shot == 2:
                    result = result + '. You went into water (+2 shots)'
                    self.game.shots += penalty_shot
                    serge.sound.Register.playSound('water')
                elif not self.game.isEnded():
                    serge.sound.Register.playSound('word')

                #
                self.setText(result)
                #
                if self.game.isEnded():
                    serge.sound.Register.playSound('end-game')
                    self.endGame()
                elif self.game.shots == 0:
                    # New hole
                    if over_score > 0:
                        serge.sound.Register.playSound('poor-hole')
                    elif over_score < 0:
                        serge.sound.Register.playSound('good-hole')
                    else:
                        serge.sound.Register.playSound('hole')
                    #
                    # Show the new hole
                    self.updateHoleDisplay()
                else:
                    # New word
                    self.highlightWord(word)
                    if self.game.distance < self.game.min_length:
                        self.showGreen()
            #
            self.clearKeys()
        else:
            self.log.debug('Word is not long enough')
            serge.sound.Register.playSound('error')

    def setText(self, text):
        """Set the result text"""
        self.result.setText(text)
        self.effect.unpause()
        self.effect.restart()

    def endGame(self):
        """End the game"""
        self.effect.finish()
        self.log.info('Ending the game now (%s)' % (self.game.scores,))
        #
        # Update high scores
        self.this_score = self.score.table.addScore('%s - %d holes - shots' % 
            (self.gamestart.selected_game_name, self.gamestart.selected_holes),
             os.getenv('USERNAME'), self.game.getScore(), self.clock, time.time())
        self.log.info('Result of adding score is "%s"' % self.this_score)
        self.score.table.addScore('%s - %d holes - time' % (self.gamestart.selected_game_name, self.gamestart.selected_holes),
            os.getenv('USERNAME'), self.game.getScore(), self.clock, time.time())
        self.score.saveTable()
        self.score.updateTable()
        #
        self.world.getEngine().setCurrentWorldByName('end')

    def restartGame(self, holes, game):
        """Restart the game"""
        self.game = self.game.newGame(game)
        self.game.max_holes = holes
        self.game.tryHole()
        self.clock = 0.0
        for x, row in enumerate(self.game.board.board):
            for y, letter in enumerate(row):
                k = self.key_grid.getActorAt((x,y))
                k.visual.setText(letter.upper())
                k.visual.setOff()
        #
        self.updateHoleDisplay()
                
    def clearKeys(self):
        """Clear all the keys"""
        for key in self.clicked:
            key.visual.setOff()
        self.clicked =[]

    def updateActor(self, interval, world):
        """Update the current game state"""
        #
        # Debug suggestion
        if self.mouse.isClicked(serge.input.M_RIGHT) and self.can_suggest:
            suggestion = self.game.suggestWord()
            self.log.debug('Getting suggestion: %s' % suggestion)
            for l in suggestion:
                self.showLetter(l)
            self.handleGo(None, None, suggestion)
            
        #
        # Watch for keys
        if self.keyboard.isDown(pygame.K_ESCAPE):
            self.log.debug('User pressed escape')
            self.world.getEngine().setCurrentWorldByName('escape')
            return

        if self.game.distance < self.game.min_length:
            distance = 'Putting. %d letters' % self.game.min_length
        else:
            distance = self.game.distance
        #
        # Update the score
        self.ui_parts['score'].setText('Score: %s' % self.game.score)
        self.ui_parts['hole'].setText('Hole: %d of %d' % (self.game.num, self.game.max_holes))
        self.ui_parts['shots'].setText('Shots: %s' % self.game.shots)
        self.ui_parts['par'].setText('Par: %s' % self.game.par)
        self.ui_parts['distance'].setText('Dist: %s' % distance)
        self.ui_parts['time'].setText('Time: %s' % self.niceTime(self.clock))
        #
        self.clock += interval/1000.0

        

