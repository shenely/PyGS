#!/usr/bin/env python2.7

"""Space routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   02 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import *
from datetime import datetime,timedelta
import logging
import types
import copy

#External libraries
from scipy.optimize import newton

#Internal libraries
from core import coroutine
from .state import KeplerianState
#
##################


##################
# Export section #
#
__all__ = ["kepler"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

CLOCK_STEP = timedelta(seconds=60)

KEPLER_EQUATION = lambda E,M,e:E - e * sin(E) - M
KEPLER_DERIVATIVE = lambda E,M,e:1 - e * cos(E)
ANOMALY_ERROR = 1e-15
#
####################


@coroutine
def kepler(state,step=CLOCK_STEP,pipeline=None):
    """Kepler Iteration"""
    
    assert isinstance(state,KeplerianState)
    assert isinstance(step,timedelta)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None
    
    message = None
    while True:
        yield message,pipeline

        e = state.e
        M = (state.M + state.n * step.total_seconds()) % (2 * pi)
        E = newton(KEPLER_EQUATION,M,KEPLER_DERIVATIVE,(M,e),ANOMALY_ERROR)
        
        state.epoch += step
        state.theta = 2 * atan2(sqrt(1 + e) * sin(E / 2),
                                sqrt(1 - e) * cos(E / 2))
                
        message = copy.deepcopy(state)
                        
        logging.info("Space.Kepler:  State iterated to %s" % state.epoch)