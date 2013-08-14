#!/usr/bin/env python2.7

"""Database routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   09 August 2013

Provides routines for interacting with a database.

Classes:
DatabaseFind  -- Find in database
DatabaseSave  -- Save in database

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-08-08    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime
import logging
import types

#External libraries
import pymongo

#Internal libraries
from . import EventRoutine,ActionRoutine
from .. import BaseObject
from .. import persist
from .. import engine
#
##################


##################
# Export section #
#
__all__ = ["DatabaseFind",
           "DatabaseSave"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


database_find = persist.ObjectPersistance()

@database_find.type(persist.EVENT_OBJECT)
class DatabaseFind(EventRoutine):
    """Story:  Find in database
    
    IN ORDER TO
    AS A
    I WANT TO
    
    """
    
    """Specification:  Find in database
    
    GIVEN
        
    Scenario 1:
    WHEN
    THEN 
    
    """
    
    name = "Database.Find"
    
    def __init__(self):
        EventRoutine.__init__(self)
        
        self.database = engine.Application("PyGS").database
        
    @database_find.property
    def collection(self):
        return self._collection
    
    @collection.setter
    def collection(self,collection):
        assert isinstance(collection,types.StringTypes)
        
        self._collection = collection
        
    @database_find.property
    def query(self):
        return self._query
    
    @query.setter
    def query(self,query):
        assert isinstance(query,types.DictType)
        
        self._query = query
        
        self.cursor = self.database[self._collection].find(self._query)
    
    def _occur(self,message):
        try:
            document = BaseObject(**self.cursor.next())
                          
            logging.info("{0}:  Found {1} in database".\
                         format(self.name,document._id))
            
            return document
        except StopIteration:
            self.cursor.close()
            
            logging.warn("{0}:  No more documents".\
                         format(self.name))


database_save = persist.ObjectPersistance()

@database_save.type(persist.ACTION_OBJECT)
class DatabaseSave(ActionRoutine):
    """Story:  Save to database
    
    IN ORDER TO
    AS A
    I WANT TO
    
    """
    
    """Specification:  Save to database
    
    GIVEN
        
    Scenario 1:
    WHEN
    THEN
    
    """
    
    name = "Database.Save"
    
    def __init__(self):
        ActionRoutine.__init__(self)
        
        self.database = engine.Applciation().database
        
    @database_save.property
    def collection(self):
        return self._collection
    
    @collection.setter
    def collection(self,collection):
        assert isinstance(collection,types.StringTypes)
        
        self._collection = collection
    
    def _execute(self,document):
        assert isinstance(document,types.DictType)
        
        self.database[self._collection].save(document)
                    
        logging.info("{0}:  Saved {1} in database".\
                     format(self.name,document._id))
        
        return document