#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

"""Transformation routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   28 July 2013

Provides routines for state transformation.

Classes:
identityTransfrom               -- Identity transform
InertialToKeplerianTransform    -- Inertial to Keplerian
KeplerianToInertialTransform    -- Keplerian to inertial
InertialToGeographicTransform   -- Inertial to geographic
GeographicToHorizontalTransform -- Geographic to horizontal

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-08    shenely         1.0         Initial revision
2013-07-28    shenely         1.1         Added time to geographic

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
from core.routine import ActionRoutine
from epoch import EpochState
from .. import *
#
##################


##################
# Export section #
#
__all__ = ["identityTransfrom",
           "InertialToKeplerianTransform",
           "KeplerianToInertialTransform",
           "InertialToGeographicTransform",
           "GeographicToHorizontalTransform"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

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

#Rotation matrices
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


class TransformAction(ActionRoutine):pass

class IdentityTransform(TransformAction):
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
    
    name = "Transform.Identity"
    
    def _execute(self,message):
        logging.info("{0}:  Transforming from self".\
                     format(self.name))
        
        #
        
        logging.info("{0}:  Transformed to self".\
                     format(self.name))
                     
        return message

class InertialToKeplerianTransform(TransformAction):
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
    
    name = "Transform.InertialToKeplerian"
    
    def _execute(self,message):
        assert isinstance(message,InertialState)

        logging.info("{0}:  Transforming from inertial".\
                     format(self.name))
        
        t = message.epoch

        #orbital elements
        epsilon = message.epsilon
        a = - EARTH_GRAVITATION / epsilon / 2
        
        _h_ = message.h
        h = norm(_h_)
        
        _e_ = message.e
        e = norm(_e_)

        _N_ = cross(UNIT_VECTOR_Z,_h_)
        N = norm(_N_)

        i = acos(_h_[:,2] / h)
        theta = acos(dot(_e_,message.position) / e / message.R)
        omega = acos(dot(_N_,_e_) / N / e)
        OMEGA = acos(_N_[:,0] / N)

        #quadrant correction
        if dot(message.position,message.velocity) < 0: theta = 2 * pi - theta
        if _e_[:,2] < 0:omega = 2 * pi - omega
        if _N_[:,1] < 0:OMEGA = 2 * pi - OMEGA

        message = KeplerianState(t,a,theta,e,omega,i,OMEGA)
        
        logging.info("{0}:  Transformed to Keplerian".\
                     format(self.name))
        
        return message

class KeplerianToInertialTransform(TransformAction):
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
    
    name = "Transform.KeplerianToInertial"
    
    def _execute(self,message):
        assert isinstance(message,KeplerianState)
        
        logging.info("{0}:  Transforming from Keplerian".\
                     format(self.name))

        #rotation matrices
        R_OMEGA = ROTATION_Z_AXIS(message.OMEGA)
        R_i = ROTATION_X_AXIS(message.i)
        R_omega = ROTATION_Z_AXIS(message.omega)

        Q = R_OMEGA * R_i * R_omega

        #state vectors
        r = message.r * matrix([cos(message.theta),
                                sin(message.theta),0]).T
        v = EARTH_GRAVITATION / message.h *\
            matrix([- sin(message.theta),
                    message.e + cos(message.theta),0]).T

        #apply rotations
        t = message.epoch
        r = Q * r
        v = Q * v

        message = InertialState(t,r,v)
        
        logging.info("{0}:  Transformed to inertial".\
                     format(self.name))
        
        return message

class InertialToGeographicTransform(TransformAction):
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
    
    name = "Transform.InertialToGeographic"
    
    def _execute(self,message):
        assert isinstance(message,InertialState)

        logging.info("{0}:  Transforming from inertial".\
                     format(self.name))
        
        t = message.epoch
        arc = acosd(EARTH_RADIUS / message.R)
        long = (RAD_TO_DEG * message.alpha % 360 +\
                360 * (t - J2000).total_seconds() / JULIAN_DAY) % 360
        lat = RAD_TO_DEG * message.delta

        message = GeographicState(t,arc,long,lat)
        
        logging.info("{0}:  Transformed to geographic".\
                     format(self.name))
        
        return message

class GeographicToHorizontalTransform(TransformAction):
    """Story:  Geographic to horizontal
    
    IN ORDER TO determine the azimuth and elevation of a spacecraft
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
    
    name = "Transform.GeographicToHorizontal"
    
    def __init__(self,state):
        assert isinstance(state,GeographicState)
        
        TransformAction.__init__(self)
        
        self.state = state

    def _execute(self,message):
        assert isinstance(message,GeographicState)

        logging.info("{0}:  Transforming from geographic".\
                     format(self.name))
        
        t = message.epoch
        az = atan2(sind(message.long - self.state.long),
                   cosd(self.state.lat) * tand(message.lat) -\
                   sind(self.state.lat) * cosd(message.long -\
                                               self.state.long))
        el = asin(cosd(self.state.lat) * cosd(message.lat) *\
                  cosd(message.long - self.state.long) -\
                  sind(self.state.lat) * sind(message.lat))
        r = max(roots([1 / EARTH_RADIUS,
                       2 * sin(el),
                       EARTH_RADIUS * (1 / cos(self.state.arc) ** 2 -\
                                       1 / cos(message.arc) ** 2)]))

        message = HorizontalState(t,r,az,el)
        
        logging.info("{0}:  Transformed to horizontal".\
                     format(self.name))

        return message