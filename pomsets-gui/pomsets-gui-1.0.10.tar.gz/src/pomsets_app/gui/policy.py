import math
import os
import subprocess
import tempfile

import pomsets.resource as ResourceModule

class Policy(ResourceModule.Struct):

    ATTRIBUTES = ['contextManager']

    def __init__(self):
        ResourceModule.Struct.__init__(self)
        return

    # END clas Policy
    pass


class NodePolicy(Policy):

    ATTRIBUTES = Policy.ATTRIBUTES + [
        'portPolicy',
        'visualPolicy'
        ]

    WIDTH = 100
    HEIGHT = 50

    KEY_BORDER_SELECTION_TRUE = "selected border"
    KEY_BORDER_SELECTION_FALSE = "not selected border"
    KEY_BACKGROUND_SELECTION_TRUE = "selected background"
    KEY_BACKGROUND_SELECTION_FALSE = "not selected background"
    KEY_TEXT_SELECTION_TRUE = "selected text"
    KEY_TEXT_SELECTION_FALSE = "not selected text"

    def __init__(self):
        Policy.__init__(self)
        self._colors = {}
        return

    def color(self, key, value=None):
        if value is not None:
            self._colors[key] = value
        return self._colors[key]

    def getPositionForNameLabel(self):
        return [0, 15, 0]

    def getPositionForExecuteStatusLabel(self):
        return [0, -7, 0]

    def setupDimensions(self, node):
        node.width= NodePolicy.WIDTH
        node.height= NodePolicy.HEIGHT
        return

    def setPortPosition(self, node, port):

        # TODO:
        # some of the values in this function
        # are calculated multiple times
        # because this function is called once per port
        # but some of the values, 
        # e.g. minimumPortAreaWidth
        # is constant

        import pomsets_app.gui.graph as GraphModule

        portDirection = port.direction

        yOffset = 0
        if (portDirection == GraphModule.Port.PORT_DIRECTION_INPUT):
            yOffset = node.height + 5
        elif (portDirection == GraphModule.Port.PORT_DIRECTION_OUTPUT):
            yOffset = -1*(port.height+5)

        port.y = yOffset

        minimumPortMargin = 5
        portCount = port.positionCount()
        minimumPortAreaWidth = \
            port.width * portCount + minimumPortMargin * (portCount-1)

        portIndex = port.positionIndex()

        xOffset = 0
        if minimumPortAreaWidth > node.width:
            # Ports have to extend beyond the limit of the node
            # because of size constraint
            startLocation = (node.width-minimumPortAreaWidth)/2
            xOffset = startLocation + portIndex*(portWidth + minimumPortMargin) - portWidth/2
        else:
            xOffset = node.width/portCount * (portIndex+0.5) - port.width/2
        port.x = xOffset


        return 


    # END class NodePolicy
    pass


class VisualPolicy(Policy):

    ATTRIBUTES = Policy.ATTRIBUTES + []
    
    KEY_SELECTION_TRUE = "selected"
    KEY_SELECTION_FALSE = "not selected"

    COLOR_DEFAULT = [1.0, 1.0, 1.0, 1.0]

    FONT_DEFAULT = "FreeUniversal-Regular"
    FONT_DEFAULT_FILE = "%s.ttf" % FONT_DEFAULT

    KEY_FONT_DEFAULT = "default font"    

    def __init__(self):
        Policy.__init__(self)
        self._backgroundMap = {}
        self._textMap = {}
        self._colorMap = {}
        self._fontMap = {}
        return

    def getFontPath(self):
        return os.sep.join([self.contextManager().resourcePath(),
                            'fonts'])

    def color(self, key, value=None):
        if value is not None:
            self._colorMap[key] = value
        if not key in self._colorMap:
            self._colorMap[key] = copy.copy(VisualPolicy.COLOR_DEFAULT)
        return self._colorMap[key]


    def getPathForDefaultFont(self):
        fontPath = os.sep.join([self.getFontPath(),
                                VisualPolicy.FONT_DEFAULT_FILE])
        return fontPath
    
    # END class VisualPolicy
    pass



class EdgePolicy(Policy):


    KEY_SELECTION_TRUE = 'selected'
    KEY_SELECTION_FALSE = 'not selected'
    KEY_DYNAMIC = 'dynamic'

    ATTRIBUTES = Policy.ATTRIBUTES + [
        'visualPolicy',
        'lineColor'
        ]

    def __init__(self):
        Policy.__init__(self)
        return

    def updateEdge(self, edge):

        inputPort = edge.inputPort()
        inputPort.edge = edge
        inputPort.updateColors()

        outputPort = edge.outputPort()
        outputPort.edge = edge
        outputPort.updateColors()

        pass


    def createPath(self, inputPoint, outputPoint, steps=30):

        points = []
        delta = (outputPoint[0]-inputPoint[0], outputPoint[1]-inputPoint[1])
        
        for i in xrange(steps+1):
            theta = float(i)/steps
            x = inputPoint[0] + delta[0] * (1-math.cos(theta*math.pi))/2
            y = inputPoint[1] + delta[1] * theta
            z = math.sin(theta*math.pi)*-1.0
            points.append( (x,y,z) )
        return points

    # END class EdgePolicy
    pass


class BasicLayoutPolicy(Policy):

    ATTRIBUTES = Policy.ATTRIBUTES + []

    OFFSET_X = 100
    OFFSET_Y = 100

    def __init__(self):
        Policy.__init__(self)
        return

    def layoutNodes(self, nodes, edges):

        # sort the nodes
        predecessorMap = {}
        successorMap = {}
        for edge in edges:
            sourceNode = edge.sourceNode()
            targetNode = edge.targetNode()
            if not targetNode in predecessorMap:
                predecessorMap[targetNode] = []
                pass
            predecessorMap[targetNode].append(sourceNode)
            if not sourceNode in successorMap:
                successorMap[sourceNode] = []
            successorMap[sourceNode].append(targetNode)
            pass

        minimalNodes = set(nodes).difference(
            set(reduce(list.__add__, successorMap.values(), [])))
        nodeToLevelMap = dict([(x,0) for x in minimalNodes])

        processedNodes = set(minimalNodes)
        nodesToProcess = reduce(
            list.__add__,
            [successorMap[x] for x in minimalNodes if x in successorMap], [])
        while len(nodesToProcess):
            nodeToProcess = nodesToProcess.pop(0)
            processedNodes.add(nodeToProcess)

            # add the node's successors to nodesToProces
            nodesToProcess.extend(successorMap.get(nodeToProcess, []))

            nodePredecessors = predecessorMap.get(nodeToProcess, [])
            unprocessedPredecessors = set(nodePredecessors).difference(processedNodes)
            if len(unprocessedPredecessors) is not 0:
                # we have not processed all its predecessors,
                # so we don't do anything
                continue
            nodeToLevelMap[nodeToProcess] = max(
                [nodeToLevelMap[x] for x in nodePredecessors]) + 1
            pass
        
        # place the nodes into the different levels
        levelToNodeMap = {}
        for node, level in nodeToLevelMap.iteritems():
            if not level in levelToNodeMap:
                levelToNodeMap[level] = []
            levelToNodeMap[level].append(node)

        # now set the position accordingly
        numLevels = len(levelToNodeMap)

        offsetX = NodePolicy.WIDTH + 50
        offsetY = NodePolicy.HEIGHT + 50

        height = offsetY * numLevels
        width =  offsetX * max([len(x) for x in levelToNodeMap.values()])
        for level, nodesInLevel in levelToNodeMap.iteritems():
            y = offsetY * (numLevels - level - 1) + BasicLayoutPolicy.OFFSET_Y 
            for index, nodeInLevel in enumerate(nodesInLevel):
                x = offsetX * index + BasicLayoutPolicy.OFFSET_X
                nodeInLevel.setPosition(x, y)
            pass

        return (width, height)


    # END class LayoutPolicy
    pass


class GraphvizLayoutPolicy(Policy):
    
    ATTRIBUTES = Policy.ATTRIBUTES + []

    def __init__(self):
        Policy.__init__(self)
        return

    def temporaryFilePath(self, value=None):
        if value is not None:
            self._tmpFile = None
            
        if not hasattr(self, '_tmpFile'):
            self._tmpFile = os.sep.join(
                [tempfile.gettempdir(), 'temp_dotFile.dot'])
            
        return self._tmpFile



    def generateDotFile(self, path, nodes, edges):

        import gv
        
        nodeMap = {}

        gvGraph = gv.digraph('name')
        for node in nodes:
            gvNode = gv.node(gvGraph, node.nodeData.name())
            nodeMap[node] = gvNode
            gv.setv(gvNode, 'pos', str(node.getPosition()))

        for edge in edges:
            gvEdge = gv.edge(gvGraph, 
                             edge.sourceNode().nodeData.name(),
                             edge.targetNode().nodeData.name())

        gv.write(gvGraph, path)
        return



    def layoutNodes(self, nodes, edges):

        tmpFile = self.temporaryFilePath()
        self.generateDotFile(tmpFile, nodes, edges)

        # use the subprocess module to execute
        layoutFile = '/tmp/pomset.layout'
        command = [self.contextManager().commandPath('dot'),
                   tmpFile, '-o%s' % layoutFile]

        try:
            ret = subprocess.call(command)
        except OSError:
            pass

        boundingbox = ""

        with open(layoutFile, 'r') as f:
            for line in f.readlines():
                logging.debug(line)

                match = re.search('^\s*graph \[(.*)\];$', line)
                if match is not None:
                    attributeString = match.group(1)
                    logging.debug("Graph has attributes: %s" % match.group(1))
                    attributes = self.getAttributesDict(attributeString)
                    if attributes.has_key('bb'):
                        bb = map(float, attributes['bb'].split(','))
                    continue;

                foundNode = False
                for node in nodes:
                    nodeName = "%s" % (node.nodeData.name())
                    match = re.search('^\s*"{0,1}'+nodeName+'"{0,1}\s*\[(.*)\];$', line)
                    if match is not None:
                        attributeString = match.group(1)
                        attributes = self.getAttributesDict(attributeString)
                        if attributes.has_key('pos'):

                            position = 1.5 * numpy.matrix(
                                ' '.join(attributes['pos'].split(',')))
                            logging.debug('position >> %s' % position)
                            node.setPosition(position[0,0], position[0,1])
                            pass
                        if attributes.has_key('width'):
                            (node.width) = float(attributes['width']) * 80
                        if attributes.has_key('height'):
                            (node.height) = float(attributes['height']) * 80
                        foundNode = True;
                    if foundNode:
                        break

        return (bb[2],bb[3])

    
    def getAttributesDict(self, attributeString):
        dict = {}
        matches = re.findall('(\w+)="(.*?)"',attributeString)
        if matches is not None:
            for match in matches:
                attributeName = match[0]
                attributeValue = match[1]
                dict[attributeName] = attributeValue
        return dict



    # END class GraphvizLayoutPolicy
    pass



class PortPolicy(object):


    # TODO:
    # the following should be configurable
    # port size, currently (8,8)
    # min port margin, currently 5
    # port spacing, currently dynamically spaced out

    def __init__(self, contextManager):
        self.contextManager(contextManager)
        return

    def contextManager(self, value=None):
        if value is not None:
            self._manager = value
        return self._manager


    def setupDimensions(self, port):
        port.width = 8
        port.height = 8
        return



    # END class PortPolicy
    pass

