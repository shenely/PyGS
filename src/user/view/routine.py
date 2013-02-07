#!/usr/bin/env python2.7

"""View routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 February 2013

Provides routines for generating views.

Functions:
global2d -- Global (geographic) view
global3d -- Global (inertial) view
local    -- Local (horizontal) view

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-06    shenely         1.0         Promoted to version 1.0

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
from . import BaseView
from space.state import *
#
##################


##################
# Export section #
#
__all__ = ["global2d",
           "global3d",
           "local"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


@coroutine
def global2d(address,pipeline=None):
    """Story:  Global (geographic) view
    
    IN ORDER TO view the geographic location of a spacecraft
    AS A user segment
    I WANT TO generate a global (2D) view
    
    """
    
    """Specification:  Global (geographic) view
    
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
    
    logging.debug("View.Global2D:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("View.Global2D:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,GeographicState),states)
            
            notice = BaseView(states[0].epoch,states,"global2d")
            message = address,encoder(notice)
                            
            logging.info("View.Global2D  Generated for %s" % address)


@coroutine
def global3d(address,pipeline=None):
    """Story:  Global (inertial) view
    
    IN ORDER TO view the inertial location of a spacecraft
    AS A user segment
    I WANT TO generate a global (3D) view
    
    """
    
    """Specification:  Global (inertial) view
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream states received
    WHEN Cartesian states are received from upstream
    THEN the a global (3D) view SHALL be generated
        AND the view SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("View.Global3D:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("View.Global3D:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,CartesianState),states)
            
            notice = BaseView(states[0].epoch,states,"global3d")
            message = address,encoder(notice)
                            
            logging.info("View.Global3D  Generated for %s" % address)


@coroutine
def local(address,pipeline=None):
    """Story:  Local (horizontal) view
    
    IN ORDER TO view the horizontal location of a spacecraft
    AS A user segment
    I WANT TO generate a local view
    
    """
    
    """Specification:  Local (horizontal) view
    
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
    
    logging.debug("View.Local:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("View.Local:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,HorizontalState),states)
            
            notice = BaseView(states[0].epoch,states,"local")
            message = address,encoder(notice)
                            
            logging.info("View.Local:  Generated for %s" % address)
