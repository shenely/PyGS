#!/usr/bin/env python2.7

"""View routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 February 2013

Provides routines for generating views.

Functions:
inertial   -- Inertial view
geographic -- Geographic view
horizontal -- Horizontal view

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-07    shenely         1.0         Promoted to version 1.0
2013-02-10                                Using InertialState now

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from core import coroutine,encoder
from core.message import RequestMessage
from . import BaseView
from space.state import *
#
##################


##################
# Export section #
#
__all__ = ["inertial",
           "geographic",
           "horizontal"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


@coroutine
def inertial(address,pipeline=None):
    """Story:  Inertial view
    
    IN ORDER TO view the inertial location of a spacecraft
    AS A user segment
    I WANT TO generate a global (3D) view
    
    """
    
    """Specification:  Inertial view
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream states received
    WHEN inertial states are received from upstream
    THEN the a global (3D) view SHALL be generated
        AND the view SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("View.Inertial:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("View.Inertial:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,InertialState),states)
            
            view = BaseView(states[0].epoch,states,"inertial")
            notice = RequestMessage("view",view)
            message = address,encoder(notice)
                            
            logging.info("View.Inertial  Generated for %s" % address)

@coroutine
def geographic(address,pipeline=None):
    """Story:  Geographic view
    
    IN ORDER TO view the geographic location of a spacecraft
    AS A user segment
    I WANT TO generate a global (2D) view
    
    """
    
    """Specification:  Geographic view
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream states received
    WHEN geographic states are received from upstream
    THEN the a global (2D) view SHALL be generated
        AND the view SHALL be sent downstream
    
    """

    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("View.Geographic:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("View.Geographic:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,GeographicState),states)
            
            view = BaseView(states[0].epoch,states,"geographic")
            notice = RequestMessage("view",view)
            message = address,encoder(notice)
                            
            logging.info("View.Geographic  Generated for %s" % address)

@coroutine
def horizontal(address,pipeline=None):
    """Story:  Horizontal view
    
    IN ORDER TO view the horizontal location of a spacecraft
    AS A user segment
    I WANT TO generate a local view
    
    """
    
    """Specification:  Horizontal view
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream states received
    WHEN horizontal states are received from upstream
    THEN the a local view SHALL be generated
        AND the view SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("View.Horizontal:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("View.Horizontal:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,HorizontalState),states)
            
            view = BaseView(states[0].epoch,states,"horizontal")
            notice = RequestMessage("view",view)
            message = address,encoder(notice)
                            
            logging.info("View.Horizontal:  Generated for %s" % address)
