import sys
import string
import random

from pycheck import NUM_CALLS

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------

MIN_INT = -sys.maxint - 1
MAX_INT = sys.maxint

MAX_STR = 255
MAX_UNI = sys.maxunicode

LIST_LEN = 30

# ------------------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------------------

class PyCheckException(Exception):
    pass

class UnknownTypeException(PyCheckException):
    def __init__(self, t_def):
        self.t_def = t_def
    
    def __str__(self):
        return "PyCheck doesn't know about type: " + str(self.t_def)

class UnknownTypeException(PyCheckException):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return str(self.message)

# ------------------------------------------------------------------------------
# Base Generator
# ------------------------------------------------------------------------------

class PyCheckGenerator(object):
    def __init__(self, num_calls=NUM_CALLS):
        self._calls_remaining = num_calls

    def __iter__(self):
        return self

    def next(self):
        if self._calls_remaining <= 0:
            raise StopIteration
        else:
            self._calls_remaining -= 1
            return self.next_value()
    
    @classmethod
    def get(cls, t_def):
        if isinstance(t_def, type):
            return cls._generator_for_type(t_def)()
            
        elif isinstance(t_def, tuple) and len(t_def) == 2:
            outer, inner = t_def
            outer = cls._generator_for_type(outer)
            
            if issubclass(outer, CollectionGenerator):
                return outer(cls.get(inner))
            else:
                return (outer(), cls.get(inner))
        
        else:
            raise UnknownTypeException(t_def)
        
    @classmethod
    def _generator_for_type(cls, t_def):
        assert isinstance(t_def, type)
        
        try:
            return {
                str:     StringGenerator,
                int:     IntGenerator,
                unicode: UnicodeGenerator,
                bool:    BooleanGenerator,
                list:    ListGenerator,
                dict:    DictGenerator
            }[t_def]
        except KeyError:
            raise UnknownTypeException(t_def)

# ------------------------------------------------------------------------------
# Basic Type Generators
# ------------------------------------------------------------------------------

class StringGenerator(PyCheckGenerator):
    def next_value(self):
        length = random.randint(0, LIST_LEN)
        return ''.join([chr(random.randint(0, MAX_STR)) for x in xrange(length)])

class UnicodeGenerator(PyCheckGenerator):
    def next_value(self):
        length = random.randint(0, LIST_LEN)
        return ''.join([unicode(random.randint(0, MAX_UNI)) for x in xrange(length)])

class IntGenerator(PyCheckGenerator):
    def next_value(self):
        return random.randint(MIN_INT, MAX_INT)

class BooleanGenerator(PyCheckGenerator):
    def next_value(self):
        return random.randint(0, 1) == 1
    
# ------------------------------------------------------------------------------
# Collection Generators
# ------------------------------------------------------------------------------

class CollectionGenerator(PyCheckGenerator):
    pass

class ListGenerator(CollectionGenerator):
    def __init__(self, inner=None, num_calls=NUM_CALLS):
        PyCheckGenerator.__init__(self, num_calls=num_calls)
        if inner is None:
            raise UnknownTypeException("PyCheck needs a type for lists, such " +
                                       "as (list, int) or (list, bool)")
        self.inner = inner
    
    def next_value(self):
        length = random.randint(0, LIST_LEN)
        return [self.inner.next_value() for x in xrange(length)]

class DictGenerator(CollectionGenerator):
    def __init__(self, inner=None, num_calls=NUM_CALLS):
        PyCheckGenerator.__init__(self, num_calls=num_calls)
        self.k_inner, self.v_inner = inner
        
        if not (isinstance(self.k_inner, PyCheckGenerator) and isinstance(self.v_inner, PyCheckGenerator)):
            raise UnknownTypeException("PyCheck needs a type for dicts, such " +
                                       "as (dict, (str, int))")

    def next_value(self):
        dct = {}
        length = random.randint(0, LIST_LEN)
        for x in xrange(length):
            dct[self.k_inner.next_value()] = self.v_inner.next_value()
            
        return dct
        