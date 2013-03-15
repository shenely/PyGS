#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Orbit routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 March 2013

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
2013-03-15    shenely         1.0         Intial revision

"""


##################
# Import section #
#
#Built-in libraries
from math import *
from datetime import datetime
import functools
import logging
import types

#External libraries
from numpy import matrix,dot,cross,roots
from scipy.linalg import norm
from bson.tz_util import utc

#Internal libraries
from core import coroutine
from clock.epoch import EpochState
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

DEG_TO_RAD = pi / 180#Degrees to radians
RAD_TO_DEG = 180 / pi#Radians to degrees

#Earth parameters
EARTH_RADIUS = 6378.1
EARTH_GRAVITATION = 398600.4

JULIAN_DAY = 86400#Length of Julian day (in seconds)

J2000 = datetime(2000,1,1,12,tzinfo=utc)#Julian epoch (2000-01-01T12:00:00Z)

#Unit vectors
UNIT_VECTOR_X = matrix([1,0,0]).T
UNIT_VECTOR_Y = matrix([0,1,0]).T
UNIT_VECTOR_Z = matrix([0,0,1]).T

#Rotiation matrices
ROTATION_X_AXIS = lambda theta:matrix([[1,0,0],
                                       [0,cos(theta),-sin(theta)],
                                       [0,sin(theta),cos(theta)]])
ROTATION_Y_AXIS = lambda theta:matrix([[cos(theta),0,sin(theta)],
                                       [0,1,0],
                                       [-sin(theta),0,cos(theta)]])
ROTATION_Z_AXIS = lambda theta:matrix([[cos(theta),-sin(theta),0],
                                       [sin(theta),cos(theta),0],
                                       [0,0,1]])

#Wrapper functions for angles in degrees
@functools.wraps(cos)
def cosd(x):return cos(DEG_TO_RAD * x)

@functools.wraps(sin)
def sind(x):return sin(DEG_TO_RAD * x)

@functools.wraps(tan)
def tand(x):return tan(DEG_TO_RAD * x)

@functools.wraps(acos)
def acosd(x):return RAD_TO_DEG * acos(x)

@functools.wraps(asin)
def asind(x):return RAD_TO_DEG * asin(x)

@functools.wraps(atan2)
def atand2(y,x):return RAD_TO_DEG * atan2(y,x)
#
####################


@coroutine
def perigee(threshold,pipeline=None):
    """Story:  Orbit perigee
    
    IN ORDER TO perform analyses at perigee
    AS A generic segment
    I WANT TO be notified when perigee is achieved
    
    """
    
    """Specification:  Orbit perigee
    
    GIVEN a threshold
    AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND the following criteria are true:
            r∙v≈0
            μ<|r|v²
    THEN the state SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    flag = False
    
    logging.debug("Orbit.Perigee:  Starting")
    while True:
        try:
            state = yield (state if flag else None),pipeline
        except GeneratorExit:
            logging.warn("Orbit.Perigee:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,CartesianState)
            
            flag = (abs(state.position.T * state.velocity) < threshold) and\
                   (state.R * state.V ** 2 > EARTH_GRAVITATION)
            
            logging.info("Orbit.Perigee:  %s" % flag)

@coroutine
def apogee(threshold,pipeline=None):
    """Story:  Orbit apogee
    
    IN ORDER TO perform analyses at apogee
    AS A generic segment
    I WANT TO be notified when apogee is achieved
    
    """
    
    """Specification:  Orbit apogee
    
    GIVEN a threshold
    AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    AND the following criteria are true:
            r∙v≈0
            μ>|r|v²
    THEN the state SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    flag = False
    
    logging.debug("Orbit.Apogee:  Starting")
    while True:
        try:
            state = yield (state if flag else None),pipeline
        except GeneratorExit:
            logging.warn("Orbit.Apogee:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,CartesianState)
            
            flag = (abs(state.position.T * state.velocity) < threshold) and\
                   (state.R * state.V ** 2 < EARTH_GRAVITATION)
            
            logging.info("Orbit.Apogee:  %s" % flag)
