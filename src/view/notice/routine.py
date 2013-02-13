#!/usr/bin/env python2.7

"""Notice routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   12 February 2013

Provides routines for generating notices.

Functions:
inertial   -- Inertial view
geographic -- Geographic view
horizontal -- Horizontal view

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-07    shenely         1.0         Promoted to version 1.0
2013-02-10                    1.1         Using InertialState now
2013-02-11                    1.2         Replaced states with assets
2013-02-12                    1.3         Renaming as notices

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
from model.asset import SpaceAsset
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
__version__ = "1.3"#current version [major.minor]
#
####################


#TODO:  update documentation to mention assets (not states)

@coroutine
def inertial(assets,address,pipeline=None):
    """Story:  Inertial notice
    
    IN ORDER TO view the inertial location of a spacecraft
    AS A user segment
    I WANT TO generate a global (3D) notice
    
    """
    
    """Specification:  Inertial notice
    
    GIVEN a list of spacecraft
        AND an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream states received
    WHEN inertial states are received from upstream
    THEN the a global (3D) notice SHALL be generated
        AND the view SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(assets,types.ListType)
    assert filter(lambda asset:isinstance(asset,SpaceAsset),assets)
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("Notice.Inertial:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("Notice.Inertial:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,InertialState),states)
            
            for i in range(len(assets)):
                assets[i].state = states[i]
            
            notice = BaseView(states[0].epoch,assets,"inertial")
            message = address,encoder(notice)
                            
            logging.info("Notice.Inertial  Generated for %s" % address)

@coroutine
def geographic(assets,address,pipeline=None):
    """Story:  Geographic notice
    
    IN ORDER TO view the geographic location of a spacecraft
    AS A user segment
    I WANT TO generate a global (2D) notice
    
    """
    
    """Specification:  Geographic notice
    
    GIVEN a list of spacecraft
        AND an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream states received
    WHEN geographic states are received from upstream
    THEN the a global (2D) notice SHALL be generated
        AND the notice SHALL be sent downstream
    
    """

    #configuration validation
    assert isinstance(assets,types.ListType)
    assert filter(lambda asset:isinstance(asset,SpaceAsset),assets)
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("Notice.Geographic:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("Notice.Geographic:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,GeographicState),states)
            
            for i in range(len(assets)):
                assets[i].state = states[i]
            
            notice = BaseView(states[0].epoch,assets,"geographic")
            message = address,encoder(notice)
                            
            logging.info("Notice.Geographic  Generated for %s" % address)

@coroutine
def horizontal(assets,address,pipeline=None):
    """Story:  Horizontal notice
    
    IN ORDER TO view the horizontal location of a spacecraft
    AS A user segment
    I WANT TO generate a local notice
    
    """
    
    """Specification:  Horizontal notice
    
    GIVEN a list of spacecraft
        AND an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream states received
    WHEN horizontal states are received from upstream
    THEN the a local notice SHALL be generated
        AND the notice SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(assets,types.ListType)
    assert filter(lambda asset:isinstance(asset,SpaceAsset),assets)
    assert isinstance(address,types.StringTypes)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    
    logging.debug("Notice.Horizontal:  Starting")
    while True:
        try:
            states = yield message,pipeline
        except GeneratorExit:
            logging.warn("Notice.Horizontal:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert filter(lambda state:isinstance(state,HorizontalState),states)
            
            for i in range(len(assets)):
                assets[i].state = states[i]
                        
            notice = BaseView(states[0].epoch,assets,"horizontal")
            message = address,encoder(notice)
                            
            logging.info("Notice.Horizontal:  Generated for %s" % address)
