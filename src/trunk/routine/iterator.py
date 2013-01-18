#!/usr/bin/env python2.7

"""Iterator routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   11 January 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import pi,sqrt,cos,sin,tan,atan
from datetime import datetime,timedelta
import logging
import types

#External libraries
from scipy.optimize import newton

#Internal libraries
from . import coroutine
from ..core.state import KeplerianState
#
##################


##################
# Export section #
#
__all__ = ["caesium"
           "kepler"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

EPOCH_STEP_SIZE = timedelta(seconds=60)
ANOMALY_ERROR = 1e-15

KEPLER_EQUATION = lambda E,M,e:E - e * sin(E) - M
KEPLER_DERIVATIVE = lambda E,M,e:1 - e * cos(E)
#
####################


@coroutine
def caesium(epoch=datetime.utcnow(),scale=1,pipeline=None):
    """Update System Epoch"""
    
    assert isinstance(epoch,datetime)
    assert isinstance(scale,(types.IntType,types.FloatType))
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    now = datetime.utcnow()
    while True:
        yield epoch,pipeline
        
        past = now
        now = datetime.utcnow()
        
        epoch += scale * (now - past)
        
        logging.info("Routine.Iterator:  Caesium iterated to %s" % epoch)

@coroutine
def kepler(state,margin,step=EPOCH_STEP_SIZE,error=ANOMALY_ERROR,pipeline=None):
    """Kepler Iteration"""
    
    assert isinstance(state,KeplerianState)
    assert isinstance(step,timedelta)
    assert isinstance(error,types.FloatType)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        yield message,pipeline        

        e = state.e
        M = (state.M + state.n * step.total_seconds()) % (2 * pi)
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,e),error)
        
        state.epoch += step
        state.theta = 2 * atan(sqrt((1 + e) / (1 - e)) * tan(E / 2))
                
        message = state.copy()
                        
        logging.info("Routine.Iterator:  Kepler iterated to %s" % state.epoch)