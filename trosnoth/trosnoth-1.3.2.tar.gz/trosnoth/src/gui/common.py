# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import pygame

defaultAnchor = 'topleft'

def uniqueColour(colours):
    '''Returns a greyish colour that is not in the given list of colour
    triples. Useful for colourkeying.'''
    result = [0, 0, 0]
    i = 0
    while True:
        result[i] += 1
        rTuple = tuple(result)
        for colour in colours:
            if colour == rTuple:
                break
        else:
            return rTuple
        i = (i + 1) % 3

def addPositions(p1, p2):
    return tuple([p1[i] + p2[i] for i in 0,1])

def _getScaledSize(app, size):
    return app.screenManager.scale(size)

class ScaledPoint(object):
    def __init__(self, x, y):
        self.val = (x, y)
    def getPoint(self, app):
        return app.screenManager.placePoint(self.val)
    def __repr__(self):
        return "Scaled Point (%d, %d)" % self.val

def canvasIntervalToScreen(app, val):
    return max(1, app.screenManager.scaleFactor * val)

class ScaledScalar(object):
    def __init__(self, val):
        self.val = val
        self._val = None
        self._scaleFactor = None
        
    def getVal(self, app):
        sf = app.screenManager.scaleFactor
        if self._scaleFactor != sf:
            self._val = canvasIntervalToScreen(app, self.val)
            self._scaleFactor = sf
        return self._val

    def __repr__(self):
        return "ScaledScalar (%d)" % (self.val,)

class FullScreenAttachedPoint(object):
    def __init__(self, distance, attachedAt = 'topleft'):
        self.val = distance
        self.attachedAt = attachedAt

    def getPoint(self, app):
        if hasattr(self.val, 'getSize'):
            val = self.val.getSize(app)
        else:
            val = self.val
        pos = getattr(app.screenManager.rect, self.attachedAt)
        return addPositions(pos, val)

class ScaledScreenAttachedPoint(object):
    def __init__(self, distance, attachedAt = 'topleft'):
        self.val = distance
        self.attachedAt = attachedAt

    def getPoint(self, app):
        if hasattr(self.val, 'getSize'):
            val = self.val.getSize(app)
        else:
            val = self.val
        pos = getattr(app.screenManager.scaledRect, self.attachedAt)
        return addPositions(pos, val)    

# @param attachedTo_Rect should be a reference to a function which
# returns a pygame.Rect
class AttachedPoint(object):
    def __init__(self, val, attachedTo_Rect, attachedAt = 'topleft'):
        self.val = val
        self.attachedAt = attachedAt
        self.attachedTo_Rect = attachedTo_Rect

    def getPoint(self, app):
        pos = getattr(self.attachedTo_Rect(), self.attachedAt)
        if hasattr(self.val, 'getSize'):
            val = self.val.getSize(app)
        else:
            val = self.val

        return addPositions(pos, val)

class ScaledSize(object):
    def __init__(self, x, y):
        self.val = (x, y)
    def getSize(self, app):
        return _getScaledSize(app, self.val)
    def __repr__(self):
        return "Scaled Size (%d, %d)" % self.val

class Size(object):
    def __init__(self, x, y):
        self.val = (x, y)
    def getSize(self, app):
        return self.val
    def __repr__(self):
        return "Size (%d, %d)" % self.val

class FullScreenSize(object):
    def getSize(self, app):
        return app.screenManager.size
    def __repr__(self):
        return "Full Screen Size"

class ScaledScreenSize(object):
    def getSize(self, app):
        return app.screenManager.scaledSize
    def __repr__(self):
        return "Scaled Screen Size"

# An image loaded from file
class NewImage(object):
    def __init__(self, nameOrImage, colourkey=True):
        if isinstance(nameOrImage, str):
            self.name = nameOrImage
            self.image = None
        else:
            assert isinstance(nameOrImage, pygame.Surface)
            self.image = nameOrImage
        self.colourkey = colourkey
    def getImage(self, app):
        if self.image is not None:
            return self.image
        self.image = pygame.image.load(self.name).convert()
        if self.colourkey:
            self.image.set_colorkey(self.image.get_at((0,0)))
        return self.image

    def getSize(self, app):
        return self.getImage(app).get_size()


class SizedImage(NewImage):
    def __init__(self, nameOrImage, size, colourkey=True):
        super(SizedImage, self).__init__(nameOrImage, colourkey)
        self.sizedImage = None
        # Keep a record of whether the size of the screen changes
        self.lastSize = None
        self.size = size

    def getImage(self, app):
        if self.sizedImage is not None and self.lastSize == self._getCurrentSize(app):
            return self.sizedImage
        img = super(SizedImage, self).getImage(app)
        self.lastSize = self._getCurrentSize(app)
        self.sizedImage = pygame.transform.scale(img, self.lastSize)
        return self.sizedImage

    def _getCurrentSize(self, app):
        if hasattr(self.size, 'getSize'):
            return self.size.getSize(app)
        else:
            return self.size


class TextImage(NewImage):
    '''Shows text at a specified screen location.'''
    
    def __init__(self, text, font, colour=(0,128,0), bgColour=None, antialias=True):
        self.colour = colour
        self.bgColour = bgColour
        self._text = str(text)
        self.font = font
        self.antialias = antialias

    def setText(self, text):
        self._text = str(text)
    def getText(self):
        return self._text
    text = property(getText, setText)

    def getImage(self, app):
        return self.font.render(app, self._text, self.antialias, self.colour, self.bgColour)
 

class Location(object):
    '''
    @param  point   the point that this location is attached to
    @param  anchor  a string representing the rectangle attribute which this
                    location will reposition
    '''
    def __init__(self, point, anchor=defaultAnchor):            
        if anchor == 'centre':
            anchor = 'center'
        self.point = point
        self.anchor = anchor

    def __repr__(self):
        return "Location: %s anchored at %s" % (repr(self.point), self.anchor)
    def apply(self, app, rect):
        '''Moves the rect so that it is anchored according to this anchor.'''
        point = self.point
        if hasattr(point, 'getPoint'):
            point = point.getPoint(app)
        setattr(rect, self.anchor, point)

# Location relative to another location
# @param size Can be a tuple or a ScaledPoint
class RelativeLocation(Location):
    def __init__(self, location, size):
        self.size = size
        self.location = location

    def __repr__(self):
        return 'RelativeLocation: (%s plus %s)' % (repr(self.location), repr(self.size))
        
    def apply(self, app, rect):
        self.location.apply(app, rect)
        if hasattr(self.size, 'getSize'):
            diff = self.size.getSize(app)
        else:
            diff = self.size
        rect.topleft = addPositions(diff, rect.topleft)

class Area(Location):
    '''
    @param  point   the point that this area is attached to
    @param  size    the size of this area
    @param  anchor  a string representing which of the rectangle's attributes
                    the point will be attached to
    '''
    def __init__(self, point, size, anchor=defaultAnchor):
        Location.__init__(self, point, anchor)
        self.size = size

    def apply(self, app, rect):
        '''Moves and resizes this rect so that it covers this area.'''
        if hasattr(self.size, 'getSize'):
            rect.size = self.size.getSize(app)
        else:
            rect.size = self.size
        Location.apply(self, app, rect)

    def getRect(self, app):
        result = pygame.Rect(0,0,0,0)
        self.apply(app, result)
        return result

    def __repr__(self):
        return "Area: point is %s, size is %s, anchored at %s" % (repr(self.point), repr(self.size), self.anchor)


class PygameEvent(object):
    def __init__(self, **kwargs):
        self._repr = 'PygameEvent(%s)' % (', '.join('%s=%s' % a for a in
                kwargs.iteritems()))
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

    def __repr__(self):
        return self._repr

def translateEvent(event, amount):
    result = PygameEvent(type=event.type, pos=(event.pos[0] - amount[0],
                                         event.pos[1] - amount[1]))
    for name in ['button', 'buttons']:
        try:
            v = getattr(event, name)
        except AttributeError:
            pass
        else:
            setattr(result, name, v)
    return result

# For ease of use    
def ScaledLocation(x, y, anchor = defaultAnchor):
    return Location(ScaledPoint(x, y), anchor)

def ScaledArea(x, y, width, height, anchor = defaultAnchor):
    return Area(ScaledPoint(x, y), ScaledSize(width, height), anchor)


class Region(object):
    '''
    Defines a region using any of various anchors. The values passed in should
    be one of:
        * Abs(a, b) - absolute coordinates.
        * Canvas(a, b) - takes (a, b) on a 1024x768 surface and maps to the
            screen.
        * Screen(a, b) - takes floats a and b in the range of 0..1 and scales
            them to the screen size.
    '''
    STANDARD_ARGS = {
        'topleft':      ('0', '0'),
        'topright':     ('2', '0'),
        'bottomleft':   ('0', '2'),
        'bottomright':  ('2', '2'),
        'size':         ('s', 's'),
        'midtop':       ('1', '0'),
        'midbottom':    ('1', '2'),
        'midleft':      ('0', '1'),
        'midright':     ('2', '1'),
        'centre':       ('1', '1'),
        'center':       ('1', '1'),
        'left':         ('0', '-'),
        'right':        ('2', '-'),
        'x':            ('0', '-'),
        'width':        ('s', '-'),
        'w':            ('s', '-'),
        'centrex':      ('1', '-'),
        'centerx':      ('1', '-'),
        'top':          ('-', '0'),
        'bottom':       ('-', '2'),
        'y':            ('-', '0'),
        'height':       ('-', 's'),
        'h':            ('-', 's'),
        'centrey':      ('-', '1'),
        'centery':      ('-', '1'),
    }

    OTHER_ARGS = frozenset(['aspect'])     # The aspect ratio.

    VALID_ARGS = OTHER_ARGS.union(STANDARD_ARGS.keys())

    def __init__(self, **kwargs):
        self.aspect = None
        self.aspect_dir = None

        self._validateArgNames(kwargs)
        self._setRepr(kwargs)

        aspect = None
        if 'aspect' in kwargs:
            aspect = kwargs.pop('aspect')

        xConstraints = {}
        yConstraints = {}
        constraints_2d = []
        constraints_1d = []
        for arg, val in kwargs.iteritems():
            xKind, yKind = self.STANDARD_ARGS[arg]
            if xKind != '-':
                if xKind in xConstraints:
                    raise TypeError('specifying %s overconstrains region (x)' %
                            (arg,))
                xConstraints[xKind] = arg
            if yKind != '-':
                if yKind in yConstraints:
                    raise TypeError('specifying %s overconstrains region (y)' %
                            (arg,))
                yConstraints[yKind] = arg

            if xKind == '-':
                c = constraints_1d
                if yKind == 's':
                    method = 'getYVal'
                else:
                    method = 'getYPoint'
            elif yKind == '-':
                c = constraints_1d
                if xKind == 's':
                    method = 'getXVal'
                else:
                    method = 'getXPoint'
            else:
                c = constraints_2d
                if xKind == 's' and yKind == 's':
                    method = 'getSize'
                elif xKind != 's' and yKind != 's':
                    method = 'getPoint'
                else:
                    raise AssertionError('definition of %r in '
                        'Region.STANDARD_ARGS does not make sense' % (arg,))

            c.append((arg, val, method))

        self.constraints_2d = constraints_2d
        self.constraints_1d = constraints_1d

        xNum = len(xConstraints)
        yNum = len(yConstraints)
        if xNum > 2:
            raise TypeError('Region is overconstrained horizontally')
        if yNum > 2:
            raise TypeError('Region is overconstrained vertically')
        if aspect is None:
            if xNum < 2:
                raise TypeError('Region is underconstrained horizontally')
            if yNum < 2:
                raise TypeError('Region is underconstrained vertically')
            self.constraints = [self._makeXConstraint(xConstraints),
                    self._makeYConstraint(yConstraints)]
        else:
            if xNum + yNum > 3:
                raise TypeError('Region is overconstrained')
            if xNum + yNum < 3:
                raise TypeError('Region is underconstrained')
            if xNum == 2:
                self.constraints = self._makeYAspectConstraints(xConstraints,
                        yConstraints, aspect)
            else:
                self.constraints = self._makeXAspectConstraints(xConstraints,
                        yConstraints, aspect)

    def __repr__(self):
        return self._repr

    def _setRepr(self, kwargs):
        self._repr = 'Region(%s)' % (', '.join('%s=%r' % t for t in
                kwargs.iteritems()))

    def _validateArgNames(self, kwargs):
        for arg in kwargs:
            if arg not in self.VALID_ARGS:
                raise TypeError('Region() got an unexpected keyword argument '
                        + repr(arg))
                
    def getRect(self, app):
        vals = self._evaluateConstraints(app)
        r = pygame.Rect((0, 0), (0, 0))
        self._applyConstraints(r, vals)
        return r

    def _applyConstraints(self, r, vals):
        for c, args in self.constraints:
            c(r, vals, args)

    def _evaluateConstraints(self, app):
        vals = {}
        for k, v, m in self.constraints_2d:
            vals[k] = getattr(v, m)(app)
        for k, v, m in self.constraints_1d:
            result = getattr(v, m)(app)
            vals[k] = (result, result)
        return vals

    def _standardXConstraint(self, r, vals, args):
        p1, p2 = args
        left, width = self._xInterval(vals[p1][0], vals[p2][0])
        r.width = width
        r.left = left

    def _standardYConstraint(self, r, vals, args):
        p1, p2 = args
        top, height = self._yInterval(vals[p1][1], vals[p2][1])
        r.height = height
        r.top = top

    def _makeXConstraint(self, xConstraints):
        self._xInterval, args = self._getIntervalFunction(xConstraints)
        return self._standardXConstraint, args
        
    def _makeYConstraint(self, yConstraints):
        self._yInterval, args = self._getIntervalFunction(yConstraints)
        return self._standardYConstraint, args

    def _getIntervalFunction(self, constraintsDict):
        if '0' in constraintsDict:
            if 's' in constraintsDict:
                intervalFunc = self._getIntervalFromInterval
                args = constraintsDict['0'], constraintsDict['s']
            elif '2' in constraintsDict:
                intervalFunc = self._getIntervalFromEdges
                args = constraintsDict['0'], constraintsDict['2']
            else:
                intervalFunc = self._getIntervalFromFirstHalf
                args = constraintsDict['0'], constraintsDict['1']
        elif '2' in constraintsDict:
            if 's' in constraintsDict:
                intervalFunc = self._getIntervalFromReverseInterval
                args = constraintsDict['2'], constraintsDict['s']
            else:
                intervalFunc = self._getIntervalFromSecondHalf
                args = constraintsDict['1'], constraintsDict['2']
        else:
            intervalFunc = self._getIntervalFromCentre
            args = constraintsDict['1'], constraintsDict['s']
        return intervalFunc, args

    def _xAspectConstraint(self, r, vals, args):
        aspect, attr, key = args
        r.width = int(r.height * aspect + 0.5)
        setattr(r, attr, vals[key][0])

    def _yAspectConstraint(self, r, vals, args):
        aspect, attr, key = args
        r.height = int(r.width / aspect + 0.5)
        setattr(r, attr, vals[key][1])

    def _makeXAspectConstraints(self, xConstraints, yConstraints, aspect):
        key, val = xConstraints.items().pop()
        if key == '0':
            attr = 'left'
        elif key == '1':
            attr = 'centerx'
        elif key == '2':
            attr = 'right'
        else:
            raise TypeError('Region is overconstrained')
        return [
            self._makeYConstraint(yConstraints),
            (self._xAspectConstraint, (aspect, attr, val))
        ]

    def _makeYAspectConstraints(self, xConstraints, yConstraints, aspect):
        key, val = yConstraints.items().pop()
        if key == '0':
            attr = 'top'
        elif key == '1':
            attr = 'centery'
        elif key == '2':
            attr = 'bottom'
        else:
            raise TypeError('Region is overconstrained')
        return [
            self._makeXConstraint(xConstraints),
            (self._yAspectConstraint, ((aspect+0.), attr, val))
        ]

    def _getIntervalFromEdges(self, x1, x2):
        return (x1, x2 - x1)
    def _getIntervalFromInterval(self, x1, deltaX):
        return (x1, deltaX)
    def _getIntervalFromFirstHalf(self, x1, midx):
        return (x1, 2 * (midx - x1))
    def _getIntervalFromSecondHalf(self, midx, x2):
        deltaX = 2 * (x2 - midx)
        return (x2 - deltaX, deltaX)
    def _getIntervalFromCentre(self, midx, deltaX):
        return midx - int(deltaX / 2), deltaX
    def _getIntervalFromReverseInterval(self, x2, deltaX):
        return (x2 - deltaX, deltaX)

class Abs(object):
    def __init__(self, *args):
        self.values = args
    def __repr__(self):
        return 'Abs(%s)' % ', '.join(repr(v) for v in self.values)

    def getVal(self, app):
        assert len(self.values) == 1
        return self.values[0]
    getXVal = getYVal = getVal
    getXPoint = getYPoint = getVal

    def getPoint(self, app):
        assert len(self.values) == 2
        return self.values
    getSize = getPoint

    def getRect(self, app):
        assert len(self.values) == 4
        return pygame.Rect(*self.values)
        
class Canvas(object):
    def __init__(self, *args):
        self.values = args
    def __repr__(self):
        return 'Canvas(%s)' % ', '.join(repr(v) for v in self.values)

    def getVal(self, app):
        assert len(self.values) == 1
        return canvasIntervalToScreen(app, self.values[0])
    getXVal = getYVal = getVal

    def getXPoint(self, app):
        assert len(self.values) == 1
        sm = app.screenManager
        return int(self.value[0] * sm.scaleFactor + sm.offsets[0])

    def getYPoint(self, app):
        assert len(self.values) == 1
        sm = app.screenManager
        return int(self.value[1] * sm.scaleFactor + sm.offsets[1])

    def getPoint(self, app):
        assert len(self.values) == 2
        return app.screenManager.placePoint(self.values)

    def getSize(self, app):
        assert len(self.values) == 2
        return app.screenManager.scale(self.values)

    def getRect(self, app):
        assert len(self.values) == 4
        x, y = app.screenManager.size
        xr, yr, wr, hr = self.values
        return pygame.Rect(x * xr, y * yr, x * wr, y * hr)

class Screen(object):
    def __init__(self, *args):
        self.values = args
    def __repr__(self):
        return 'Screen(%s)' % ', '.join(repr(v) for v in self.values)

    def getXVal(self, app):
        assert len(self.values) == 1
        return app.screenManager.size[0] * self.values[0]
    getXPoint = getXVal

    def getYVal(self, app):
        assert len(self.values) == 1
        return app.screenManager.size[1] * self.values[1]
    getYPoint = getYVal

    def getPoint(self, app):
        assert len(self.values) == 2
        x, y = app.screenManager.size
        xr, yr = self.values
        return (x * xr, y * yr)
    getSize = getPoint

    def getRect(self, app):
        assert len(self.values) == 4
        x, y = app.screenManager.size
        xr, yr, wr, hr = self.values
        return pygame.Rect(x * xr, y * yr, x * wr, y * hr)
