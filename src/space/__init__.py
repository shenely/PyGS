import types
import re

from core import BaseObject
from clock.epoch import EpochState
from ground.status import BaseStatus

RE_COLOR = "#(?:[0-9a-fA-F]{3}){1,2}"

class Spacecraft(BaseObject):
    type = "space"
    
    def __init__(self,name,color,status,state,*args,**kwargs):
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(name,types.StringTypes)
        assert isinstance(color,types.StringTypes)
        assert isinstance(status,BaseStatus)
        assert isinstance(state,EpochState)
        
        self.name = name
        self.color = color
        self.status = status
        self.state = state