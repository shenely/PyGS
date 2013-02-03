from datetime import datetime
import functools
import types
import json

from numpy import matrix
from bson import json_util
from bson.objectid import ObjectId

__all__= ["coroutine",
          "ObjectDict",
          "encoder",
          "decoder"]

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

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
    def __init__(self,_id=ObjectId(),object=None):
        ObjectDict.__init__(self)
        
        assert isinstance(_id,ObjectId)
        assert isinstance(object,ObjectId) or object is None
        
        self._id = _id
        if object is not None:self.object = object
    
    @staticmethod
    def check(kwargs):
        assert isinstance(kwargs,ObjectDict)
        assert hasattr(kwargs,"_id")
        
        return True
    
    @classmethod
    def build(cls,kwargs):
        assert cls.check(kwargs)
        
        return cls(**kwargs)
        
def object_hook(dct):
    dct = json_util.object_hook(dct)
    
    if isinstance(dct,types.DictType):
        dct = ObjectDict(dct)
        
        if hasattr(dct,"position"):
            dct.position = matrix(dct.position).T
        if hasattr(dct,"velocity"):
            dct.velocity = matrix(dct.velocity).T
    
    return dct

def default(obj):
    if isinstance(obj,matrix):
        obj = obj.T.tolist()
    else:
        obj = json_util.default(obj)
        
    return obj

encoder = functools.partial(json.dumps,default=default)
decoder = functools.partial(json.loads,object_hook=object_hook)