#!/usr/bin/env python2.7

"""Method routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   09 August 2013

Provides routines for working with properties and methods.

Classes:
PropertyTransfer -- Transfer property
MethodExecute    -- Execute method

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-06-29    shenely         1.0         Initial revision
2013-08-09    shenely         1.1         Adding persistance logic

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from . import ActionRoutine
from .. import persist
#
##################


##################
# Export section #
#
__all__ = ["PropertyTransfer",
           "MethodExecute"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]
#
####################


property_transfer = persist.ObjectPersistance()

@property_transfer.type(persist.ACTION_OBJECT)
class PropertyTransfer(ActionRoutine):
    name = "Property.Transfer"
        
    @property_transfer.property
    def sourceObj(self):
        return self._source_obj
    
    @sourceObj.setter
    def sourceObj(self,source_obj):
        assert isinstance(source_obj,types.ObjectType)
        
        self._source_obj = source_obj
        self._source_cls = source_obj.__class__
        
    @property_transfer.property
    def sourceProp(self):
        return self._source_prop
    
    @sourceProp.setter
    def sourceProp(self,source_prop):
        assert isinstance(source_prop,types.StringTypes)
        assert hasattr(self._source_cls,source_prop)
        
        self._source_prop = source_prop
        
        self._source = getattr(self._source_cls,self._source_prop).fget
        
    @property_transfer.property
    def targetObj(self):
        return self._target_obj
    
    @targetObj.setter
    def targetObj(self,target_obj):
        assert isinstance(target_obj,types.ObjectType)
        
        self._target_obj = target_obj
        self._target_cls = target_obj.__class__
        
    @property_transfer.property
    def targetProp(self):
        return self._target_prop
    
    @targetProp.setter
    def targetProp(self,target_prop):
        assert isinstance(target_prop,types.StringTypes)
        assert hasattr(self._target_cls,target_prop)
        
        self._target_prop = target_prop
        
        self._target = getattr(self._target_cls,self._target_prop).fset
    
    def _execute(self,message):
        logging.info("{0}:  Transferring proeprty".\
                     format(self.name))
        
        self._target(self._target_obj,self._source(self._source_obj))
        
        logging.info("{0}:  Transferred property".\
                     format(self.name))
                     
        return message


method_execute = persist.ObjectPersistance()

@method_execute.type(persist.ACTION_OBJECT)
class MethodExecute(ActionRoutine):    
    name = "Method.Execute"
        
    @method_execute.property
    def method(self):
        return self._method
    
    @method.setter
    def method(self,method):
        assert isinstance(method,types.MethodType)
        
        self._method = method
    
    def _execute(self,message):
        logging.info("{0}:  Executing method".\
                     format(self.name))
        
        message = self._method(message)
        
        logging.info("{0}:  Executed method".\
                     format(self.name))
                     
        return message