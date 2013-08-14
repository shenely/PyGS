#!/usr/bin/env python2.7

"""Persistance service

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   08 August 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import pickle

#External libraries
import pymongo

#Internal libraries
import engine
#
##################


##################
# Export section #
#
__all__ = ["RoutinePersistance",
           "SOURCE_ROUTINE",
           "EVENT_ROUTINE",
           "CONDITION_ROUTINE",
           "ACTION_ROUTINE",
           "TARGET_ROUTINE",
           "GENERAL_ROUTINE",
           "SPECIAL_ROUTINE"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

SOURCE_OBJECT = "source"
EVENT_OBJECT = "event"
CONDITION_OBJECT = "condition"
ACTION_OBJECT = "action"
TARGET_OBJECT = "target"
GENERAL_OBJECT = "general"
SPECIAL_OBJECT = "special"
#
####################


class ObjectPersistance(object):
    routines = []
    
    def __init__(self):
        object.__init__(self)
        
        self.properties = list()
        self.methods = list()
        
        self.routines.append(self)
    
    def __call__(self,cls):
        self.cls = cls
        
        return cls
    
    def type(self,type):
        self._type = type
        
        return self
    
    def property(self,func):
        self.properties.append(func)
        
        return property(func)
        
    def method(self,func):
        self.methods.append(func)
        
        return func
    
    def persist(self,collection):
        query = dict(name=self.cls.__name__)
        document = collection.find_one(query)
        
        if document is None:
            document = dict(name = self.cls.__name__,
                            type = self._type,
                            path = pickle.dumps(self.cls),
                            properties = [property.func_name \
                                          for property in self.properties],
                            methods = [method.func_name \
                                       for method in self.methods])
            
            collection.save(document)
            
        self.cls._id = document["_id"]
        
def main():
    database = engine.Application("PyGS").database
    collection = database.Objects
    
    for routine in ObjectPersistance.routines:
        routine.persist(collection)