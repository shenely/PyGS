#!/usr/bin/env python2.7

"""Message routines

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   10 Auguest 2013

Provides routines for message formatting.

Classes:
MessageParse  -- Parse message
MessageFormat -- Format message

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-08-10    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from .. import encoder,decoder,BaseObject
from .. import persist
from . import EventRoutine,ActionRoutine
#
##################


##################
# Export section #
#
__all__ = ["MessageParse",
           "MessageFormat"]
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


message_parse = persist.ObjectPersistance()

@message_parse.type(persist.EVENT_OBJECT)
class MessageParse(EventRoutine):
    """Story:  Parse epoch message
    
    IN ORDER TO process messages for synchronizing the current epoch
    AS A generic segment
    I WANT TO decode the a formatted string as an epoch
        
    """
    
    """Specification:  Parse epoch message
    
    GIVEN a downstream pipeline (default null)
        
    Scenario 1:  Upstream message received
    WHEN a message is received from upstream
    THEN the message SHALL be decoded as an epoch
        AND the epoch SHALL be sent downstream
    
    """
    
    name = "Message.Parse"
    
    def _occur(self,string):
        assert isinstance(string,types.StringTypes)
        
        logging.info("{0}:  Parsing from {1}".\
                     format(self.name,string))
        
        message =  BaseObject(**decoder(string))
        
        logging.info("{0}:  Parsed".\
                     format(self.name))
                     
        return message


message_format = persist.ObjectPersistance()

@message_format.type(persist.ACTION_OBJECT)
class MessageFormat(ActionRoutine):
    """Story:  Format epoch message
    
    IN ORDER TO generate messages for distributing the current epoch
    AS A clock segment
    I WANT TO encode a epoch in a defined string format
        
    """
    
    """Specification:  Format epoch message
    
    GIVEN an address for the message envelope
        AND a downstream pipeline (default null)
        
    Scenario 1:  Upstream epoch received
    WHEN an epoch is received from upstream
    THEN the epoch SHALL be encoded as a message
        AND the message SHALL be sent downstream
    
    """
    
    name = "Message.Format"
    
    def _execute(self,message):
        assert isinstance(message,BaseObject)
        
        logging.info("{0}:  Formatting".\
                     format(self.name))
        
        string = encoder(message)
        
        logging.info("{0}:  Formatted to {1}".\
                     format(self.name,string))
                     
        return string