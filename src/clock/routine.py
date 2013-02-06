#!/usr/bin/env python2.7

"""Clock routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   06 February 2013

Provides routines for driving the simulation clock.

Functions:
continuous -- Continuous clock routine
discrete   -- Discrete clock routine
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
from datetime import datetime,timedelta
import logging
import types

#External libraries
from bson.tz_util import utc

#Internal libraries
from core import coroutine
#
##################


##################
# Export section #
#
__all__ = ["continuous",
           "discrete"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

CLOCK_SCALE = 1.0#Clock rate scale (default 1:1, i.e. real-time)
CLOCK_STEP = timedelta(seconds=60)#Clock step (default to 60 seconds)
#
####################


@coroutine
def continuous(epoch=J2000,scale=CLOCK_SCALE,pipeline=None):
    """Story:  Continuous clock
    
    IN ORDER TO manage the simulation time
    AS A clock segment
    I WANT TO progress the simulation time based off the progress of
        system time
    
    """
    
    """Specification:  Continuous clock
    
    GIVEN an initial epoch (default J2000.0)
        AND a clock rate scale (default 1.0)
        AND a downstream pipeline (default null)
        
    Scenario 1:  Simulation time requested
    WHEN the clock value is requested from upstream
    THEN the system time since the last request SHALL be determined
        AND the elapsed time SHALL be scaled by the clock rate scale
        AND the simulation time SHALL be increased by the elapsed time
        AND the simulation time SHALL be sent downstream
    
    Scenario 2:  Clock rate scale modified
    WHEN a clock rate scale is sent from upstream
        AND the clock scale rate is a numeric value
    THEN the clock scale rate SHALL be modified to the upstream value
        AND the simulation time SHALL be requested
    
    """
    
    #configuration validation
    assert isinstance(epoch,datetime)
    assert isinstance(scale,(types.IntType,types.FloatType))
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    now = datetime.utcnow()
        
    logging.debug("Clock.Continuous:  Starting at %s" % epoch)
    while True:
        try:
            message = yield epoch,pipeline
        except GeneratorExit:
            logging.warn("Clock.Continuous:  Stopping at %s" % epoch)
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            if message is not None:
                #input validation
                assert isinstance(message,(types.IntType,types.FloatType))
                
                scale = message
                
            past = now
            now = datetime.utcnow()
            
            epoch += scale * (now - past)#increase simulation time
            
            logging.info("Clock.Continuous:  Updated epoch to %s" % epoch)

@coroutine
def discrete(epoch=J2000,step=CLOCK_STEP,pipeline=None):
    """Story:  Discrete clock
    
    IN ORDER TO manage the simulation time
    AS A clock segment
    I WANT TO progress the simulation time at fixed intervals
    
    """
    
    """Specification:  Discrete clock
    
    GIVEN an initial epoch (default J2000.0)
        AND a clock step (default 60 seconds)
        AND a downstream pipeline (default null)
        
    Scenario 1:  Simulation time requested
    WHEN the clock value is requested from upstream
    THEN the simulation time SHALL be increased by the clock step size
        AND the simulation time SHALL be sent downstream
    
    Scenario 2:  Clock step size modified
    WHEN a clock step size sent from upstream
        AND the clock step size represents a change in time
    THEN the clock step size SHALL be modified to the upstream value
        AND the simulation time SHALL be requested
    
    """
    
    #configuration validation
    assert isinstance(epoch,datetime)
    assert isinstance(step,timedelta)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
        
    logging.debug("Clock.Discrete:  Starting at %s" % epoch)
    while True:
        try:
            message = yield epoch,pipeline
        except GeneratorExit:
            logging.warn("Clock.Discrete:  Stopping at %s" % epoch)
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            if message is not None:
                #input validation
                assert isinstance(message,timedelta)
                
                step = message
                
            epoch += step#increase simulation time
            
            logging.info("Clock.Discrete:  Updated epoch to %s" % epoch)
