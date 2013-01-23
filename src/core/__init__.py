from datetime import datetime
import functools
import types
import json

from numpy import matrix

__all__= ["ObjectDict",
          "encoder",
          "decoder"]

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"

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
        
def object_hook(obj):
    obj = ObjectDict(obj)
    
    if hasattr(obj,"epoch"):
        obj.epoch = datetime.strptime(obj.epoch,EPOCH_FORMAT)
    
    if hasattr(obj,"position"):
        obj.position = matrix(obj.position)
    if hasattr(obj,"velocity"):
        obj.velocity = matrix(obj.velocity)
    
    return obj

def object_default(obj):
    if isinstance(obj,datetime):
        obj = datetime.strftime(obj,EPOCH_FORMAT)
    elif isinstance(obj,matrix):
        obj = obj.tolist()
        
    return obj

encoder = functools.partial(json.dumps,default=object_default)
decoder = functools.partial(json.loads,object_hook=object_hook)