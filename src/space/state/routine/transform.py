#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Transformation routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 February 2013

Provides routines for state transformation.

Functions:
identity              -- Identity transform
inertial2keplerian    -- Inertial to Keplerian
keplerian2inertial    -- Keplerian to inertial
inertial2geographic   -- Inertial to geographic
geographic2horizontal -- Geographic to horizontal

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-06    shenely         1.0         Promoted to version 1.0
2013-02-10                                Using InertialState now

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
__all__ = ["identity",
           "inertial2keplerian",
           "keplerian2inertial",
           "inertial2geographic",
           "geographic2horizontal"]
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
def identity(pipeline=None):
    """Story:  Identity transform
    
    IN ORDER TO have the input equal output
    AS A generic segment
    I WANT TO perform an identity transformation
    
    """
    
    """Specification:  Identity transform
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a state is received from upstream
    THEN the state SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    
    logging.debug("Transform.Identity:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Transform.Identity:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,EpochState)
            
            logging.info("Transform.Identity")

@coroutine
def inertial2keplerian(pipeline=None):
    """Story:  Inertial to Keplerian
    
    IN ORDER TO determine the orbital elements of a spacecraft
    AS A generic segment
    I WANT TO convert inertial coordinates into Keplerian elements
    
    """
    
    u"""Specification:  Inertial to Keplerian
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a inertial state is received from upstream
    THEN the state SHALL be converted to orbital elements:
                a=-μ/ε/2
                e=|e|
                cos(i)=h[z]/|h|
                cos(θ)=(e/|e|)∙(r/|r|)
                cos(ω)=(e/|e|)∙N
                cos(Ω)=N[z]
        AND the state SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    
    logging.debug("Transform.InertialToKeplerian:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Transform.InertialToKeplerian:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,InertialState)

            t = state.epoch

            #orbital elements
            epsilon = state.epsilon
            a = - EARTH_GRAVITATION / epsilon / 2
            
            _h_ = state.h
            h = norm(_h_)
            
            _e_ = state.e
            e = norm(_e_)

            _N_ = cross(UNIT_VECTOR_Z,_h_)
            N = norm(_N_)

            i = acos(_h_[:,2] / h)
            theta = acos(dot(_e_,state.position) / e / state.R)
            omega = acos(dot(_N_,_e_) / N / e)
            OMEGA = acos(_N_[:,0] / N)

            #quadrant correction
            if dot(state.position,state.velocity) < 0: theta = 2 * pi - theta
            if _e_[:,2] < 0:omega = 2 * pi - omega
            if _N_[:,1] < 0:OMEGA = 2 * pi - OMEGA

            state = KeplerianState(t,a,theta,e,omega,i,OMEGA)
            
            logging.info("Transform.InertialToKeplerian")

@coroutine
def keplerian2inertial(pipeline=None):
    """Story:  Keplerian to Inertial
    
    IN ORDER TO determine the orbital elements of a spacecraft
    AS A generic segment
    I WANT TO convert inertial coordinates into Keplerian elements
    
    """
    
    u"""Specification:  Keplerian to Inertial
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a Keplerian state is received from upstream
    THEN the state SHALL be converted to inertial coordinates:
                    [cos(θ)]
                r=r*[sin(θ)]
                    [0     ]
                   μ  [-sin(θ) ]
                v=---*[e+cos(θ)]
                  |h| [0       ]
                r=R[z](Ω)*R[x](i)*R[z](ω)*r
                v=R[z](Ω)*R[x](i)*R[z](ω)*v
        AND the state SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    
    logging.debug("Transform.KeplerianToInertial:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Transform.KeplerianToInertial:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:
            #input validation
            assert isinstance(state,KeplerianState)

            #rotation matrices
            R_OMEGA = ROTATION_Z_AXIS(state.OMEGA)
            R_i = ROTATION_X_AXIS(state.i)
            R_omega = ROTATION_Z_AXIS(state.omega)

            Q = R_OMEGA * R_i * R_omega

            #state vectors
            r = state.r * matrix([cos(state.theta),
                                  sin(state.theta),0]).T
            v = EARTH_GRAVITATION / state.h *\
                matrix([- sin(state.theta),
                        state.e + cos(state.theta),0]).T

            #apply rotations
            t = state.epoch
            r = Q * r
            v = Q * v

            state = InertialState(t,r,v)
                    
            logging.info("Transform.KeplerianToInertial")

@coroutine
def inertial2geographic(pipeline=None):
    """Story:  Inertial to geographic
    
    IN ORDER TO determine the latitude and longitude of a spacecraft
    AS A generic segment
    I WANT TO convert inertial coordinates into geographic coordinates
    
    """
    
    u"""Specification:  Inertial to geographic
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a inertial state is received from upstream
    THEN the state SHALL be converted to geographic coordinates:
                cos(σ)=R[e]/R
                λ=α+(t-J2000.0)/86400
                φ=δ
        AND all coordinates SHALL be converted to degrees
        AND the state SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    
    logging.debug("Transform.InertialToGeographic:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Transform.InertialToGeographic:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else:        
            #input validation
            assert isinstance(state,InertialState)
            
            t = state.epoch
            arc = acosd(EARTH_RADIUS / state.R)
            long = (RAD_TO_DEG * state.alpha +\
                    360 * (t - J2000).total_seconds() / JULIAN_DAY) % 360
            lat = RAD_TO_DEG * state.delta

            state = GeographicState(t,arc,long,lat)
            
            logging.info("Transform.InertialToGeographic")

@coroutine
def geographic2horizontal(point,pipeline=None):
    """Story:  Geographic to horizontal
    
    IN ORDER TO determine the azimuth and eleveation of a spacecraft
    AS A generic segment
    I WANT TO convert geographic coordinates into horizontal coordinates
    
    """
    
    u"""Specification:  Geographic to horizontal
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream state received
    WHEN a inertial state is received from upstream
    THEN all coordinates SHALL be converted to radians
        AND the state SHALL be converted to geographic coordinates:
                tan(A)=sin(λ1-λ0)/(cos(φ0)tan(φ1)-sin(φ0)cos(λ1-λ0))
                sin(a)=cos(φ0)cos(φ1)cos(λ1-λ0)-sin(φ0)sin(φ1)
                r²+2*sin(a)*R[e]*r+R[e]²*(1/cos²(σ0)-1/cos²(σ1))=0
        AND all coordinates SHALL be converted to degrees
        AND the state SHALL be sent downstream
    
    """
    
    #configuration validation
    assert isinstance(point,GeographicState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    
    logging.debug("Transform.GeographicToHorizontal:  Starting")
    while True:
        try:
            state = yield state,pipeline
        except GeneratorExit:
            logging.warn("Transform.GeographicToHorizontal:  Stopping")
            
            #close downstream routine (if it exists)
            pipeline.close() if pipeline is not None else None
            
            return
        else: 
            #input validation
            assert isinstance(state,GeographicState)
            
            t = state.epoch
            az = atan2(sind(state.long - point.long),
                       cosd(point.lat) * tand(state.lat) -\
                       sind(point.lat) * cosd(state.long - point.long))
            el = asin(cosd(point.lat) * cosd(state.lat) * cosd(state.long - point.long) -\
                      sind(point.lat) * sind(state.lat))
            r = max(roots([1 / EARTH_RADIUS,
                           2 * sin(el),
                           EARTH_RADIUS * (1 / cos(point.arc) ** 2 -\
                                           1 / cos(state.arc) ** 2)]))

            state = HorizontalState(t,r,az,el)
            
            logging.info("Transform.GeographicToHorizontal")
