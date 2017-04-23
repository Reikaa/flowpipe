from __future__ import print_function

import unittest

from flowpipe.node import INode
from flowpipe.plug import InputPlug, OutputPlug
from flowpipe.graph import Graph


class TestNode(INode):

    def __init__(self, name=None):
        super(TestNode, self).__init__(name)
        OutputPlug('out', self)
        InputPlug('in1', self, 0)
        InputPlug('in2', self, 0)

    def compute(self, in1, in2):
        """Multiply the two inputs."""
        return {'out': in1 * in2}


class TestGraph(unittest.TestCase):
    """Test the Graph."""

    def test_evaluation_grid(self):
        """The nodes as a 2D grid."""
        start = TestNode('start')
        n11 = TestNode('11')
        n12 = TestNode('12')
        n21 = TestNode('21')
        n31 = TestNode('31')
        n32 = TestNode('32')
        n33 = TestNode('33')
        end = TestNode('end')

        # Connect them
        start.outputs['out'] >> n11.inputs['in1']
        start.outputs['out'] >> n21.inputs['in1']
        start.outputs['out'] >> n31.inputs['in1']

        n31.outputs['out'] >> n32.inputs['in1']
        n32.outputs['out'] >> n33.inputs['in1']

        n11.outputs['out'] >> n12.inputs['in1']
        n33.outputs['out'] >> n12.inputs['in2']

        n12.outputs['out'] >> end.inputs['in1']
        n21.outputs['out'] >> end.inputs['in2']

        nodes = [start, n11, n12, n21, n31, n32, n33, end]
        graph = Graph(nodes=nodes)

        order = [[start], [n11, n21, n31], [n32], [n33], [n12], [end]]

        for i, row in enumerate(graph.evaluation_grid):
            for node in row:
                self.assertIn(node, order[i])
    # end def test_evaluation_grid

    def test_linar_evaluation_sequence(self):
        """A linear graph."""
        n1 = TestNode('n1')
        n2 = TestNode('n2')
        n3 = TestNode('n3')
        n1.outputs['out'] >> n2.inputs['in1']
        n2.outputs['out'] >> n3.inputs['in1']
        nodes = [n2, n1, n3]
        graph = Graph(nodes=nodes)

        seq = [s.name for s in graph.evaluation_sequence]

        self.assertEqual(['n1', 'n2', 'n3'], seq)
    # end def test_linar_evaluation_sequence

    def test_branching_evaluation_sequence(self):
        """Branching graph."""
        n1 = TestNode('n1')
        n2 = TestNode('n2')
        n3 = TestNode('n3')
        n1.outputs['out'] >> n2.inputs['in1']
        n1.outputs['out'] >> n3.inputs['in1']
        nodes = [n2, n1, n3]
        graph = Graph(nodes=nodes)

        seq = [s.name for s in graph.evaluation_sequence]

        self.assertEqual('n1', seq[0])
        self.assertIn('n2', seq[1:])
        self.assertIn('n3', seq[1:])
    # end def test_branching_evaluation_sequence

    def test_complex_branching_evaluation_sequence(self):
        """Connect and disconnect nodes."""
        # The Nodes
        start = TestNode('start')
        n11 = TestNode('11')
        n12 = TestNode('12')
        n21 = TestNode('21')
        n31 = TestNode('31')
        n32 = TestNode('32')
        n33 = TestNode('33')
        end = TestNode('end')

        # Connect them
        start.outputs['out'] >> n11.inputs['in1']
        start.outputs['out'] >> n21.inputs['in1']
        start.outputs['out'] >> n31.inputs['in1']

        n31.outputs['out'] >> n32.inputs['in1']
        n32.outputs['out'] >> n33.inputs['in1']

        n11.outputs['out'] >> n12.inputs['in1']
        n33.outputs['out'] >> n12.inputs['in2']

        n12.outputs['out'] >> end.inputs['in1']
        n21.outputs['out'] >> end.inputs['in2']

        nodes = [start, n11, n12, n21, n31, n32, n33, end]
        graph = Graph(nodes=nodes)

        seq = [s.name for s in graph.evaluation_sequence]

        self.assertEqual('start', seq[0])

        self.assertIn('11', seq[1:4])
        self.assertIn('21', seq[1:4])
        self.assertIn('31', seq[1:4])

        self.assertIn('32', seq[4:6])
        self.assertIn('33', seq[4:6])

        self.assertEqual('12', seq[-2])
        self.assertEqual('end', seq[-1])
    # end def test_complex_branching_evaluation_sequence
# end class TestGraph


class TestSubGraphs(unittest.TestCase):
    """Test using Graphs like nodes, as subgraphs."""

    def test_dynamic_graph_inputs(self):
        """A Graph can reference input and output Plugs of it's nodes."""
        # Graph 1
        g1_start = TestNode('g1_start')
        g1_node = TestNode('g1_node')
        g1_start.outputs['out'] >> g1_node.inputs['in1']
        graph1 = Graph('Graph1', [g1_start, g1_node])

        # Adding Input Plugs
        graph1.inputs['in'] = g1_start.inputs['in1']
        graph1.outputs['out'] = g1_node.outputs['out']

        # Graph 1
        g2_start = TestNode('g2_start')
        g2_node = TestNode('g2_node')
        g2_start.outputs['out'] >> g2_node.inputs['in1']
        graph2 = Graph('Graph2', [g2_start, g2_node])

        # Adding Input Plugs
        graph2.inputs['in'] = g2_start.inputs['in1']
        graph2.outputs['out'] = g2_node.outputs['out']

        # Connecting Input Plugs
        # graph2.inputs['in'] >> g2_start.inputs['in1']
        graph1.outputs['out'] >> graph2.inputs['in']
        g2_node.outputs['out'] >> graph2.outputs['out']

        # Creating a top graph
        nodes = [graph1, graph2]
        graph = Graph(nodes=nodes)

        # Set some values and evaluate the graph
        graph1.inputs['in'].value = 3
        g1_start.inputs['in2'].value = 2
        g1_node.inputs['in2'].value = 1
        g2_start.inputs['in2'].value = 1
        g2_node.inputs['in2'].value = 1

        graph.evaluate()
        self.assertEqual(6, g2_node.outputs['out'].value)
    # def test_dynamic_graph_inputs
# end class TestSubGraphs


if __name__ == '__main__':
    unittest.main()
# end if
