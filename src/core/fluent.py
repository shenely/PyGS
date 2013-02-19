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
from core import ObjectDict
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
        
    def assets(self,*args,**kwargs):
        if len(args) == 0:
            return Assets(public=kwargs["public"],private=kwargs["private"])
        else:
            for name in self.workflows:
                self.workflows[wname].assets(*args)
    
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
        
    def assets(self,*args):
        if len(args) == 0:
            return Assets(public=kwargs["public"],private=kwargs["private"])
        else:
            for name in self.pipelines:
                if isinstance(self.pipelines[name],Assets):
                    self.pipelines[name].clean(full=False)

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
            
            obj.pipeline = None
            
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
    
    def clean(self,full):
        self.built = False
        
        for name in self.downstream:
            self.downstream[name].clean(full)
        else:
            self.pipeline.close() if self.pipeline is not None else None
            
            self.pipeline = None
    
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
            
                for name in self.upstream:
                    if isinstance(self.upstream[name],Split):
                        self.upstream[name].tick(self.pipeline)
                for name in self.downstream:
                    if isinstance(self.downstream[name],Merge):
                        self.downstream[name].tick(self.pipeline)
        
        return self.pipeline

class Assets(Pipeline):pass

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
    
    def clean(self,full):
        self.built = False
        
        if self.true is not None:
            self.true.clean(full)
        if self.false is not None:
            self.false.clean(full)

        self.pipeline.close() if self.pipeline is not None else None
            
        self.pipeline = None
    
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
        
        obj.opipes = []
        
        return obj
    
    def clean(self,full=True):
        Sink.clean(self,full)
        
        self.opipes = []
    
    def build(self):
        if self.built:pass
        else:
            self.built = True
            
            ipipe = None
            for name in self.downstream:
                self.opipes.append(self.downstream[name].build())
            else:
                self.pipeline = self.routine(ipipe=ipipe,opipes=self.opipes)
        
        return self.pipeline
    
    def tick(self,pipeline):
        self.opipes.append(pipeline)

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
        
        obj.ipipes = []
        obj.pipeline = None
        
        return obj
    
    def clean(self,full=True):
        if full:
            Source.clean(self,full)        
        
            self.ipipes = []
    
    def build(self):       
        if self.built:pass
        else:
            self.built = True
            
            for name in self.downstream:
                opipe = self.downstream[name].build()
            else:
                self.pipeline = self.routine(ipipes=self.ipipes,opipe=opipe)
        
        return self.pipeline
    
    def tick(self,pipeline):
        self.ipipes.append(pipeline)

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