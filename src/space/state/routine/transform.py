#!/usr/bin/env python2.7

"""Transformation routines

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
from datetime import datetime
import functools
import logging
import types

#External libraries
from numpy import matrix,dot,cross,roots
from scipy.linalg import norm

#Internal libraries
from core import coroutine
from ...state import *
#
##################


##################
# Export section #
#
__all__ = ["identity",
           "cartesian2keplerian",
           "keplerian2cartesian",
           "cartesian2geographic",
           "geographic2horizontal"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

DEG_TO_RAD = pi / 180
RAD_TO_DEG = 180 / pi

EARTH_RADIUS = 6378.1
EARTH_GRAVITATION = 398600.4

JULIAN_DAY = 86400

J2000 = datetime(2000,1,1,12)

UNIT_VECTOR_X = matrix([1,0,0]).T
UNIT_VECTOR_Y = matrix([0,1,0]).T
UNIT_VECTOR_Z = matrix([0,0,1]).T

ROTATION_X_AXIS = lambda theta:matrix([[1,0,0],
                                       [0,cos(theta),-sin(theta)],
                                       [0,sin(theta),cos(theta)]])
ROTATION_Y_AXIS = lambda theta:matrix([[cos(theta),0,sin(theta)],
                                       [0,1,0],
                                       [-sin(theta),0,cos(theta)]])
ROTATION_Z_AXIS = lambda theta:matrix([[cos(theta),-sin(theta),0],
                                       [sin(theta),cos(theta),0],
                                       [0,0,1]])

functools.wraps(cos)
def cosd(x):
    return cos(DEG_TO_RAD * x)

functools.wraps(sin)
def sind(x):
    return sin(DEG_TO_RAD * x)

functools.wraps(tan)
def tand(x):
    return tan(DEG_TO_RAD * x)

functools.wraps(acos)
def acosd(x):
    return RAD_TO_DEG * acos(x)

functools.wraps(asin)
def asind(x):
    return RAD_TO_DEG * asin(x)

functools.wraps(atan2)
def atand2(y,x):
    return RAD_TO_DEG * atan2(y,x)
#
####################

@coroutine
def identity(pipeline):
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    while True:
        state = yield state,pipeline

        assert isinstance(state,BaseState)
        
        logging.info("Routine.Transform:  Identity")

@coroutine
def cartesian2keplerian(pipeline):
    """Cartesian State to Keplerian Elements Transform"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    while True:
        state = yield state,pipeline

        assert isinstance(state,CartesianState)

        t = state.epoch

        epsilon = state.epsilon
        a = - EARTH_GRAVITATION / epsilon / 2
        
        _h_ = state.h
        h = norm(_h_)
        
        _e_ = state.e
        e = norm(_h_)

        _N_ = cross(UNIT_VECTOR_Z,_h_)
        N = norm(_N_)

        i = acos(_h_[:,2] / h)
        theta = acos(dot(_e_,state.position) / e / state.r)
        omega = acos(dot(_N_,_e_) / N / e)
        OMEGA = acos(_N_[:,0] / N)

        if dot(state.position,state.velocity) < 0: theta = 2 * pi - theta
        if _e_[:,2] < 0:omega = 2 * pi - omega
        if _N_[:,1] < 0:OMEGA = 2 * pi - OMEGA

        state = KeplerianState(t,a,theta,e,omega,i,OMEGA)
        
        logging.info("Routine.Transform:  CartesianToKeplerian")

@coroutine
def keplerian2cartesian(pipeline):
    """Keplerian Elements to Cartesian State Transform"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    while True:
        state = yield state,pipeline
        
        assert isinstance(state,KeplerianState)

        R_OMEGA = ROTATION_Z_AXIS(state.OMEGA)
        R_i = ROTATION_X_AXIS(state.i)
        R_omega = ROTATION_Z_AXIS(state.omega)

        Q = R_OMEGA * R_i * R_omega

        r = state.r * matrix([cos(state.theta),
                              sin(state.theta),0]).T
        v = EARTH_GRAVITATION / state.h * matrix([- sin(state.theta),
                                                  state.e + cos(state.theta),0]).T
                                                  
        t = state.epoch
        r = Q * r
        v = Q * v

        state = CartesianState(t,r,v)
                
        logging.info("Routine.Transform:  KeplerianToCartesian")

@coroutine
def cartesian2geographic(pipeline):
    """Cartesian State to Geographic State Transform"""
    
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    while True:
        state = yield state,pipeline
        
        assert isinstance(state,CartesianState)
        
        t = state.epoch
        arc = acosd(EARTH_RADIUS / state.R)
        long = (RAD_TO_DEG * state.alpha +\
                360 * (t - J2000).total_seconds() / JULIAN_DAY) % 360
        lat = RAD_TO_DEG * state.delta

        state = GeographicState(t,arc,long,lat)
        
        logging.info("Routine.Transform:  CartesianToGeographic")

@coroutine
def geographic2horizontal(point,pipeline):
    """Geographic State to Horizontal State Transform"""
    
    assert isinstance(point,GeographicState)
    assert isinstance(pipeline,types.GeneratorType) or pipeline is None

    state = None
    while True:
        state = yield state,pipeline
        
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

        state = HorizontalState(t,az,el,r)
        
        logging.info("Routine.Transform:  GeographicToHorizontal")