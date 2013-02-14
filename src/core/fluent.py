#!/usr/bin/env python2.7

"""Fluent interface

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   13 February 2013

Provides a fluent interfaces to routines.

Classes:

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-13    shenely         1.0         Initial revision

"""


##################
# Import section #
#
#Built-in libraries

#External libraries

#Internal libraries
#
##################


##################
# Export section #
#
__all__ = []
#
##################


####################
# Constant section #
#
__version__ = "1.0"#current version [major.minor]
#
####################


"""Story:  Fluent interface

IN ORDER TO configure a service to execute tasks
AS A user
I WANT TO a fluent interface

"""

"""Specification:  Fluent interface

GIVEN the current service
    AND the current task
    AND the current context


Scenario 1:  Nominal task creation

WHEN the context IS a service
    AND a task IS added to the service
    AND a task name IS provided
    AND no task in the service has any unsealed sequences
THEN the task name SHALL be unique to the service
    AND a new task SHALL be created with the provided name
    AND the task SHALL be added as a child of the service
    AND the service SHALL be added as the parent of the task
    AND the current context SHALL be the new task


Scenario 2:  Nominal task termination

WHEN the context IS a task
    AND a task IS added to the service
    AND a task name IS provided
    AND the current context has no unsealed sequences
THEN the task name SHALL be unique to the service
    AND a new task SHALL be created with the provided name
    AND the new task SHALL be added as a child of the service
    AND the service SHALL be added as the parent of the new task
    AND the current context SHALL be the new task


Scenario 3:  Source sequence creation

WHEN the current context IS the current task task
    AND a source sequence IS added to the task
    AND a sequence name IS provided
    AND a routine IS provided
    AND optional arguments ARE provided
THEN the sequence name SHALL be unique to the task
    AND a new source sequence SHALL be created with the provided name,
        routine, and optional arguments
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be the new sequence


Scenario 4:  Nominal sequence creation

WHEN the current context IS a sequence
    AND a sequence IS added to the task
    AND a sequence name IS provided
    AND a routine IS provided
    AND optional arguments ARE provided
THEN the sequence name SHALL be unique to the task
    AND a new sequence SHALL be created with the provided name,
        routine, and optional arguments
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be the new sequence


Scenario 5:  Referenced sequence creation

WHEN the current context IS a sequence
    AND a sequence IS added to the task
    AND a sequence name IS provided
    AND a routine IS NOT provided
    AND the sequence name matches a sequence name in the current task
    AND the sequence matching the sequence name IS sealed
THEN the sequence matching the sequence name SHALL refer to the 
        downstream sequence
    AND the current context SHALL refer to the upstream sequence
    AND the upstream sequence SHALL be added as a parent of the 
        downstream sequence
    AND the downstream sequence SHALL be added as a parent of the 
        upstream sequence
    AND the current context SHALL be sealed


Scenario 6:  Sink sequence creation

WHEN the current context IS a sequence
    AND a sink sequence IS added to the task
    AND a sequence name IS provided
    AND a routine IS provided
    AND optional arguments ARE provided
THEN the sequence name SHALL be unique to the task
    AND a new sink sequence SHALL be created with the provided name,
        routine, and optional arguments
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be sealed


Scenario 7:  Anonymous sink sequence creation

WHEN the current context IS a sequence
    AND a sink sequence IS added to the task
THEN the sequence name SHALL be unique to the task
    AND a new sink sequence SHALL be created
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be sealed


Scenario 8:  Task split sequence creation

WHEN the current context IS a sequence
    AND a split sequence IS added to the task
    AND a list of names IS provided
THEN the list of names SHALL be treated as a list of task names in the
        current service
    AND list of task names SHALL be added as downstream dependencies of
        the current task
    AND the current context SHALL be sealed


Scenario 9:  Nominal sequence termination

WHEN the current context is sealed
    AND the current context IS a sequence
    AND the current context IS NOT a source sequence
    AND the parent of the current context IS NOT a choice sequence
THEN the current context SHALL be the parent of the current context
    AND the current context SHALL be sealed


Scenario 10:  Source sequence termination

WHEN the current context is sealed
    AND the current context IS a source sequence
THEN the current context SHALL be the current task


Scenario 11:  Choice sequence termination

WHEN the current context is sealed
    AND the parent of the current context IS a choice sequence
    AND the true sequence of the choice sequence is sealed
    AND the false sequence of the choice sequence is sealed
THEN the current context SHALL be the parent of the current context
    AND the current context SHALL be sealed


Scenario 12:  Choice sequence creation

WHEN the current context IS a sequence
    AND a choice sequence IS added to the task
    AND a sequence name IS provided
    AND a routine IS provided
    AND optional arguments ARE provided
THEN the sequence name SHALL be unique to the task
    AND a new choice sequence SHALL be created with the provided name,
        routine, and optional arguments
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be the new sequence


Scenario 13:  True sequence creation
    
WHEN the current context is a choice sequence
    AND a true sequence IS added to the current context
THEN the sequence name SHALL be unique to the task
    AND a new true sequence SHALL be created
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be the new sequence


Scenario 14:  False sequence creation
    
WHEN the current context is a choice sequence
    AND a false sequence IS added to the current context
THEN the sequence name SHALL be unique to the task
    AND a new false sequence SHALL be created
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be the new sequence


Scenario 15:  Child sequences of true sequence
    
WHEN the current context is a true sequence
    AND a sequence IS added to the task
    AND a sequence name IS provided
    AND a routine IS provided
    AND optional arguments ARE provided
THEN the sequence name SHALL be unique to the task
    AND a new sequence SHALL be created with the provided name,
        routine, and optional arguments
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be the new sequence


Scenario 16:  Child sequences of false sequence
    
WHEN the current context is a false sequence
    AND a sequence IS added to the task
    AND a sequence name IS provided
    AND a routine IS provided
    AND optional arguments ARE provided
THEN the sequence name SHALL be unique to the task
    AND a new sequence SHALL be created with the provided name,
        routine, and optional arguments
    AND the sequence SHALL be added as a child of the context
    AND the context SHALL be added as the parent of the sequence
    AND the current context SHALL be the new sequence


Scenario 17:  True sequence termination

WHEN the current context is sealed
    AND the parent of the current context IS a true sequence
THEN the current context SHALL be the parent of the current context
    AND the current context SHALL be sealed


Scenario 18:  False sequence termination

WHEN the current context is sealed
    AND the parent of the current context IS a false sequence
THEN the current context SHALL be the parent of the current context
    AND the current context SHALL be sealed
"""