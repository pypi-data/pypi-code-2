from __future__ import with_statement

import os
import sys
import Image, ImageDraw

"""
img = Image.new("RGBA", (300,300), "#FFFFFF")
draw = ImageDraw.Draw(img)
draw.line((0,10,0,300),fill=(0,0,0),width=10)
"""

KEY_BORDER_SELECTION_TRUE =  [0.3, 0.3, 0.3, 1.0]
KEY_BORDER_SELECTION_FALSE = [0.7, 0.7, 0.7, 1.0]
KEY_BACKGROUND_SELECTION_TRUE = [0.6, 0.6, 0.9, 1.0]
#KEY_BACKGROUND_SELECTION_FALSE = [0.3, 0.3, 0.5, 0.8]
KEY_BACKGROUND_SELECTION_FALSE = [0.6, 0.6, 0.6, 1.0]
KEY_TEXT_SELECTION_TRUE = [1.0, 1.0, 1.0, 1.0]
KEY_TEXT_SELECTION_FALSE = [0.8, 0.8, 0.8, 1.0]

BORDER_WIDTH = 10

DEFAULT_NODE_WIDTH = 300
DEFAULT_NODE_HEIGHT = 200


def saveImage(image, path):
    #with open(path, 'w') as f:
    #    image.save(f, 'PNG')
    image.save(path, 'PNG')
    return

def generateNewImage(size=None, color=None):
    if size is None:
        size = (DEFAULT_NODE_WIDTH,DEFAULT_NODE_HEIGHT)
    if color is None:
        # color = "#FFFFFF"
        color = "#0000FF"

    img = Image.new("RGBA", size, color)
    return img

def getFill(color):
    # return tuple(color[:3])
    fill = "#%s%s%s%s%s%s" % (
        hex(int(color[0]*255)/16)[2],
        hex(int(color[0]*255)%16)[2],
        hex(int(color[1]*255)/16)[2],
        hex(int(color[1]*255)%16)[2],
        hex(int(color[2]*255)/16)[2],
        hex(int(color[2]*255)%16)[2],
        )

    return fill


def generateAtomicNode(backgroundColor, borderColor):

    imageWidth = DEFAULT_NODE_WIDTH
    imageHeight = DEFAULT_NODE_HEIGHT

    img = generateNewImage(size=(imageWidth,imageHeight),
                           color=backgroundColor)
    draw = ImageDraw.Draw(img)

    draw.line((0,BORDER_WIDTH/2,imageWidth,BORDER_WIDTH/2), 
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((0,imageHeight-BORDER_WIDTH/2,imageWidth,imageHeight-BORDER_WIDTH/2), 
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((BORDER_WIDTH/2, 0, BORDER_WIDTH/2, imageHeight), 
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth-BORDER_WIDTH/2, 0, imageWidth-BORDER_WIDTH/2, imageHeight), 
              fill=borderColor,
              width=BORDER_WIDTH)

    return img


def generateNestNode(backgroundColor,borderColor):
    imageWidth = DEFAULT_NODE_WIDTH
    imageHeight = DEFAULT_NODE_HEIGHT

    offsetWidth = int(1.5 * BORDER_WIDTH)
    offsetHeight = int(1.5 * BORDER_WIDTH)

    offsetBorderWidth = 5
    offsetBorderHeight = 5

    img = generateNewImage(size=(imageWidth,imageHeight),
                           color=backgroundColor)
    draw = ImageDraw.Draw(img)

    draw.line((0,offsetBorderHeight,imageWidth,offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth-offsetBorderWidth,0,imageWidth-offsetBorderWidth,
               imageHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth,imageHeight-offsetBorderHeight,
               0,imageHeight-offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((0+offsetBorderWidth,imageHeight, 0+offsetBorderWidth,0),
              fill=borderColor,
              width=BORDER_WIDTH)

    draw.line((offsetWidth,offsetHeight+offsetBorderHeight,imageWidth-offsetWidth,offsetHeight+offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth-offsetWidth-offsetBorderWidth,offsetHeight,
               imageWidth-offsetWidth-offsetBorderWidth,imageHeight-offsetHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth-offsetWidth,imageHeight-offsetHeight-offsetBorderHeight,
               offsetWidth,imageHeight-offsetHeight-offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((offsetWidth+offsetBorderWidth,imageHeight-offsetHeight,
               offsetWidth+offsetBorderWidth,offsetHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    return img

def generateBranchNode():
    return

def generateLoopNode():
    return

def generateParameterSweepNode(backgroundColor, borderColor):

    offsetWidth = int(1.5 * BORDER_WIDTH)
    offsetHeight = int(1.5 * BORDER_WIDTH)

    offsetBorderWidth = -5
    offsetBorderHeight = 5

    imageWidth = DEFAULT_NODE_WIDTH + 3*BORDER_WIDTH
    imageHeight = DEFAULT_NODE_HEIGHT + 3*BORDER_WIDTH
    img = generateNewImage(size=(imageWidth,imageHeight),
                           color=backgroundColor)

    draw = ImageDraw.Draw(img)

    draw.line((offsetWidth,2*offsetHeight+offsetBorderHeight+3,
               offsetWidth,offsetHeight+offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((offsetWidth+offsetBorderWidth,offsetHeight+offsetBorderHeight+2,
               imageWidth-offsetWidth,offsetHeight+offsetBorderHeight+2),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth-offsetWidth+offsetBorderWidth,offsetHeight+offsetBorderHeight,
               imageWidth-offsetWidth+offsetBorderWidth,imageHeight-offsetHeight+offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth-offsetWidth+offsetBorderWidth,imageHeight-offsetHeight,
               imageWidth-2*offsetWidth,imageHeight-offsetHeight),
              fill=borderColor,
              width=BORDER_WIDTH)

    draw.line((offsetWidth*2,offsetHeight+offsetBorderHeight,
               2*offsetWidth,0),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((2*offsetWidth+offsetBorderWidth+1,0+offsetBorderHeight,
               imageWidth,0+offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth+offsetBorderWidth,0+offsetBorderHeight, 
               imageWidth+offsetBorderWidth,imageHeight-2*offsetHeight+offsetBorderHeight),
              fill=borderColor,
              width=BORDER_WIDTH)
    draw.line((imageWidth+offsetBorderWidth,imageHeight-2*offsetHeight,
               imageWidth-offsetWidth,imageHeight-2*offsetHeight),
              fill=borderColor,
              width=BORDER_WIDTH)

    return img


def main(args):

    if len(args) < 2:
        print "need to specify output dir"
        return

    outputDir = args[1]

    for path, background, border in [('node unselected.png',
                                      KEY_BACKGROUND_SELECTION_FALSE,
                                      KEY_BORDER_SELECTION_FALSE),
                                     ('node selected.png',
                                      KEY_BACKGROUND_SELECTION_TRUE,
                                      KEY_BORDER_SELECTION_TRUE)]:
        backgroundColor = getFill(background)
        borderColor = getFill(border)
        img = generateAtomicNode(backgroundColor, borderColor)
        saveImage(img, os.path.join(outputDir, path))
        pass

    for path, background, border in [('nest unselected.png',
                                      KEY_BACKGROUND_SELECTION_FALSE,
                                      KEY_BORDER_SELECTION_FALSE),
                                     ('nest selected.png',
                                      KEY_BACKGROUND_SELECTION_TRUE,
                                      KEY_BORDER_SELECTION_TRUE)]:
        backgroundColor = getFill(background)
        borderColor = getFill(border)
        img = generateNestNode(backgroundColor, borderColor)
        saveImage(img, os.path.join(outputDir, path))
        pass

    generateBranchNode()
    generateLoopNode()


    for path, background, border in [('ps unselected.png',
                                      KEY_BACKGROUND_SELECTION_FALSE,
                                      KEY_BORDER_SELECTION_FALSE),
                                     ('ps selected.png',
                                      KEY_BACKGROUND_SELECTION_TRUE,
                                      KEY_BORDER_SELECTION_TRUE)]:
        backgroundColor = getFill(background)
        borderColor = getFill(border)
        img = generateParameterSweepNode(backgroundColor, borderColor)
        saveImage(img, os.path.join(outputDir, path))
        pass

    return

if __name__=="__main__":
    main(sys.argv)
