#!/usr/bin/env python2.7

"""Fluent interface

Author(s):  Sean Henely
Language:   Python 2.x
Modified:   17 February 2013

Provides a fluent interfaces to routines.

Classes:

"""

"""Change log:
                                        
Date          Author          Version     Description
----------    ------------    --------    -----------------------------
2013-02-13    shenely         1.0         Initial revision
2013-02-14                    1.1         Needs of clock segment met
2013-02-15                    1.2         Attempting to fix split
2013-02-18                    1.3         Incorporating some lessons

"""


##################
# Import section #
#
#Built-in libraries
import logging
import types

#External libraries

#Internal libraries
from core.routine import control
#
##################


##################
# Export section #
#
__all__ = ["application"]
#
##################


####################
# Constant section #
#
__version__ = "1.3"#current version [major.minor]
#
####################


"""Story:  Fluent interface

IN ORDER TO configure a service to execute tasks
AS A user
I WANT TO build tasks with a fluent interface

"""

"""Specification:  Fluent interface

GIVEN a context

WHEN the context IS a task
    AND a source pipeline IS created
THEN the context SHALL be the source

WHEN the context IS a pipeline
    AND a sequence pipeline IS created
THEN the sequence SHALL be a downstream pipeline of the context
    AND the context SHALL be an upstream pipeline of the sequence
    AND the context SHALL be the sequence

WHEN the context IS a pipeline
    AND a sink pipeline IS created
THEN the sink SHALL be a downstream pipeline of the context
    AND the context SHALL be an upstream pipeline of the sink
    AND the context SHALL be the sink
    AND the context SHALL be sealed

WHEN the context IS a pipeline
    AND a choice pipeline IS created
THEN the choice SHALL be a downstream pipeline of the context
    AND the context SHALL be an upstream pipeline of the choice
    AND the context SHALL be the choice

WHEN the context IS a choice pipeline
    AND a true pipeline IS created
THEN the true SHALL be the true pipeline of the context
    AND the context SHALL be the choice pipeline of the true
    AND the content SHALL be the true

WHEN the context IS a choice pipeline
    AND a false pipeline IS created
THEN the true SHALL be the false pipeline of the context
    AND the context SHALL be the choice pipeline of the false
    AND the context SHALL be the false

WHEN the context IS a pipeline
    AND a split pipeline IS created
THEN the split SHALL be a downstream pipeline of the context
    AND the context SHALL be an upstream pipeline of the split
    AND the context SHALL be sealed

WHEN the context IS a task
    AND a merge pipeline IS created
THEN the merge SHALL be a downstream pipeline of the context
    AND the context SHALL be an upstream pipeline of the merge
    
WHEN the context IS a pipeline
    AND the context IS sealed
THEN the context SHALL be the upstream pipeline
    AND the context of the context SHALL be sealed
    
WHEN the context IS a source pipeline
    AND the context IS sealed
THEN the context SHALL be the context's task
    
WHEN the context IS a merge pipeline
    AND the context IS sealed
THEN the context SHALL be the context's task
"""


class Application(object):
    def __init__(self,name):
        self.name = name
        
        self.workflows = {}
        
        self.context = self
    
    def __getitem__(self,name):
        return self.routine[name]
    
    def clean(self):
        for name in self.workflows:
            self.workflows[name].clean()
    
    def build(self):
        self.routine = {}
        for name in self.workflows:
            self.routine[name] = self.workflows[name].build()
        else:
            return self
    
    def workflow(self,name):
        self.context = Workflow(self,name)
        
        return self
    
    def source(self,name,routine=None,*args,**kwargs):
        self.context = Source(self.context,name,routine,*args,**kwargs)
        
        return self
    
    def sink(self,name,routine=None,*args,**kwargs):
        self.context = Sink(self.context,name,routine,*args,**kwargs)
        self.context.seal()
        
        return self
    
    def sequence(self,name,routine=None,*args,**kwargs):
        self.context = Sequence(self.context,name,routine,*args,**kwargs)
        
        if self.context.sealed:self.context.seal()
        
        return self
    
    def choice(self,name,routine,*args,**kwargs):
        self.context = Choice(self.context,name,routine,*args,**kwargs)
        
        return self
    
    def istrue(self):
        
        self.context = IsTrue(self.context)
        
        return self
    
    def isfalse(self):
        assert isinstance(self.context,Choice)
        assert self.context.false is None
        
        self.context = IsFalse(self.context)
        
        return self
    
    def split(self,name):
        self.context = Split(self.context,name)
        self.context.seal()
        
        return self
    
    def merge(self,name):
        self.context = Merge(self.context,name)
        
        return self

class Workflow(object):
    def __init__(self,context,name):
        assert isinstance(context,(Application,Workflow))
        
        self.name = name
        
        self.pipelines = {}
        
        if isinstance(context,Application):
            self.application = context
            context.workflows[name] = self
        elif isinstance(context,Workflow):
            self.application = context.application
            context.application.workflows[name] = self
    
    def clean(self):
        for name in self.pipelines:
            if isinstance(self.pipelines[name],Source) and\
               len(self.pipelines[name].upstream) == 0:
                return self.pipelines[name].clean()
    
    def build(self):
        for name in self.pipelines:
            if isinstance(self.pipelines[name],Source) and\
               len(self.pipelines[name].upstream) == 0:
                return self.pipelines[name].build()

class Pipeline(object):
    def __new__(cls,context,name=None,routine=None,*args,**kwargs):
        if isinstance(context,Pipeline) and\
           name in context.workflow.pipelines:
            obj = context.workflow.pipelines[name]
        elif isinstance(context,Workflow) and\
           name in context.pipelines:
            obj = context.pipelines[name]
        else:
            obj = object.__new__(cls)
            
            obj.name = name
            
            obj.routine = routine
            obj.args = args
            obj.kwargs = kwargs
            
            obj.upstream = {}
            obj.downstream = {}
            
            obj.sealed = False
            obj.built = False
        
        if isinstance(context,Pipeline):
            context.downstream[name] = obj
            obj.upstream[context.name] = context
            context = context.workflow
        else:pass
        
        obj.workflow = context
        context.pipelines[name] = obj
            
        return obj
        
    def seal(self):
        self.workflow.application.context = self
        
        for name in self.downstream:
            if not self.downstream[name].sealed:
                break
        else:
            self.sealed = True
            
            for name in self.upstream:
                if not self.upstream[name].sealed:
                    self.upstream[name].seal()
                    
                    break
            else:
                self.workflow.application.context = self.workflow
    
    def clean(self):
        self.built = False
        
        for name in self.downstream:
            self.downstream[name].clean()
    
    def build(self):
        if self.built:pass
        else:
            self.built = True
            
            pipeline = None
            for name in self.downstream:
                pipeline = self.downstream[name].build()
            else:
                self.pipeline = self.routine(pipeline=pipeline,*self.args,**self.kwargs)\
                                if self.routine is not None else None
        
        return self.pipeline

class Source(Pipeline):        
    def seal(self):
        Pipeline.seal(self)
        
        self.workflow.application.context = self.workflow

class Sink(Pipeline):
    def __new__(cls,*args,**kwargs):
        obj = Pipeline.__new__(cls,*args,**kwargs)
        
        obj.sealed = True
        
        return obj

class Sequence(Pipeline):pass

class Choice(Pipeline):
    def __new__(cls,context,name,routine,*args,**kwargs):
        obj = Pipeline.__new__(cls,context,name,routine,*args,**kwargs)
        
        obj.true = None
        obj.false = None
        
        return obj
        
    def seal(self):
        self.workflow.application.context = self
        
        if self.true is not None and self.false is not None and\
           self.true.sealed and self.false.sealed:
            self.sealed = True
            
            for name in self.upstream:
                if not self.upstream[name].sealed:
                    self.upstream[name].seal()
                    
                    break
    
    def clean(self):
        self.built = False
        
        if self.true is not None:
            self.true.clean()
        if self.false is not None:
            self.false.clean()
    
    def build(self):
        if self.built:pass
        else:
            self.built = True
            
            istrue = self.true.build()
            isfalse = self.false.build()
            
            self.pipeline = self.routine(istrue=istrue,isfalse=isfalse,*self.args,**self.kwargs)
            
        return self.pipeline

class IsTrue(Pipeline):
    def __new__(cls,context):
        assert isinstance(context,Choice)
        assert context.false is None
        
        obj = Pipeline.__new__(cls,context,name=context.name+" (True)",routine=None)
        
        obj.choice = context
        context.true = obj
        
        return obj
        
    def seal(self):        
        for name in self.downstream:
            if not self.downstream[name].sealed:
                break
        else:
            self.sealed = True
            
            self.choice.seal()
    
    def build(self):
        if self.built:pass
        else:
            self.built = True
            
            pipeline = None
            for name in self.downstream:
                self.pipeline = self.downstream[name].build()
        
        return self.pipeline

class IsFalse(Pipeline):
    def __new__(cls,context):
        assert isinstance(context,Choice)
        assert context.false is None
        
        obj = Pipeline.__new__(cls,context,name=context.name+" (False)",routine=None)
        
        obj.choice = context
        context.false = obj
        
        return obj
        
    def seal(self):        
        for name in self.downstream:
            if not self.downstream[name].sealed:
                break
        else:
            self.sealed = True
            
            self.choice.seal()
    
    def build(self):
        if self.built:pass
        else:
            self.built = True
            
            pipeline = None
            for name in self.downstream:
                self.pipeline = self.downstream[name].build()
        
        return self.pipeline

class Split(Sink):
    def __new__(cls,context,name):
        obj = Sink.__new__(cls,context,name,control.split)
        
        return obj
    
    def build(self):
        if self.built:pass
        else:
            self.built = True
            
            ipipe = None
            opipes = []
            for name in self.downstream:
                opipes.append(self.downstream[name].build())
            else:
                self.pipeline = self.routine(ipipe=ipipe,opipes=opipes)
        
        return self.pipeline

class Merge(Source):
    def __new__(cls,context,name):
        obj = object.__new__(cls)
        
        obj.name = name
        
        obj.routine = control.merge
        obj.args = []
        obj.kwargs = {}
        
        obj.upstream = {}
        obj.downstream = {}
        
        if isinstance(context,Pipeline):
            context.downstream[name] = obj
            obj.upstream[context.name] = context
            context = context.workflow
        else:pass
        
        if name in context.pipelines and \
           isinstance(context.pipelines[name],Sink):
            obj.upstream.update(context.pipelines[name].upstream)
            
            for name2 in obj.upstream:
                obj.upstream[name2].downstream[name] = obj
        
        obj.workflow = context
        context.pipelines[name] = obj
        
        obj.sealed = False
        obj.built = False
        
        return obj
    
    def build(self):
        if self.built:pass
        else:
            self.built = True
            
            opipe = None
            ipipes = [None] * len(self.upstream)
            for name in self.downstream:
                opipe = self.downstream[name].build()
            else:
                self.pipeline = self.routine(ipipes=ipipes,opipe=opipe)
        
        return self.pipeline

def application(name):
    return Application(name)

def main():
    logging.basicConfig(level=logging.DEBUG)
    
    test = application("test-application").\
        workflow("test-workflow").\
            source("test-source",control.allow).\
            split("test-split").\
            source("test-split").\
            sink("test-merge").\
            merge("test-merge").\
            sink("test-sink")
    
    test.clean()
    test.build()
            
if __name__ == '__main__':
    main()