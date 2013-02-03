import types
import re

from core import ObjectDict

RE_COLOR = "#(?:[0-9a-fA-F]{3}){1,2}"

class Spacecraft(ObjectDict):
    type = "space"
    
    def __init__(self,name,color):
        ObjectDict.__init__(self)
        
        assert isinstance(name,types.StringTypes)
        assert isinstance(color,types.StringTypes)
        assert re.findall(RE_COLOR,color)[0] is color
        
        self.name = name
        self.color = color