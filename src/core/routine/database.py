#!/usr/bin/env python2.7

"""Database routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   12 February 2013

Provides routines for accessing a database.

Functions:
save -- Save document
find -- Find document

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-05    shenely         1.0         Promoted to version 1.0
2013-02-12                    1.1         Changed save to insert

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
__version__ = "1.1"#current version [major.minor]
#
####################


@coroutine
def save(collection,pipeline=None):
    """Story:  Save document
    
    IN ORDER TO for data to persist
    AS A generic segment
    I WANT TO store documents in a database
    
    """
    
    """Specification:  Save document
    
    GIVEN a collection of documents
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream document received
    WHEN an document is received from upstream
    THEN the document SHALL be saved to the collection
        AND the document SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(collection,Collection)
    assert isinstance(pipeline,types.GeneratorType)
    
    document = None
    
    logging.debug("Database.Save:  Starting")
    while True:
        try:
            document = yield document,pipeline
        except GeneratorExit:
            logging.warn("Database.Save:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(document,dict)
            
            document.id = collection.insert(document)
            
            logging.info("Database.Save:  Saved document(s)")

@coroutine
def find(collection,pipeline=None):
    """Story:  Find document(s)
    
    IN ORDER TO retrieve persistent data
    AS A generic segment
    I WANT TO query the database for documents
    
    """
    
    """Specification:  Find document(s)
    
    GIVEN a collection of documents
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream query received
    WHEN a query is received from upstream
    THEN the query SHALL be executed against the collection
        AND any documents found SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(collection,Collection)
    assert isinstance(pipeline,types.GeneratorType)
    
    documents = None
    
    logging.debug("Database.Find:  Starting")
    while True:
        try:
            query = yield documents,pipeline
        except GeneratorExit:
            logging.warn("Database.Find:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:       
            #input validation
            assert isinstance(query,dict) or query is None
            
            documents = collection.find(query)
            
            logging.info("Database.Find:  Found document(s)")