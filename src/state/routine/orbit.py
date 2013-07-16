#!/usr/bin/env python2.7

"""Orbit routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   15 July 2013

Provides routines for orbit events.

Functions:
OrbitPerigee        -- Perigee
OrbitApogee         -- Apogee
OrbitAscendingNode  -- Ascending node
OrbitDescendingNode -- Descending node
OrbitNorthernPole   -- Northern pole
OrbitSouthernPole   -- Southern pole

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-07-12    shenely         1.0         Initial revision
2013-07-15    shenely         1.1         Changed to events


"""


##################
# Import section #
#
#Built-in libraries
from datetime import timedelta
import logging

#External libraries
from numpy import poly1d,where

#Internal libraries
from core.routine import EventRoutine
from .. import InertialState
#
##################


##################
# Export section #
#
__all__ = ["OrbitPerigee",
           "OrbitApogee",
           "OrbitAscendingNode",
           "OrbitDescendingNode",
           "OrbitNorthernPole",
           "OrbitSouthernPole"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]

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
#
####################


class OrbitEvent(EventRoutine):pass

class OrbitPerigee(OrbitEvent):
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
    
    name = "Orbit.Perigee"
    
    def _occur(self,message):
        assert isinstance(message,InertialState)
        
        self.prev = self.next
        self.next = message
        
        p0 = (self.prev.position.T * self.prev.velocity)[0,0]
        p1 = (self.next.position.T * self.next.velocity)[0,0]
            
        if (p0 <= 0 and p1 >= 0):
            x0 = self.prev.epoch
            x1 = self.next.epoch
            dx = (x1 - x0).total_seconds()
            
            m0 = - EARTH_GRAVITATION / self.prev.R * dx
            m1 = - EARTH_GRAVITATION / self.next.R * dx
            
            p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
            #m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
            
            r = p.r
            t = r[where((r > 0) & (r < 1))][0]
            
            epoch = x0 + timedelta(seconds = t * dx)
        
            logging.info("{0}:  Achieved at {1}".\
                         format(self.name,epoch))
        
            return epoch

class OrbitApogee(OrbitEvent):
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
    
    name = "Orbit.Apogee"
    
    def _occur(self,message):
        assert isinstance(message,InertialState)
        
        self.prev = self.next
        self.next = message
        
        p0 = (self.prev.position.T * self.prev.velocity)[0,0]
        p1 = (self.next.position.T * self.next.velocity)[0,0]
            
        if (p0 >= 0 and p1 <= 0):
            x0 = self.prev.epoch
            x1 = self.next.epoch
            dx = (x1 - x0).total_seconds()
            
            m0 = - EARTH_GRAVITATION / self.prev.R * dx
            m1 = - EARTH_GRAVITATION / self.next.R * dx
            
            p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
            #m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
            
            r = p.r
            t = r[where((r > 0) & (r < 1))][0]
            
            epoch = x0 + timedelta(seconds = t * dx)
        
            logging.info("{0}:  Achieved at {1}".\
                         format(self.name,epoch))
        
            return epoch

class OrbitAscendingNode(OrbitEvent):
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
    
    name = "Orbit.AscendingNode"
    
    def _occur(self,message):
        assert isinstance(message,InertialState)
        
        self.prev = self.next
        self.next = message
        
        p0 = self.prev.z
        p1 = self.next.z
            
        if (p0 <= 0 and p1 >= 0):
            x0 = self.prev.epoch
            x1 = self.next.epoch
            dx = (x1 - x0).total_seconds()
            
            m0 = self.prev.w * dx
            m1 = self.next.w * dx
            
            p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
            #m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
            
            r = p.r
            t = r[where((r > 0) & (r < 1))][0]
            
            epoch = x0 + timedelta(seconds = t * dx)
        
            logging.info("{0}:  Achieved at {1}".\
                         format(self.name,epoch))
        
            return epoch

class OrbitDescendingNode(OrbitEvent):
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
    
    name = "Orbit.DescendingNode"
    
    def _occur(self,message):
        assert isinstance(message,InertialState)
        
        self.prev = self.next
        self.next = message
        
        p0 = self.prev.z
        p1 = self.next.z
            
        if (p0 >= 0 and p1 <= 0):
            x0 = self.prev.epoch
            x1 = self.next.epoch
            dx = (x1 - x0).total_seconds()
            
            m0 = self.prev.w * dx
            m1 = self.next.w * dx
            
            p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
            #m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
            
            r = p.r
            t = r[where((r > 0) & (r < 1))][0]
            
            epoch = x0 + timedelta(seconds = t * dx)
        
            logging.info("{0}:  Achieved at {1}".\
                         format(self.name,epoch))
        
            return epoch

class OrbitNorthernPole(OrbitEvent):
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
    
    name = "Orbit.NorthernPole"
    
    def _occur(self,message):
        assert isinstance(message,InertialState)
        
        self.prev = self.next
        self.next = message
            
        m0 = self.prev.w
        m1 = self.next.w
            
        if (m0 >= 0 and m1 <= 0):
            x0 = self.prev.epoch
            x1 = self.next.epoch
            dx = (x1 - x0).total_seconds()
        
            p0 = self.prev.z
            p1 = self.next.z
            
            m0 *= dx
            m1 *= dx
            
            #p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
            m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
            
            r = m.r
            t = r[where((r > 0) & (r < 1))][0]
            
            epoch = x0 + timedelta(seconds = t * dx)
        
            logging.info("{0}:  Achieved at {1}".\
                         format(self.name,epoch))
        
            return epoch

class OrbitSouthernPole(OrbitEvent):
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
    
    name = "Orbit.SouthernPole"
    
    def _occur(self,message):
        assert isinstance(message,InertialState)
        
        self.prev = self.next
        self.next = message
            
        m0 = self.prev.w
        m1 = self.next.w
            
        if (m0 <= 0 and m1 >= 0):
            x0 = self.prev.epoch
            x1 = self.next.epoch
            dx = (x1 - x0).total_seconds()
        
            p0 = self.prev.z
            p1 = self.next.z
            
            m0 *= dx
            m1 *= dx
            
            #p = HERMITE_POLYNOMIAL(p0,m0,p1,m1)
            m = HERMITE_DERIVATIVE(p0,m0,p1,m1)
            
            r = m.r
            t = r[where((r > 0) & (r < 1))][0]
            
            epoch = x0 + timedelta(seconds = t * dx)
        
            logging.info("{0}:  Achieved at {1}".\
                         format(self.name,epoch))
        
            return epoch