"""Our main visual theme"""

import serge.blocks.themes

theme = serge.blocks.themes.Manager()
theme.load({
    'main' : ('', {
    
        # Text sizes
        'normal-text-size' : 12,
        'small-text-size' : 8,
        'large-text-size' : 20,
        
        # Text colours
        'text-button-colour' : (17, 19, 56, 255),
        
        # Hole buttons
        'hole-button-height' : 30,
        'hole-button-width' : 120,
        'hole-button-font-size' : 12,
        
        # Game buttons
        'game-button-height' : 120,
        'game-button-width' : 110,
        
        # Score display
        'score-grid-width' : 150,
        'score-grid-height' : 300,
        'score-grid-offset-x' : 85,
        'score-grid-offset-y' : 50,
        
        # Key buttons
        'key-colour' : (17, 19, 56, 255),
        'key-text-size' : 18,
        'key-offset-x' : 320, 
        'key-offset-y' : 20,
        'key-width' : 50,
        'key-height': 50,
        
        # Main ui
        'ui-height' : 180,
        'ui-offset-x' : 25,
        'ui-offset-y' : 25,
        
        # Result
        'result-text-colour' : (229, 237, 0, 255),
        'result-offset-x' : 300,
        'result-offset-y' : 350,
        
        # Hole display
        'hole-offset-x' : 20,
        'hole-offset-y' : 400,
        'hole-width' : 600,
        'hole-height' : 50,
        'hole-text-size' : 22,
        
        # Final display
        'final-offset-x' : 150,
        'final-offset-y' : 80,
        'congrats-offset-y' : 25,
        'final-text-colour' : (229, 237, 0, 255),
        'congrats-text-colour' : (255, 255, 255, 255),
        'final-text-size' : 20,
        'final-line-offset' : 25,
        
        # The escape page
        'escape-offset-x' : 320,
        'escape-offset-y': 450,
        
    }),
    
    '__default__' : 'main',

})

get = theme.getProperty
