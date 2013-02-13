import types
import re

from core import BaseObject
from clock.epoch import EpochState
from ground.status import BaseStatus

RE_COLOR = "#(?:[0-9a-fA-F]{3}){1,2}"

class BaseAsset(BaseObject):
    def __init__(self,type,name,color,*args,**kwargs):
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(type,types.StringTypes)
        assert isinstance(name,types.StringTypes)
        assert isinstance(color,types.StringTypes)
        
        self.type = type
        self.name = name
        self.color = color

class SpaceAsset(BaseAsset):
    def __init__(self,name,color,*args,**kwargs):
        BaseAsset.__init__(self,"space",name,color,*args,**kwargs)

class GroundAsset(BaseObject):    
    def __init__(self,name,color,*args,**kwargs):
        BaseAsset.__init__(self,"ground",name,color,*args,**kwargs)