import itertools as it
import heapq
import inspect
import collections
import operator as op

# need to replicate, hack for now
#from . import time

class A:
    pass

time = A()

time.gMin = 0
time.gMax = 214739855
time.printI64 = lambda x: x
time.printStamp = print

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
# creators
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
        return self.tuple._make(c(node=node, label='{0}{1}{2}'.format(label, self.glue, f))
                                for f, c in it)
        
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
                raise Exception('Node {0} cannot depend on not constructed node {1}'.format(str(self), str(v.node)))
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
        self.output(self.op(self.inp0.v, self.inp1.v))
        
    def get_inputs(self):
        return [self.inp0, self.inp1]
        

class AggOpNode(Node):
    __slots__ = ('inp', 'op')
    def __init__(self, inp, op, label=None):
        self.inp = inp
        self.op = op
        if not label:
            label = ','.join([str(x) for x in (inp[:2] + ['...'] + inp[-2:] if len(inp) >= 5 else inp)])
            label = '{0}({1})'.format(op.__name__, label)
        Node.__init__(self, Single(default = op((x.v0 for x in inp))), label=label)
    
    def __call__(self):
        self.output(self.op((x.v for x in self.inp)))
    
    def get_inputs(self):
        return self.inp
    
########################   
# ts function
########################
def FuncSpec(output_creator, depend_on_names=(), label=''):
    def wrapper(tsfunc):
        def wire(*args, **kwargs):
            nonlocal output_creator, depend_on_names, label
            if label is '':
                label = tsfunc.__name__
            try:
                sig = inspect.signature(tsfunc)
                ba = sig.bind(*args, **kwargs)
                depend_on = [ba.arguments[d_name] for d_name in depend_on_names]
            except:
                raise Exception('Cannot bind {0} to arguments!'.format(tsfunc.__name__))
            
            class FuncNode(Node):
                __slots__ = ('inputs', 'key_inputs', 'tsfunc')
                def __init__(self, inputs, key_inputs, tsfunc, depend_on, output_creator, label):
                    self.inputs = inputs
                    Node.__init__(self, output_creator, depend_on=depend_on, label=label)
                    key_inputs['Return'] = self.output
                    self.key_inputs = key_inputs
                    self.tsfunc = tsfunc
                
                def __call__(self):
                    self.tsfunc(*self.inputs, **self.key_inputs)
                
                def get_inputs(self):
                    return self.inputs
                    
            node = FuncNode(list(arg), keyargs, tsfunc, depend_on, output_creator, label)
            return node.get_output()
        return wire
    return wrapper


#####################
# Sources
#####################
class Source(Node):
    __slots__ = ('time', 'port', 'iter', 'next_value', 'seqno', 'seqno_start', 'seqno_inc')
    def __init__(self, port, output_creator, label):
        Node.__init__(self, port, output_creator, label=label)
        self.seqno = 0
        self.port = port
        self.iter = None
        self.time = time.gMin
        self.next_value = None
        self.constructed = True
    
    def __lt__(self, other):
        return self.time < other.time or (self.time == other.time and self.seqno < other.seqno)
        
    def __iter__(self):
        self.time = time.gMin
        self.next_value = None
        self.iter = iter(self.port)
        return self
    
    def __next__(self):
        next_time, self.next_value = next(self.iter)
        if next_time < self.time:
            raise Exception('time decreaess in the source {0} at {1}!'.format(str(self), self.time))
        elif next_time > self.time:
            self.seqno = 0
        else:
            self.seqno += 1
        self.time = next_time
        return self
        
    def __call__(self):
        pass
    
    def get_inputs(self):
        return []
        
    def reset(self, date, levels):
        Node.reset(self, date, levels)
        if hasattr(self.port, 'reset'):
            self.port.reset(date)

class ValueSource(Source):
    __slots__ = ()
    def __init__(self, port, default=float('nan'), label='source'):
        Source.__init__(self, port, Single(default), label)
        
    def __call__(self):
        self.output(self.next_value)
        
class ArraySource(Source):
    __slots__ = ()
    def __init__(self, port, N, defaults=None, label='source'):
        defaults = defaults if defaults else (float('nan'), ) * N
        creators_array = tuple(Single(v) for v in defaults)
        Source.__init__(self, port, Array(creators_array), label)
    
    def __call__(self):
        for i, v in enumerate(self.next_value):
            self.output[i](v)
            
            
class StructSource(Source):
    __slots__ = ()
    def __init__(self, port, name, fields, defaults, glue='.', label='source'):
        creators = [Single(v) for v in defaults]
        Source.__init__(self, port, Struct(name, fields, creators, glue), label)
    
    def __call__(self):
        for i, v in enumerate(self.next_value):
            self.output[i](v)
    
        
#####################
# engine
#####################

def getNodesRwd(obj):
    return set(v.node for v in getValues(obj) if v.node is not None)

def getNodesFwd(obj):
    return set(it.chain.from_iterable(v.observers for v in getValues(obj)))

def iterBreadthFirst(nodes, get_children):
    setFrom = set()
    setTo = set(nodes)
    while(setTo):
        setFrom = etTo
        setTo = set()
        for node in setFrom:
            for nodeTo in get_children(node):
                setTo.add(nodeTo)
            yield node

def getSources(inputs):
    sources = set()
    for node in iterBreadthFirst(getNodesRwd(inputs), lambda x: getNodesRwd(x.get_inputs())):
        if len(node.get_inputs()) == 0:
            sources.add(node)
    return sources

def getHeight(sources):
    return max(node.height for node in iterBreadthFirst(source, lambda x: getNodeFwd(x.output)))
    
#########################
# engine API
#########################

# globals
gValueTime = Value(time.gMin, 'time')


def Run(outputs, date=None, start=None, end=None):
    global gNowTime
    
    if not outputs:
        return
    
    start = start if start else time.gMin
    end = end if end else time.gMax
    
    sources = getSources(outputs)
    print('----------- TS Engine -------------')
    print('date        = {0}\nstart time = {1}\nend time    = {2}\nsources:'.format(date, time.printI64(start), time.printI64(end)))
    for source in sources:
        print('     {0}'.format(str(source)))
    
    height = getHeight(sources)
    levels = [set() for _ in range(height+1)]
    levels = levels
    chain_levels = it.chain.from_iterable
    
    #initialize
    gValueTime.reset()
    for node in iterBreadthFirst(sources, lambda x: getNodesFwd(x.output)):
        node.reset(date, levels)
        #if d_f: print("Run()[reste]:label={0},class={1},id={2},height={3},depend_on={4}".format(
        #               node.label, node.__class__, id(node), node.height, sorted(set([id(v.node) for v in deeplistiter(node.depend_on)]))),
        #               logfile)
    all_sources = heapq.merge(*sources)
    next_source = all_sources.__next__
    tick_time = gValueTime.__call__
    clear_levels = [level.clear for level in levels]
    
    # start iteration
    time.printStamp('begin ...')
    source = next(all_sources)
    while source.time < start:
        source = next_source()
    
    nextTime, nextSeqno = source.time, source.seqno
    gNowTime, nowSeqno = nextTime, nextSeqno
    try:
        while gNowTime < end:
            while nextTime == gNowTime and nextSeqno == nowSeqno:
                source()
                source = next_source()
                nextTime, nextSeqno = source.time, source.seqno
            
            # if d_f: gNowTime_str = printI64(gNowTime)
            
            if(gNowTime < nextTime):
                tick_time(gNowTime)
            for a in chain_levels(levels):
                a()
                
            for clear_level in clear_levels:
                clear_level()
            
            gNowTime, nowSeqno = nextTime, nextSeqno
    except StopIteration:
        tick_time(gNowTime)
        for a in chain_levels(levels):
            a()
        for clear_level in clear_levels:
            clear_level()
    time.printStamp('end!')
    print('--------- TS Engine ----------')
    
