#!/usr/bin/env python2.7

"""State objects

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 February 2013

Purpose:    
"""


##################
# Import section #
#
#Built-in libraries
from math import *
from datetime import datetime,time
import types

#External libraries
from numpy import matrix,dot,inner,cross,float64
from scipy.linalg import norm

#Internal libraries
from clock.epoch import EpochState
#
##################


##################
# Export section #
#
__all__ = ["InertialState",
           "KeplerianState",
           "GeographicState",
           "HorizontalState"]
#
##################


####################
# Constant section #
#
__version__ = "0.1"#current version [major.minor]

DEG_TO_RAD = pi / 180
RAD_TO_DEG = 180 / pi

EARTH_RADIUS = 6378
EARTH_GRAVITATION = 398600.4

EPOCH_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
#
####################


class InertialState(EpochState):
    def __init__(self,epoch,position,velocity,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(position,matrix)
        assert position.dtype.type is float64
        assert position.shape == (3,1)
        #assert norm(position) > EARTH_RADIUS
        
        assert isinstance(velocity,matrix)
        assert velocity.dtype.type is float64
        assert velocity.shape == (3,1)
        #assert velocity.T * velocity * norm(position) < 2 * EARTH_GRAVITATION
        
        self.position = position
        self.velocity = velocity
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"position")
        assert hasattr(kwargs,"velocity")
        
        return True
    
    @property
    def x(self):
        """Inertial X (read-only)"""
        return self.position[0,0]
    
    @property
    def y(self):
        """Inertial Y (read-only)"""
        return self.position[1,0]
    
    @property
    def z(self):
        """Inertial Z (read-only)"""
        return self.position[2,0]
    
    @property
    def u(self):
        """Inertial U (read-only)"""
        return self.velocity[0,0]
    
    @property
    def v(self):
        """Inertial V (read-only)"""
        return self.velocity[1,0]
    
    @property
    def w(self):
        """Inertial W (read-only)"""
        return self.velocity[2,0]
    
    @property
    def R(self):
        """Inertial Radius (read-only)"""
        return norm(self.position)
    
    @property
    def V(self):
        """Inertial U (read-only)"""
        return norm(self.velocity)
    
    @property
    def alpha(self):
        """Inertial Right Ascension (read-only)"""
        return atan2(self.position[1,0],self.position[0,0])
    
    @property
    def delta(self):
        """Inertial Declination (read-only)"""
        return asin(self.position[2,0] / self.R)
    
    @property
    def epsilon(self):
        """Inertial Specific Energy (read-only)"""
        return self.V ** 2 / 2 - EARTH_GRAVITATION / self.R
    
    @property
    def h(self):
        """Inertial Specific Angular Momentum (read-only)"""
        return cross(self.position,self.velocity)
    
    @property
    def e(self):
        """Inertial Eccentricity Vector (read-only)"""
        return cross(self.position,self.h) / EARTH_GRAVITATION - self.position / self.R


class KeplerianState(EpochState):
    def __init__(self,epoch,a,theta,e,omega,i,OMEGA,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(a,types.FloatType)
        assert a > EARTH_RADIUS
        assert isinstance(e,types.FloatType)
        if e < 0:
            e = - e
            omega += pi
        assert e < 1
        assert isinstance(i,types.FloatType)
        i %= 2 * pi
        if i < 0 or i >= pi:
            i -= pi
            omega += pi
        assert i < pi
        assert isinstance(theta,types.FloatType)
        theta %= 2 * pi
        assert isinstance(omega,types.FloatType)
        omega %= 2 * pi
        assert isinstance(OMEGA,types.FloatType)
        OMEGA %= 2 * pi
        
        self.a = a
        self.theta = theta
        self.e = e
        self.omega = omega
        self.i = i
        self.OMEGA = OMEGA
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"a")
        assert hasattr(kwargs,"theta")
        assert hasattr(kwargs,"e")
        assert hasattr(kwargs,"omega")
        assert hasattr(kwargs,"i")
        assert hasattr(kwargs,"OMEGA")
        
        return True
    
    @property
    def epsilon(self):
        """Keplerian Specific Energy (read-only)"""
        return - EARTH_GRAVITATION / self.a / 2
    
    @property
    def h(self):
        """Keplerian Specific Angular Momentum (read-only)"""
        return sqrt(EARTH_GRAVITATION * self.p)
    
    @property
    def r(self):
        """Keplerian Radius (read-only)"""
        return self.p / (1 + self.e * cos(self.theta))
    
    @property
    def p(self):
        """Keplerian Semi-latus Rectum (read-only)"""
        return self.a * (1 - self.e ** 2)
    
    @property
    def b(self):
        """Keplerian Semi-minor Axis (read-only)"""
        return self.a * sqrt(1 - self.e ** 2)
    
    @property
    def A(self):
        """Keplerian Apogee (read-only)"""
        return self.a * (1 + self.e)
    
    @property
    def P(self):
        """Keplerian Perigee (read-only)"""
        return self.a * (1 - self.e)
    
    @property
    def n(self):
        """Keplerian Mean Motion (read-only)"""
        return sqrt(EARTH_GRAVITATION / self.a ** 3)
    
    @property
    def T(self):
        """Keplerian Period (read-only)"""
        return 2 * pi * sqrt(self.a ** 3 / EARTH_GRAVITATION)
    
    @property
    def E(self):
        """Keplerian Eccentric Anomaly"""
        return 2 * atan2(sqrt(1 - self.e) * sin(self.theta / 2),
                         sqrt(1 + self.e) * cos(self.theta / 2))
    
    @property
    def M(self):
        """Keplerian Mean Anomaly"""
        return self.E - self.e * sin(self.E)
    
    @property
    def u(self):
        """Keplerian Argument of Latitude (read-only)"""
        return self.theta + self.omega
   

class GeographicState(EpochState):
    def __init__(self, epoch,arc,long,lat,*args,**kwargs):   
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(arc,types.FloatType)
        assert arc >= 0
        assert arc < 180
        assert isinstance(long,types.FloatType)
        long %= 360
        assert isinstance(lat,types.FloatType)
        assert abs(lat) <= 90
             
        self.arc = arc
        self.long = long
        self.lat = lat
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"arc")
        assert hasattr(kwargs,"long")
        assert hasattr(kwargs,"lat")
        
        return True

class HorizontalState(EpochState):
    def __init__(self,epoch,R,az,el,*args,**kwargs):
        EpochState.__init__(self,epoch,*args,**kwargs)
        
        assert isinstance(R,types.FloatType)
        assert abs(R) >= 0
        assert isinstance(az,types.FloatType)
        az %= 360
        assert isinstance(el,types.FloatType)
        assert abs(el) <= 90
             
        self.R = R
        self.az = az
        self.el = el
    
    @staticmethod
    def check(kwargs):
        assert EpochState.check(kwargs)
        assert hasattr(kwargs,"R")
        assert hasattr(kwargs,"az")
        assert hasattr(kwargs,"el")
        
        return True
