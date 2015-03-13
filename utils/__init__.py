

from bisect import bisect_left, bisect_right

##############################################
class Bunch:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return str(self.__dict__)
    def update(self,**kwargs):
        self.__dict__.update(kwargs)
        return self

##############################################
class SortedCollection(object):
    def __init__(self, iterable=(), key=None):
        self._given_key = key
        key = (lambda x: x) if key is None else key
        decorated = sorted((key(item), item) for item in iterable)
        self._keys = [k for k, item in decorated]
        self._items = [item for k, item in decorated]
        self._key = key
         
    def __len__(self):
        return len(self._items)
        
    def __iter__(self):
        return iter(self._items)

    def index(self, item):
        'Find the position of an item.  Raise ValueError if not found.'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        j = bisect_right(self._keys, k)
        return self._items[i:j].index(item) + i
        
    def insert(self, item):
        'Insert a new item.  If equal keys are found, add to the left'
        k = self._key(item)
        i = bisect_left(self._keys, k)
        self._keys.insert(i, k)
        self._items.insert(i, item)
        
    def remove(self, item):
        'Remove first occurence of item.  Raise ValueError if not found'
        i = self.index(item)
        del self._keys[i]
        del self._items[i]
        
    def find(self, k):
        'Return first item with a key == k.  Raise ValueError if not found.'
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            return self._items[i]
        raise ValueError('No item found with key equal to: {0}'.format(k))
    
    def replace_or_create(self, item):
        k = self._key(item)
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            self._items[i] = item
        else:
            self._keys.insert(i, k)
            self._items.insert(i, item)
    
    def remove_by_key(self,k):
        i = bisect_left(self._keys, k)
        if i != len(self) and self._keys[i] == k:
            del self._keys[i]
            del self._items[i]
        


def inspector():
    '''
        allows introspection in script
        problem with garbage collection as documented in inspect
    '''
    import code, inspect, readline, rlcompleter
    f = inspect.currentframe().f_back
    vrs = f.f_globals
    vrs.update(f.f_locals)
    readline.set_completer(rlcompleter.Completer(vrs).complete)
    readline.parse_and_bind("tab: complete")
    code.InteractiveConsole(vrs).interact(banner="interactive shell launched from script Ctrl-D to go back to execution")
