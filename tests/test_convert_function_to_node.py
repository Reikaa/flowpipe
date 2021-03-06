from __future__ import print_function
import json

from flowpipe.node import INode, function_to_node


@function_to_node(outputs=['out'])
def function_for_testing(input1, input2):
    """Test documentation."""
    return {'out': 'TestHasPassed'}


def test_input_plugs_are_taken_from_func_inputs():
    """Input args to the unction are used as input plugs for the node."""
    @function_to_node()
    def function(arg, kwarg='intial_value'):
        pass
    node = function()
    assert 2 == len(node.inputs.keys())
    assert 'arg' in node.inputs.keys()
    assert 'kwarg' in node.inputs.keys()

def test_name_is_taken_from_func_name_if_not_provided():
    """Function name is converted to node name if not provided."""
    @function_to_node()
    def function():
        pass
    node = function()
    assert 'function' == node.name

def test_name_can_be_provided_as_kwarg():
    """Name and identifier can be provided."""
    @function_to_node()
    def function():
        pass
    node = function(name='ProvidedNodeName', identifier='TestIdentifier')
    assert 'ProvidedNodeName' == node.name
    assert 'TestIdentifier' == node.identifier

def test_doc_is_taken_from_func():
    """Docstring is taken from the function."""
    @function_to_node()
    def function():
        """Function Documentation"""
    node = function()
    assert function.__doc__ == node.__doc__

def test_define_outputs():
    """Outputs have to be defined as a list of strings."""
    @function_to_node(outputs=['out1', 'out2'])
    def function():
        pass
    node = function()
    assert 2 == len(node.outputs.keys())
    assert 'out1' in node.outputs.keys()
    assert 'out2' in node.outputs.keys()

def test_decorator_returns_node_instances():
    """A call to the decorated function returns a Node instance."""
    @function_to_node()
    def function():
        pass
    node1 = function()
    node2 = function()
    assert node1 != node2

def test_serialize_function_node():
    """Serialization also stored the location of the function."""
    node = function_for_testing()
    data = json.dumps(node.serialize())
    deserialized_node = INode.deserialize(json.loads(data))
    assert node.__doc__ == deserialized_node.__doc__
    assert node.name == deserialized_node.name
    assert node.inputs.keys() == deserialized_node.inputs.keys()
    assert node.outputs.keys() == deserialized_node.outputs.keys()
    assert node.evaluate() == deserialized_node.evaluate()

def test_use_self_as_first_arg_if_present():
    """If wrapped function has self as first arg, it's used reference to class like in a method."""
    @function_to_node(outputs=['test'])
    def function(self, arg1, arg2):
        return {'test': self.test}
    node = function()
    node.test = 'test'
    assert 'test' == node.evaluate()['test']

    @function_to_node(outputs=['test'])
    def function(arg1, arg2):
        return {'test': 'Test without self'}
    node = function()
    assert 'Test without self' == node.evaluate()['test']

def test_assign_input_args_to_function_input_plugs():
    """Assign inputs to function to the input plugs."""
    @function_to_node(outputs=['test'])
    def function(arg):
        return {'test': arg}
    node = function(arg="test")
    assert 'test' == node.evaluate()['test']
