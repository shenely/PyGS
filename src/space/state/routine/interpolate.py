#!/usr/bin/env python2.7

"""Interpolation routines

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

#Internal libraries
from core import coroutine
from clock.epoch import EpochState
from .. import CartesianState
#
##################


##################
# Export section #
#
__all__ = ["hermite"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

HERMITE_SPLINE_00 = lambda t: 2 * t ** 3 - 3 * t ** 2 + 1 
HERMITE_SPLINE_10 = lambda t: t ** 3 - 2 * t ** 2 + t
HERMITE_SPLINE_01 = lambda t: - 2 * t ** 3 + 3 * t ** 2
HERMITE_SPLINE_11 = lambda t: t ** 3 - t ** 2
#
####################

@coroutine
def hermite(system,prev=None,next=None,istrue=None,isfalse=None):
    """Cubic Hermite Spline Interpolation"""
    
    assert isinstance(system,EpochState)
    assert isinstance(prev,CartesianState) or prev is None
    assert isinstance(next,CartesianState) or next is None
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    state,pipeline = None,None
    while True:
        state = yield state,pipeline
        
        assert isinstance(state,CartesianState) or state is None
        
        if state is not None:
            prev,next = state,prev
        
            if (prev is not None) and (next is not None):
                x0 = prev.epoch
                x1 = next.epoch
                dx = (x1 - x0).total_seconds()
                
                p0 = prev.position
                p1 = next.position
                
                m0 = prev.velocity * dx
                m1 = next.velocity * dx
            
        if (prev is not None) and (next is not None):
            x = system.epoch
            t = (x - x0).total_seconds() / dx
            
            h00 = HERMITE_SPLINE_00(t)
            h01 = HERMITE_SPLINE_01(t)
            h10 = HERMITE_SPLINE_10(t)
            h11 = HERMITE_SPLINE_11(t)
            
            p = h00 * p0 + h10 * m0 + h01 * p1 + h11 * m1
            m = (1 - t) * m0 + t * m1
            
            state = CartesianState(x,p,m / dx)
        
            logging.info("Interpolate.Hermite")
        else:
            state = None
    
        pipeline = istrue \
                   if (state is not None) \
                   else isfalse