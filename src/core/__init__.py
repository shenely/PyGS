#!/usr/bin/env python2.7

"""Core objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   26 July 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import functools
import types
import json

#External libraries
from numpy import matrix
from bson import json_util
from bson.objectid import ObjectId

#Internal libraries
#
##################


##################
# Export section #
#
__all__= ["coroutine",
          "ObjectDict",
          "BaseObject",
          "encoder",
          "decoder"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


def coroutine(func):
    def wrapper(*args,**kw):
        gen = func(*args, **kw)
        gen.next()
        return gen
    wrapper.__name__ = func.__name__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__  = func.__doc__
    return wrapper

class ObjectDict(dict):
    def __getattr__(self,name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError
    
    def __setattr__(self,name,value):
        self[name] = value
    
    def __delattr__(self,name):
        del self[name]

class BaseObject(ObjectDict):
    def __init__(self,_id=None,**kwargs):
        ObjectDict.__init__(self,**kwargs)
        
        assert isinstance(_id,ObjectId) or _id is None
        
        self._id = _id if _id is not None else ObjectId()
        
def object_hook(dct):
    dct = json_util.object_hook(dct)
    
    if isinstance(dct,types.DictType):
        dct = ObjectDict(dct)
        
        if hasattr(dct,"$matrix"):
            dct = matrix(getattr(dct,"$matrix")).T
    
    return dct

def default(obj):
    if isinstance(obj,matrix):
        obj = { "$matrix": obj.T.tolist() }
    else:
        obj = json_util.default(obj)
        
    return obj

encoder = functools.partial(json.dumps,default=default)
decoder = functools.partial(json.loads,object_hook=object_hook)