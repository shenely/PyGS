#!/usr/bin/env python2.7

"""Database routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries
from pymongo.collection import Collection

#Internal libraries
from .. import coroutine
#
##################


##################
# Export section #
#
__all__ = ["save",
           "find"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]
#
####################


@coroutine
def save(collection,pipeline=None):
    assert isinstance(collection,Collection)
    assert isinstance(pipeline,types.GeneratorType)
    
    document = None
    while True:
        document = yield document,pipeline
        
        assert isinstance(document,dict)
        
        document.id = collection.save(document)
        
        logging.info("Database.Save:  Saved document with ID %s" % document.id)

@coroutine
def find(collection,pipeline=None):
    assert isinstance(collection,Collection)
    assert isinstance(pipeline,types.GeneratorType)
    
    documents = None
    while True:
        query = yield documents,pipeline
        
        assert isinstance(query,dict) or query is None
        
        documents = collection.find(query)
        
        logging.info("Database.Find:  Found %d documents" % len(documents))