import types
import re

from bson.objectid import ObjectId

from core import BaseObject

RE_COLOR = "#(?:[0-9a-fA-F]{3}){1,2}"

class GroundStation(BaseObject):
    
    def __init__(self,name,color,_id=ObjectId()):
        BaseObject.__init__(self)
        
        assert isinstance(name,types.StringTypes)
        assert isinstance(color,types.StringTypes)
        assert re.findall(RE_COLOR,color)[0] is color
        
        self.name = name
        self.color = color