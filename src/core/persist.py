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
import sqlite3

#External libraries

#Internal libraries
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

SOURCE_ROUTINE = "source"
EVENT_ROUTINE = "event"
CONDITION_ROUTINE = "condition"
ACTION_ROUTINE = "action"
TARGET_ROUTINE = "target"
GENERAL_ROUTINE = "general"
SPECIAL_ROUTINE = "special"
#
####################


class RoutinePersistance(object):
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
        self.type = type
        
        return self
    
    def property(self,func):
        self.properties.append(func)
        
        return property(func)
        
    def method(self,func):
        self.methods.append(func)
        
        return func
    
    def persist(self,cursor):
        self.name = self.cls.__name__
        self.code = pickle.dumps(self.cls)
        
        del self.cls
        
        cursor.execute("insert into Routines (Name,Type,Code)  values (?,?,?)",
                       (self.name,self.type,self.code))
        
        oid = cursor.lastrowid
        
        for i in range(len(self.properties)):
            self.properties[i] = (self.properties[i].func_name,oid)
            
        for i in range(len(self.methods)):
            self.methods[i] = (self.methods[i].func_name,oid)
        
        cursor.executemany("insert into Properties (Name,Routine) values (?,?)",
                           self.properties)
        cursor.executemany("insert into Methods (Name,Routine) values (?,?)",
                           self.methods)
        
def main():
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    
    cursor.execute("""create table Routines 
(Name text,Type text,Code text)""")
    
    cursor.execute("""create table Properties 
(Name text,Routine integer references Routines(OID))""")
    
    cursor.execute("""create table Methods 
(Name text,Routine integer references Routines(OID))""")
    
    for routine in RoutinePersistance.routines:
        routine.persist()