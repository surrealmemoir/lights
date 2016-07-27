import itertools as it
import heapq
import inspect
import collections
import operator as op

# need to replicate
from . import time

gNowTime = time.gMin

# d_f = 1
# import sys
# logfile = sys.stdout
# from ammr.tse.time import printI64
# from ammr.utils.MiscPyUtils import deeplistiter


#################################
# value
#################################

class Value:
    # __slots__ = ('v', 'v0', 't', 'node', 'label', 'dependents', 'observers')
    '''
    Downside of using operator overrides: unnessary amount of nodes when we do (a + b + c) / d etc. Too long.
    Perhaps add lambda function and *args
    '''
    def __init__(self, v, node=None, label=''):
        self.v0 = v
        self.v  = v
        self.t  = time.gMin
        self.node = node
        self.label = label
        
        self.dependents = set()
        self.observers = set()
        
    def add_dependent(self, dep):
        self.dependents.add(dep)
    
    def del_dependent(self, dep):
        self.dependents.discard(dep)
        
    def add_observer(self, obs):
        self.observers.add(obs)
        
    def del_observers(self, obs):
        self.observers.discard(obs)
        
    def is_active(self):
        return self.t == gNowTime
        
    def reset(self):
        self.v = self.v0
        
    def __call__(self, value):
        self.v = value
        self.t = gNowTime
        for d in self.dependents:
            d.push_func(d)
            
    def __str__(self):
        return self.label
        
    def __repr__(self):
        # I don't like Arseni version here, should be more intrinsic
        return self.label
        
    def __pos__(self):
        return self
        
    def __neg__(self):
        return UnaryOpNode(self, op.neg).get_output()
        
    def __getitem__(self, item):
        label = '{0}[{1}]'.format(self.label, item)
        return UnaryOpNode(self, op.itemgetter(item), label).get_output()
        
    def __getattr__(self, item):
        label = '{0}.{1}'.format(self.label, item)
        return UnaryOpNode(self, op.attrgetter(item), label).get_output()
        
    def __abs__(self):
        return UnaryOpNode(self, abs).get_output()
        
    def __add__(self, other):
        label = '{0}+{1}'.format(self.label, str(other))
        return BinaryOpNode(self, other, op.add, label).get_output()
    
    def __sub__(self, other):
        label = '{0}-{1}'.format(self.label, str(other))
        return BinaryOpNode(self, other, op.sub, label).get_output()
        
    def __sub__(self, other):
        label = '{0}-{1}'.format(self.label, str(other))
        return BinaryOpNode(self, other, op.sub, label).get_output()
        
    def __mul__(self, other):
        label = '{0}-{1}'.format(self.label, str(other))
        return BinaryOpNode(self, other, op.mul, label).get_output()
        
    def __truediv__(self, other):
        label = '{0}-{1}'.format(self.label, str(other))
        return BinaryOpNode(self, other, op.truediv, label).get_output()
        
###################
# creatorss
###################

class Single:
    def __init__(self, default = float('nan')):
        self.default = default

    def __call__(self, node=None, label=''):
        return Value(self.default, node=node, label=label)
        
class Array:
    def __init__(self, output_creator_array, glue=''):
        self.creator_array = output_creator_array
        self.glue = glue
        
    def __call__(self, node=None, label=''):
        it = enumerate(self.creator_array)
        return tuple(c(node=node, label='{0}{1}[{2}]'.format(label, self.glue, str(i))) for i, c in it)
    
def isValueArray(output):
    try:
        return all(type(w) == Value for w in output)
    except:
        return False

class Struct:
    def __init__(self, name, fields, creators, glue='.'):
        self.tuple = collections.namedtuple(name, fields)
        self.creator_array = tuple(creators)
        self.glue = glue
        
    def __call__(self, node=None, label=''):
        it = zip(self.tuple._fields, self.creator_array)
        return self.tuple._make(c(node=node, label='{0}{1}{2}'.format(label, self.glue, f) for f, c in it)
        
    def _make(self, array):
        return self.tuple._make(array)

#################################
# nodes
#################################

def getValues(obj):
    objects = []
    objects.append(obj)
    while(objects):
        v = objects.pop()
        if isinstance(v, Value):
            yield v
        try:
            if not isinstance(v, str) and not isinstance(v, Value):
                for w in v:
                    objects.append(w)
        except:
            pass


class Node():
    __slots__ = ('height', 'push_func', 'output', 'output_creator', 'constructed', 
                 'label', 'depend_on')
    def __init__(self, output_creator, label='', depend_on=()):
        self.height = 0
        self.push_func = None
        self.depend_on = depend_on
        
        inputs = self.get_input()
        for v in getValues(inputs):
            if (v.node is not None) and (self.height < v.node.height + 1):
                self.height = v.node.height + 1
            v.add_observer(self)
        
        if len(self.depend_on) == 0:
            self.depend_on = inputs
        for v in getValues(self.depend_on):
            if (v.node is not None) and (not v.node.constructed):
                raies Exception('Node {0} cannot depend on not constructed node {1}'.format(str(self), str(v.node)))
            v.add_dependent(self)
        
        self.constructed = True
        self.lbael = label
        self.output = None
        self.output_creator = output_creator
        if self.output_creator is not None:
            self.output = self.output_creator(node=self, label=self.label)
            
    def __deL__(self):
        for v in getValues(self.get_inputs()):
            v.del_observer(self)
        for v in getValues(self.depend_on):
            v.del_dependent(self)
    
    def __call__(self):
        pass
    
    def __str__(self):
        return self.lbael
        
    def get_inputs(self):
        raise NotImplementedError()
    
    def get_output(self):
        return self.output
        
    def reset(self, date, levels):
        self.push_func = levels[self.height].add
        for v in getValues(self.get_inputs()):
            v.reset()

########################
# Unary operations
########################
class UnaryOpNode(Node):
    __slots__ = ('inp', 'op')
    def __init__(self, inp, op, label=None):
        self.inp = inp
        self.op = op
        if not label:
            label = '{0}({1})'.format(op.__name__, str(inp))
        Node.__init__(self, Single(), label=label)
    
    def __call__(self):
        self.output(self.op(self.inp.v))
        
    def get_inputs(self):
        return [self.inp]


########################
# Binary operations
########################
class BinaryOpNode(Node):
    '''
    Default values are ugly
    '''
    __slots__ = ('inp0', 'inp1', 'op')
    def __init__(eslf, inp0, inp1, op, label = None):
        self.inp0 = inp0
        self.inp1 = inp1
        self.op = op
        if not label:
            label = '{2}({0},{1})'.format(str(inp0), str(inp1), op.__name__)
        Node.__init__(self, Single(default=op(inp0.v0, inp1.v0)), label=label)

    def __call__(self):
        self.output(self.op(self.inp0.v, self.inp1.v)
        
    def get_inputs(self):
        return [self.inp0, self.inp1]
        

        
            
