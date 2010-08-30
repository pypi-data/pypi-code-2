import os
import unittest

import simplejson as ConfigModule

import pomsets.builder as BuilderModule

import pomsets_app.controller.context as ContextModule

import pomsets_app.gui.graph as GraphModule
import pomsets_app.gui.policy as PolicyModule


class TestBasicLayoutPolicy(unittest.TestCase):

    def setUp(self):
        self.builder = BuilderModule.Builder()
        self.policy = PolicyModule.BasicLayoutPolicy()
        return

    def tearDown(self):
        return

    def testLayout1(self):
        builder = self.builder

        pomsetContext = builder.createNewNestPomset()
        pomset = pomsetContext.pomset()

        definitionContext = builder.createNewAtomicPomset()
        definitionToReference = definitionContext.pomset()

        nodes = []
        nodes.append(builder.createNewNode(
                pomset, name='A', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='B', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='C', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='D', definitionToReference=definitionToReference))

        guiNodeMap = dict([(x, GraphModule.Node(x)) for x in nodes])

        edges = []
        for sourceNode, targetNode in [(nodes[0], nodes[1]),
                                       (nodes[0], nodes[2]),
                                       (nodes[1], nodes[3]),
                                       (nodes[2], nodes[3])]:
            edges.append(
                GraphModule.Edge(
                    builder.connect(
                        pomset,
                        sourceNode, 'temporal output',
                        targetNode, 'temporal input'),
                    [guiNodeMap[sourceNode], None,
                     None, guiNodeMap[targetNode]]
                    )
                )
            pass
        
        self.policy.layoutNodes(guiNodeMap.values(), edges)

        guiNode = guiNodeMap[nodes[0]]
        self.assertEquals((100,300), guiNode.getPosition())

        guiNode = guiNodeMap[nodes[1]]
        self.assertEquals((100,200), guiNode.getPosition())

        guiNode = guiNodeMap[nodes[2]]
        self.assertEquals((250,200), guiNode.getPosition())

        guiNode = guiNodeMap[nodes[3]]
        self.assertEquals((100,100), guiNode.getPosition())

        return


    def testLayout2(self):
        builder = self.builder

        pomsetContext = builder.createNewNestPomset()
        pomset = pomsetContext.pomset()

        definitionContext = builder.createNewAtomicPomset()
        definitionToReference = definitionContext.pomset()

        nodes = []
        nodes.append(builder.createNewNode(
                pomset, name='A', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='B', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='C', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='D', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='D', definitionToReference=definitionToReference))

        guiNodeMap = dict([(x, GraphModule.Node(x)) for x in nodes])

        edges = []
        for sourceNode, targetNode in [(nodes[0], nodes[1]),
                                       (nodes[0], nodes[2]),
                                       (nodes[1], nodes[2]),
                                       (nodes[2], nodes[3]),
                                       (nodes[2], nodes[4])]:
            edges.append(
                GraphModule.Edge(
                    builder.connect(
                        pomset,
                        sourceNode, 'temporal output',
                        targetNode, 'temporal input'),
                    [guiNodeMap[sourceNode], None,
                     None, guiNodeMap[targetNode]]
                    )
                )
            pass
        
        self.policy.layoutNodes(guiNodeMap.values(), edges)

        guiNode = guiNodeMap[nodes[0]]
        self.assertEquals((100,400), guiNode.getPosition())

        guiNode = guiNodeMap[nodes[1]]
        self.assertEquals((100,300), guiNode.getPosition())

        guiNode = guiNodeMap[nodes[2]]
        self.assertEquals((100,200), guiNode.getPosition())

        positions = set([(250,100),(100,100)])

        guiNode = guiNodeMap[nodes[3]]
        positions.remove(guiNode.getPosition())

        guiNode = guiNodeMap[nodes[4]]
        positions.remove(guiNode.getPosition())

        self.assertEquals(0, len(positions))

        return


    def testLayout3(self):
        builder = self.builder

        pomsetContext = builder.createNewNestPomset()
        pomset = pomsetContext.pomset()

        definitionContext = builder.createNewAtomicPomset()
        definitionToReference = definitionContext.pomset()

        nodes = []
        nodes.append(builder.createNewNode(
                pomset, name='A', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='B', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='C', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='D', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='E', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='F', definitionToReference=definitionToReference))

        guiNodeMap = dict([(x, GraphModule.Node(x)) for x in nodes])

        edges = []
        for sourceNode, targetNode in [(nodes[0], nodes[3]),
                                       (nodes[1], nodes[3]),
                                       (nodes[2], nodes[3]),
                                       (nodes[2], nodes[4]),
                                       (nodes[3], nodes[5])]:
            edges.append(
                GraphModule.Edge(
                    builder.connect(
                        pomset,
                        sourceNode, 'temporal output',
                        targetNode, 'temporal input'),
                    [guiNodeMap[sourceNode], None,
                     None, guiNodeMap[targetNode]]
                    )
                )
            pass
        

        self.policy.layoutNodes(guiNodeMap.values(), edges)

        positions = set([(400,300),(250,300),(100,300)])

        guiNode = guiNodeMap[nodes[0]]
        positions.remove(guiNode.getPosition())

        guiNode = guiNodeMap[nodes[1]]
        positions.remove(guiNode.getPosition())

        guiNode = guiNodeMap[nodes[2]]
        positions.remove(guiNode.getPosition())

        self.assertEquals(0, len(positions))


        positions = set([(250,200),(100,200)])

        guiNode = guiNodeMap[nodes[3]]
        positions.remove(guiNode.getPosition())

        guiNode = guiNodeMap[nodes[4]]
        positions.remove(guiNode.getPosition())

        self.assertEquals(0, len(positions))

        guiNode = guiNodeMap[nodes[5]]
        self.assertEquals((100,100), guiNode.getPosition())

        return


    def testLayout4(self):
        builder = self.builder

        pomsetContext = builder.createNewNestPomset()
        pomset = pomsetContext.pomset()

        definitionContext = builder.createNewAtomicPomset()
        definitionToReference = definitionContext.pomset()

        nodes = []
        nodes.append(builder.createNewNode(
                pomset, name='A', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='B', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='C', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='D', definitionToReference=definitionToReference))

        guiNodeMap = dict([(x, GraphModule.Node(x)) for x in nodes])

        edges = []
        for sourceNode, targetNode in [(nodes[0], nodes[2]),
                                       (nodes[1], nodes[2]),
                                       (nodes[1], nodes[3])]:
            edges.append(
                GraphModule.Edge(
                    builder.connect(
                        pomset,
                        sourceNode, 'temporal output',
                        targetNode, 'temporal input'),
                    [guiNodeMap[sourceNode], None,
                     None, guiNodeMap[targetNode]]
                    )
                )
            pass
        
        self.policy.layoutNodes(guiNodeMap.values(), edges)

        positions = set([(250,200),(100,200)])

        guiNode = guiNodeMap[nodes[0]]
        positions.remove(guiNode.getPosition())

        guiNode = guiNodeMap[nodes[1]]
        positions.remove(guiNode.getPosition())

        self.assertEquals(0, len(positions))

        positions = set([(250,100),(100,100)])

        guiNode = guiNodeMap[nodes[2]]
        positions.remove(guiNode.getPosition())

        guiNode = guiNodeMap[nodes[3]]
        positions.remove(guiNode.getPosition())

        self.assertEquals(0, len(positions))

        return


    # END class TestBasicLayoutPolicy
    pass



class TestGraphvizLayoutPolicy(unittest.TestCase):

    def setUp(self):
        self.builder = BuilderModule.Builder()
        self.policy = PolicyModule.GraphvizLayoutPolicy()

        contextManager = ContextModule.QtContextManager()
        self.policy.contextManager(contextManager)

        contextManager.resourcePath(['resources'])

        configFilePath = os.path.sep.join(
            contextManager.resourcePath() + 
            ['testdata','TestLayoutPolicy','TestGraphvizLayoutPolicy','config'])


        with open(configFilePath) as f:

            config = ConfigModule.load(f)

            dotPath = config['path for dot']
            assert len(dotPath), 'expected to find path for dot'

            contextManager.commandPath('dot', dotPath)

            return

        raise NotImplemented(
            'could not read credentials from config file %s' % configFilePath)

        return

    def tearDown(self):
        return

    def testLayout1(self):
        builder = self.builder

        pomsetContext = builder.createNewNestPomset()
        pomset = pomsetContext.pomset()

        definitionContext = builder.createNewAtomicPomset()
        definitionToReference = definitionContext.pomset()

        nodes = []
        nodes.append(builder.createNewNode(
                pomset, name='A', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='B', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='C', definitionToReference=definitionToReference))
        nodes.append(builder.createNewNode(
                pomset, name='D', definitionToReference=definitionToReference))

        guiNodeMap = dict([(x, GraphModule.Node(x)) for x in nodes])

        edges = []
        for sourceNode, targetNode in [(nodes[0], nodes[1]),
                                       (nodes[0], nodes[2]),
                                       (nodes[1], nodes[3]),
                                       (nodes[2], nodes[3])]:
            edges.append(
                GraphModule.Edge(
                    builder.connect(
                        pomset,
                        sourceNode, 'temporal output',
                        targetNode, 'temporal input'),
                    [guiNodeMap[sourceNode], None,
                     None, guiNodeMap[targetNode]]
                    )
                )
            pass
        
        self.policy.layoutNodes(guiNodeMap.values(), edges)
        return

    # END class GraphvizLayoutPolicy
    pass
