#!/usr/bin/env python2.7

"""Clock routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from datetime import datetime,timedelta
import logging
import types

#External libraries

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
__version__ = "0.1"#current version [major.minor]

J2000 = datetime(2000,1,1,12)

CLOCK_SCALE = 1.0
CLOCK_STEP = timedelta(0,60)
#
####################


@coroutine
def continuous(epoch=J2000,scale=CLOCK_SCALE,pipeline=None):
    """Continuous System Epoch"""
    
    assert isinstance(epoch,datetime)
    assert isinstance(scale,(types.IntType,types.FloatType))
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    now = datetime.utcnow()
    while True:
        yield epoch,pipeline
        
        past = now
        now = datetime.utcnow()
        
        epoch += scale * (now - past)
        
        logging.info("Clock.Continuous:  Updated epoch to %s" % epoch)

@coroutine
def discrete(epoch=J2000,step=CLOCK_STEP,pipeline=None):
    """Discrete System Epoch"""
    
    assert isinstance(epoch,datetime)
    assert isinstance(step,timedelta)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    while True:
        yield epoch,pipeline
        
        epoch += step
        
        logging.info("Clock.Discrete:  Updated epoch to %s" % epoch)