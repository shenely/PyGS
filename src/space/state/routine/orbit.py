#!/usr/bin/env python2.7

"""Orbit routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   20 March 2013

Provides routines for orbit events.

Functions:
perigee         -- Perigee
apogee          -- Apogee
ascending_node  -- Ascending node
descending_node -- Descending node
northern_pole   -- Northern pole
southern_pole   -- Southern pole

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-03-15    shenely         1.0         Initial revision
2013-03-20                    1.1         Completed all routines


"""


##################
# Import section #
#
#Built-in libraries
from math import *
from datetime import datetime,timedelta
import logging
import types

#External libraries
from numpy import matrix,poly1d,where
from bson.tz_util import utc

#Internal libraries
from core import coroutine
from ...state import *
#
##################


##################
# Export section #
#
__all__ = ["perigee",
           "apogee",
           "ascending_node",
           "descending_node",
           "northern_pole",
           "southern_pole"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]

#Earth parameters
EARTH_GRAVITATION = 398600.4

HERMITE_POLYNOMIAL = lambda p0,m0,p1,m1:\
                     poly1d([2 * p0 + m0 - 2 * p1 + m1,
                             - 3 * p0 - 2 * m0 + 3 * p1 - m1,
                             m0,
                             p0])
HERMITE_DERIVATIVE = lambda p0,m0,p1,m1:\
                     poly1d([6 * p0 + 3 * m0 - 6 * p1 + 3 * m1,
                             - 6 * p0 - 4 * m0 + 6 * p1 - 2 * m1,
                             m0])

HERMITE_SPLINE_00 = lambda t: 2 * t ** 3 - 3 * t ** 2 + 1 
HERMITE_SPLINE_10 = lambda t: t ** 3 - 2 * t ** 2 + t
HERMITE_SPLINE_01 = lambda t: - 2 * t ** 3 + 3 * t ** 2
HERMITE_SPLINE_11 = lambda t: t ** 3 - t ** 2
#
####################


@coroutine
def perigee(istrue=None,isfalse=None):
    """Story:  Orbit perigee
    
    IN ORDER TO perform analyses at perigee
    AS A generic segment
    I WANT TO be notified when perigee is achieved
    
    """
    
    """Specification:  Orbit perigee
    
    GIVEN a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND  the following criterion is true for the state:
            r∙v>0
    AND the following criterion is true for the previous state:
            r∙v<0
    THEN the next state SHALL be defined as the state
        AND the state SHALL be determined where the following criterion
            is true:
                r∙v=0
        AND the state SHALL be sent downstream
    
    Scenario 2:  Criterion not achieved
    WHEN a state is received from upstream
    AND  the following criterion is false for the state:
            r∙v>0
    THEN the next state SHALL be defined as the state
        AND the previous state SHALL be defined as the state
        AND a blank message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    p0 = float("inf")
    p1 = float("-inf")

    state = None
    pipeline = None
    
    logging.debug("Orbit.Perigee:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Orbit.Perigee:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,InertialState)
            
            next = state
            
            p1 = (next.position.T * next.velocity)[0,0]
            
            if (p0 <= 0 and p1 >= 0):
                x0 = prev.epoch
                x1 = next.epoch
                dx = (x1 - x0).total_seconds()
                
                m0 = - EARTH_GRAVITATION / prev.R ** 2 * dx
                m1 = - EARTH_GRAVITATION / next.R ** 2 * dx
                
                p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
                m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
                
                r = p.r
                t = r[where((r > 0) & (r < 1))][0]
                x = x0 + timedelta(seconds = t * dx)
                
                P0 = prev.position
                P1 = next.position
                
                M0 = prev.velocity * dx
                M1 = next.velocity * dx
                
                h00 = HERMITE_SPLINE_00(t)
                h01 = HERMITE_SPLINE_01(t)
                h10 = HERMITE_SPLINE_10(t)
                h11 = HERMITE_SPLINE_11(t)
                
                P = h00 * P0 + h10 * M0 + h01 * P1 + h11 * M1
                M = (1 - t) * M0 + t * M1#FIXME:  doesn't use spline
                
                state = InertialState(x,P,M / dx)
                
                logging.info("Orbit.Perigee:  Achieved at %s" % state.epoch)
            else:
                state = None
                
            prev = next
            p0 = p1
        
            pipeline = istrue \
                       if (state is not None) \
                       else isfalse

@coroutine
def apogee(istrue=None,isfalse=None):
    """Story:  Orbit apogee
    
    IN ORDER TO perform analyses at apogee
    AS A generic segment
    I WANT TO be notified when apogee is achieved
    
    """
    
    """Specification:  Orbit apogee
    
    GIVEN a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND  the following criterion is true for the state:
            r∙v<0
    AND the following criterion is true for the previous state:
            r∙v>0
    THEN the next state SHALL be defined as the state
        AND the state SHALL be determined where the following criterion
            is true:
                r∙v=0
        AND the state SHALL be sent downstream
    
    Scenario 2:  Criterion not achieved
    WHEN a state is received from upstream
    AND  the following criterion is false for the state:
            r∙v<0
    THEN the next state SHALL be defined as the state
        AND the previous state SHALL be defined as the state
        AND a blank message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    p0 = float("-inf")
    p1 = float("inf")

    state = None
    pipeline = None
    
    logging.debug("Orbit.Apogee:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Orbit.Apogee:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,InertialState)
            
            next = state
            
            p1 = (next.position.T * next.velocity)[0,0]
            
            if (p0 >= 0 and p1 <= 0):
                x0 = prev.epoch
                x1 = next.epoch
                dx = (x1 - x0).total_seconds()
                
                m0 = - EARTH_GRAVITATION / prev.R ** 2 * dx
                m1 = - EARTH_GRAVITATION / next.R ** 2 * dx
                
                p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
                m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
                
                r = p.r
                t = r[where((r > 0) & (r < 1))][0]
                x = x0 + timedelta(seconds = t * dx)
                
                P0 = prev.position
                P1 = next.position
                
                M0 = prev.velocity * dx
                M1 = next.velocity * dx
                
                h00 = HERMITE_SPLINE_00(t)
                h01 = HERMITE_SPLINE_01(t)
                h10 = HERMITE_SPLINE_10(t)
                h11 = HERMITE_SPLINE_11(t)
                
                P = h00 * P0 + h10 * M0 + h01 * P1 + h11 * M1
                M = (1 - t) * M0 + t * M1#FIXME:  doesn't use spline
                
                state = InertialState(x,P,M / dx)
                
                logging.info("Orbit.Apogee:  Achieved at %s" % state.epoch)
            else:
                state = None
                
            prev = next
            p0 = p1
        
            pipeline = istrue \
                       if (state is not None) \
                       else isfalse

@coroutine
def descending_node(istrue=None,isfalse=None):
    """Story:  Orbit descending node
    
    IN ORDER TO perform analyses at the descending node
    AS A generic segment
    I WANT TO be notified when descending node is reached
    
    """
    
    """Specification:  Orbit descending node
    
    GIVEN a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND  the following criterion is true for the state:
            r[z]<0
    AND the following criterion is true for the previous state:
            r[z]>0
    THEN the next state SHALL be defined as the state
        AND the state SHALL be determined where the following criterion
            is true:
                r[z]=0
        AND the state SHALL be sent downstream
    
    Scenario 2:  Criterion not achieved
    WHEN a state is received from upstream
    AND  the following criterion is false for the state:
            r[z]<0
    THEN the next state SHALL be defined as the state
        AND the previous state SHALL be defined as the state
        AND a blank message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    p0 = float("-inf")
    p1 = float("inf")

    state = None
    pipeline = None
    
    logging.debug("Orbit.Node.Descending:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Orbit.Node.Descending:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,InertialState)
            
            next = state
            
            p1 = next.z
            
            if (p0 >= 0 and p1 <= 0):
                x0 = prev.epoch
                x1 = next.epoch
                dx = (x1 - x0).total_seconds()
                
                m0 = prev.w * dx
                m1 = next.w * dx
                
                p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
                m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
                
                r = p.r
                t = r[where((r > 0) & (r < 1))][0]
                x = x0 + timedelta(seconds = t * dx)
                
                P0 = prev.position
                P1 = next.position
                
                M0 = prev.velocity * dx
                M1 = next.velocity * dx
                
                h00 = HERMITE_SPLINE_00(t)
                h01 = HERMITE_SPLINE_01(t)
                h10 = HERMITE_SPLINE_10(t)
                h11 = HERMITE_SPLINE_11(t)
                
                P = h00 * P0 + h10 * M0 + h01 * P1 + h11 * M1
                M = (1 - t) * M0 + t * M1#FIXME:  doesn't use spline
                
                state = InertialState(x,P,M / dx)
                
                logging.info("Orbit.Node.Descending:  Achieved at %s" % state.epoch)
            else:
                state = None
                
            prev = next
            p0 = p1
        
            pipeline = istrue \
                       if (state is not None) \
                       else isfalse

@coroutine
def ascending_node(istrue=None,isfalse=None):
    """Story:  Orbit ascending node
    
    IN ORDER TO perform analyses at the ascending node
    AS A generic segment
    I WANT TO be notified when ascending node is reached
    
    """
    
    """Specification:  Orbit ascending node
    
    GIVEN a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND  the following criterion is true for the state:
            r[z]>0
    AND the following criterion is true for the previous state:
            r[z]<0
    THEN the next state SHALL be defined as the state
        AND the state SHALL be determined where the following criterion
            is true:
                r[z]=0
        AND the state SHALL be sent downstream
    
    Scenario 2:  Criterion not achieved
    WHEN a state is received from upstream
    AND  the following criterion is false for the state:
            r[z]>0
    THEN the next state SHALL be defined as the state
        AND the previous state SHALL be defined as the state
        AND a blank message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    p0 = float("inf")
    p1 = float("-inf")

    state = None
    pipeline = None
    
    logging.debug("Orbit.Node.Ascending:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Orbit.Node.Ascending:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,InertialState)
            
            next = state
            
            p1 = next.z
            
            if (p0 <= 0 and p1 >= 0):
                x0 = prev.epoch
                x1 = next.epoch
                dx = (x1 - x0).total_seconds()
                
                m0 = prev.w * dx
                m1 = next.w * dx
                
                p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
                m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
                
                r = p.r
                t = r[where((r > 0) & (r < 1))][0]
                x = x0 + timedelta(seconds = t * dx)
                
                P0 = prev.position
                P1 = next.position
                
                M0 = prev.velocity * dx
                M1 = next.velocity * dx
                
                h00 = HERMITE_SPLINE_00(t)
                h01 = HERMITE_SPLINE_01(t)
                h10 = HERMITE_SPLINE_10(t)
                h11 = HERMITE_SPLINE_11(t)
                
                P = h00 * P0 + h10 * M0 + h01 * P1 + h11 * M1
                M = (1 - t) * M0 + t * M1#FIXME:  doesn't use spline
                
                state = InertialState(x,P,M / dx)
                
                logging.info("Orbit.Node.Ascending:  Achieved at %s" % state.epoch)
            else:
                state = None
                
            prev = next
            p0 = p1
        
            pipeline = istrue \
                       if (state is not None) \
                       else isfalse


@coroutine
def northern_pole(istrue=None,isfalse=None):
    """Story:  Orbit northern pole
    
    IN ORDER TO perform analyses at the northern pole
    AS A generic segment
    I WANT TO be notified when northern pole is reached
    
    """
    
    """Specification:  Orbit northern pole
    
    GIVEN a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND  the following criterion is true for the state:
            v[z]<0
    AND the following criterion is true for the previous state:
            v[z]>0
    THEN the next state SHALL be defined as the state
        AND the state SHALL be determined where the following criterion
            is true:
                v[z]=0
        AND the state SHALL be sent downstream
    
    Scenario 2:  Criterion not achieved
    WHEN a state is received from upstream
    AND  the following criterion is false for the state:
            v[z]<0
    THEN the next state SHALL be defined as the state
        AND the previous state SHALL be defined as the state
        AND a blank message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    p0 = float("-inf")
    p1 = float("inf")

    state = None
    pipeline = None
    
    logging.debug("Orbit.Pole.Northern:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Orbit.Pole.Northern:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,InertialState)
            
            next = state
            
            p1 = next.w
            
            if (p0 >= 0 and p1 <= 0):
                x0 = prev.epoch
                x1 = next.epoch
                dx = (x1 - x0).total_seconds()
                
                m0 = - EARTH_GRAVITATION * prev.z / prev.R ** 3 * dx
                m1 = - EARTH_GRAVITATION * next.z / next.R ** 3 * dx
                
                p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
                m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
                
                r = p.r
                t = r[where((r > 0) & (r < 1))][0]
                x = x0 + timedelta(seconds = t * dx)
                
                P0 = prev.position
                P1 = next.position
                
                M0 = prev.velocity * dx
                M1 = next.velocity * dx
                
                h00 = HERMITE_SPLINE_00(t)
                h01 = HERMITE_SPLINE_01(t)
                h10 = HERMITE_SPLINE_10(t)
                h11 = HERMITE_SPLINE_11(t)
                
                P = h00 * P0 + h10 * M0 + h01 * P1 + h11 * M1
                M = (1 - t) * M0 + t * M1#FIXME:  doesn't use spline
                
                state = InertialState(x,P,M / dx)
                
                logging.info("Orbit.Pole.Northern:  Achieved at %s" % state.epoch)
            else:
                state = None
                
            prev = next
            p0 = p1
        
            pipeline = istrue \
                       if (state is not None) \
                       else isfalse


@coroutine
def southern_pole(istrue=None,isfalse=None):
    """Story:  Orbit southern pole
    
    IN ORDER TO perform analyses at the southern pole
    AS A generic segment
    I WANT TO be notified when southern pole is reached
    
    """
    
    """Specification:  Orbit southern pole
    
    GIVEN a true downstream pipeline (default null)
        AND a false downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND  the following criterion is true for the state:
            v[z]>0
    AND the following criterion is true for the previous state:
            v[z]<0
    THEN the next state SHALL be defined as the state
        AND the state SHALL be determined where the following criterion
            is true:
                v[z]=0
        AND the state SHALL be sent downstream
    
    Scenario 2:  Criterion not achieved
    WHEN a state is received from upstream
    AND  the following criterion is false for the state:
            v[z]>0
    THEN the next state SHALL be defined as the state
        AND the previous state SHALL be defined as the state
        AND a blank message SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(istrue,types.GeneratorType) or istrue is None
    assert isinstance(isfalse,types.GeneratorType) or isfalse is None
    
    p0 = float("inf")
    p1 = float("-inf")

    state = None
    pipeline = None
    
    logging.debug("Orbit.Pole.Southern:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Orbit.Pole.Southern:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,InertialState)
            
            next = state
            
            p1 = next.w
            
            if (p0 <= 0 and p1 >= 0):
                x0 = prev.epoch
                x1 = next.epoch
                dx = (x1 - x0).total_seconds()
                
                m0 = - EARTH_GRAVITATION * prev.z / prev.R ** 3 * dx
                m1 = - EARTH_GRAVITATION * next.z / next.R ** 3 * dx
                
                p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
                m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
                
                r = p.r
                t = r[where((r > 0) & (r < 1))][0]
                x = x0 + timedelta(seconds = t * dx)
                
                P0 = prev.position
                P1 = next.position
                
                M0 = prev.velocity * dx
                M1 = next.velocity * dx
                
                h00 = HERMITE_SPLINE_00(t)
                h01 = HERMITE_SPLINE_01(t)
                h10 = HERMITE_SPLINE_10(t)
                h11 = HERMITE_SPLINE_11(t)
                
                P = h00 * P0 + h10 * M0 + h01 * P1 + h11 * M1
                M = (1 - t) * M0 + t * M1#FIXME:  doesn't use spline
                
                state = InertialState(x,P,M / dx)
                
                logging.info("Orbit.Pole.Southern:  Achieved at %s" % state.epoch)
            else:
                state = None
                
            prev = next
            p0 = p1
        
            pipeline = istrue \
                       if (state is not None) \
                       else isfalse