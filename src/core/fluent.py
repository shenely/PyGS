#!/usr/bin/env python2.7

"""Fluent interface

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   14 February 2013

Provides a fluent interfaces to routines.

Classes:

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-13    shenely         1.0         Initial revision
2013-02-14                    1.1         Needs of clock segment met

"""


##################
# Import section #
#
#Built-in libraries
import types

#External libraries

#Internal libraries
from core.routine import control
#
##################


##################
# Export section #
#
__all__ = ["service"]
#
##################


####################
# Constant section #
#
__version__ = "1.1"#current version [major.minor]
#
####################


"""Story:  Fluent interface

IN ORDER TO configure a service to execute tasks
AS A user
I WANT TO build tasks with a fluent interface

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

WHEN the current context IS the current task
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

class Service:
    def __init__(self,name):
        self.name = name
        
        self.tasks = {}
        self.context = self
    
    def task(self,name):
        task = Task(name,service=self)
        
        self.context = task
        
        return self
    
    def source(self,name,routine=None,*args,**kwargs):
        if routine is not None:
            Source(name,routine,self.context,*args,**kwargs)
        else:
            if self.context.name in self.tasks[name].dstream:
                self.tasks[name].dstream[self.context.name].dstream[self.context.name] = self.context
                self.context.ustream[name] = self.tasks[name].dstream[self.context.name]
                
                self.context = self.tasks[name].dstream[self.context.name]
            elif name in self.context.task.pipes and\
                 self.context.task.pipes[name].sealed:
                self.context.dstream[name] = self.context.task.pipes[name]
                self.context.task.pipes[name].ustream[name] = self.context
                
                self.context = self.context.task.pipes[name]
                self.context.seal()
        
        return self
    
    def sequence(self,name,routine=None,*args,**kwargs):
        if routine is not None:
            Sequence(name,routine,self.context.task,*args,**kwargs)
        else:
            if name in self.context.task.pipes and\
               self.context.task.pipes[name].sealed:
                self.context.dstream[name] = self.context.task.pipes[name]
                self.context.task.pipes[name].ustream[name] = self.context
                
                self.context = self.context.task.pipes[name]
                self.context.seal() 
        
        return self
    
    def sink(self,name,routine=None,*args,**kwargs):
        if name in self.context.task.pipes:
            self.context.dstream[name] = self.context.task.pipes[name]
            self.context.task.pipes[name].ustream[self.context.name] = self.context
            
            self.context = self.context.task.pipes[name]
            self.context.seal()
        else:
            Sink(name,routine,self.context.task,*args,**kwargs)
        
        return self
    
    def choice(self,name,routine,*args,**kwargs):
        Choice(name,routine,self.context.task,*args,**kwargs)
        
        return self
    
    def istrue(self):
        IsTrue(self.context)
        
        return self
    
    def isfalse(self):
        IsFalse(self.context)
        
        return self
    
    def split(self,name,dstream=None):
        Split(name,dstream,self.context.task)
        
        return self

    def build(self):
        for name in self.tasks:
            self.tasks[name] = self.tasks[name].build()
        else:
            return self
    
class Task:
    def __init__(self,name,service):
        self.name = name
        
        self.service = service
        service.tasks[name] = self
        
        self.pipes = {}
        
        self.ustream = {}
        self.dstream = {}

    def build(self):
        for name in self.pipes:
            if isinstance(self.pipes[name],Source) and\
               len(self.pipes[name].ustream) == 0 and\
               self.pipes[name].sealed:
                return self.pipes[name].build()
        
class Source:
    def __init__(self,name,routine,task,*args,**kwargs):
        self.name = name
        self.routine = routine
        self.args = args
        self.kwargs = kwargs
        
        self.ustream = {}
        self.dstream = {}
        
        self.service = task.service
        self.service.context = self
        
        self.task = task
        self.task.pipes[name] = self
        
        self.sealed = False
        self.built = False
    
    def seal(self):
        self.service.context = self
        
        for name in self.dstream:
            if not self.dstream[name].sealed:
                break
        else:
            self.sealed = True
            
            #self.service.context = self.task

    def build(self):
        if self.sealed:
            if not self.built:
                assert len(self.dstream) == 1
                
                for name in self.dstream:
                    self.dstream[name] = self.dstream[name].build()
                else:
                    self.routine = self.routine(pipeline=self.dstream[name],
                                                *self.args,**self.kwargs)
                    
                    self.built = True
                    
            return self.routine
            

class Sequence:
    def __init__(self,name,routine,task,*args,**kwargs):
        self.name = name
        self.routine = routine
        self.args = args
        self.kwargs = kwargs
        
        self.ustream = {}
        self.dstream = {}
        
        if isinstance(task.service.context.name,types.ListType):pass
        else:
            self.ustream[task.service.context.name] = task.service.context
        
        task.service.context.dstream[name] = self
        
        self.service = task.service
        self.service.context = self
        
        self.task = task
        self.task.pipes[name] = self
        
        self.sealed = False
        self.built = False
    
    def seal(self):
        self.service.context = self
        
        for name in self.dstream:
            if not self.dstream[name].sealed:
                break
        else:
            self.sealed = True
        
            for name in self.ustream:
                self.ustream[name].seal()

    def build(self):
        if self.sealed:
            if not self.built:
                assert len(self.dstream) == 1
                
                for name in self.dstream:
                    self.dstream[name] = self.dstream[name].build()
                else:
                    self.routine = self.routine(pipeline=self.dstream[name],
                                                *self.args,**self.kwargs)
                    
                    self.built = True
                    
            return self.routine

class Sink:
    def __init__(self,name,routine,task,*args,**kwargs):
        self.name = name
        self.routine = routine
        self.args = args
        self.kwargs = kwargs
        
        self.ustream = {}
        self.dstream = {}
        
        
        if isinstance(task.service.context.name,types.ListType):pass
        else:
            self.ustream[task.service.context.name] = task.service.context
        
        task.service.context.dstream[name] = self
        
        self.service = task.service
        self.service.context = self
        
        self.task = task
        self.task.pipes[name] = self
        
        self.sealed = False
        self.built = False
        
        self.seal()
    
    def seal(self):
        self.sealed = True
        
        for name in self.ustream:
            self.ustream[name].seal()

    def build(self):
        if self.sealed:
            if not self.built:
                assert len(self.dstream) == 0
                
                if self.routine is not None:
                    self.routine = self.routine(*self.args,**self.kwargs)
                    
                self.built = True
                    
            return self.routine

class Choice:
    def __init__(self,name,routine,task,*args,**kwargs):
        self.name = name
        self.routine = routine
        self.args = args
        self.kwargs = kwargs
        
        self.ustream = {}
        self.dstream = {}
        
        if isinstance(task.service.context.name,types.ListType):pass
        else:
            self.ustream[task.service.context.name] = task.service.context
        
        task.service.context.dstream[name] = self
        
        self.service = task.service
        self.service.context = self
        
        self.task = task
        self.task.pipes[name] = self
        
        self.sealed = False
        self.built = False
    
    def seal(self):
        self.service.context = self
        
        if "istrue" in self.dstream and\
           "isfalse" in self.dstream and\
           self.dstream["istrue"].sealed and\
           self.dstream["isfalse"].sealed:
            self.sealed = True
            
            for name in self.ustream:
                self.ustream[name].seal()

    def build(self):
        if self.sealed:
            if not self.built:
                assert len(self.dstream) == 2
                
                if self.dstream["istrue"].sealed and\
                   self.dstream["isfalse"].sealed:
                    istrue = self.dstream["istrue"].build()
                    isfalse = self.dstream["isfalse"].build()
                    
                    self.routine = self.routine(istrue=istrue,isfalse=isfalse,
                                                *self.args,**self.kwargs)
                    
                self.built = True
                    
            return self.routine

class IsTrue:
    def __init__(self,choice):
        self.choice = choice
        choice.dstream["istrue"] = self
        
        self.name = choice.name
        
        self.dstream = {}
        
        self.service = choice.service
        self.service.context = self
        
        self.task = choice.task
        
        self.sealed = False
        self.built = False
    
    def seal(self):
        self.service.context = self
        
        for name in self.dstream:
            if not self.dstream[name].sealed:
                break
        else:
            self.sealed = True
            
            self.choice.seal()

    def build(self):
        if self.sealed:
            if not self.built:
                assert len(self.dstream) == 1
                
                for name in self.dstream:
                    self.dstream[name] = self.dstream[name].build()
                else:
                    self.routine = self.dstream[name]
                    
                    self.built = True
                    
            return self.routine
        
class IsFalse:
    def __init__(self,choice):
        self.choice = choice
        choice.dstream["isfalse"] = self
        
        self.name = choice.name
        
        self.dstream = {}
        
        self.service = choice.service
        self.service.context = self
        
        self.task = choice.task
        
        self.sealed = False
        self.built = False
    
    def seal(self):
        self.service.context = self
        
        for name in self.dstream:
            if not self.dstream[name].sealed:
                break
        else:
            self.sealed = True
            
            self.choice.seal()

    def build(self):
        if self.sealed:
            if not self.built:
                assert len(self.dstream) == 1
                
                for name in self.dstream:
                    self.dstream[name] = self.dstream[name].build()
                else:
                    self.routine = self.dstream[name]
                    
                    self.built = True
                    
            return self.routine

class Split:
    def __init__(self,name,dstream=None,task=None):
        self.name = name
        self.routine = control.split
        
        self.ustream = {}
        self.dstream = {}
        
        self.ustream[task.service.context.name] = task.service.context
        task.service.context.dstream[name] = self
        
        if dstream is not None:
            for name in dstream:
                task.dstream[name] = self            
        
        self.task = task
        self.task.pipes[name] = self
        
        self.service = task.service
        self.service.context = self
        
        self.sealed = False
        self.built = False
        
        self.seal()
    
    def seal(self):
        self.sealed = True
        
        for name in self.ustream:
            self.ustream[name].seal()

    def build(self):
        if self.sealed:
            if not self.built:
                assert len(self.dstream) > 0
                
                for name in self.dstream:
                    self.dstream[name] = self.dstream[name].build()
                else:
                    self.routine = self.routine(ipipe=None,opipe=self.dstream.values())
                    
                self.built = True
                    
            return self.routine

class Merge:pass

def service(name):
    return Service("name")

def main():
    test = service("test-service").\
        task("test-task").\
            source("test-source",None).\
            sequence("test-sequence",None).\
            sink("test-sink",None)
    print test
            
if __name__ == '__main__':
    main()