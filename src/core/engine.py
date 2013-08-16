import types
import pickle

import zmq
import pymongo

from . import BaseObject
from . import agenda
from .routine import *

__all__ = ["Application",
           "Behavior",
           "Scenario"]

class Application(object):
    self = dict()
    
    def __new__(cls,name):
        if name not in cls.self:
            cls.self[name] = object.__new__(cls)
            
        return cls.self[name]
    
    def __init__(self,name):
        assert isinstance(name,types.StringTypes)
        
        object.__init__(self)
        
        if not hasattr(self,"name"):
            self.name = name
            
            self.behaviors = list()
            
            self.context = zmq.Context(1)
            
            self.connection = pymongo.MongoClient()
            self.database = self.connection[self.name]
            self.processor = agenda.Processor()
            
            self.stories = self.database.stories.find()
    
    def build(self):
        for story in self.stories:
            self.behaviors.append(Behavior(**story))
    
        for behavior in self.behaviors:
            behavior.build(self)
            
    def start(self):
        self.processor.start()

class Behavior(BaseObject):
    def __init__(self,name,nodes=[],links=[],rules=[],*args,**kwargs):
        self.application = None
        
        self.routines = []
        self.scenarios = []
        
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(name,types.StringTypes)
        assert isinstance(nodes,types.ListType)
        assert isinstance(links,types.ListType)
        assert isinstance(rules,types.ListType)
        
        self.name = name
        self.nodes = nodes
        self.links = links
        self.rules = rules
        
    def build(self,application):
        self.application = application
        
        for node in self.nodes:
            node = BaseObject(**node)
            
            query = {"_id":node._id}
            node.routine = pickle.loads(BaseObject(**self.application \
                                                         .connection \
                                                         .database \
                                                         .Objects.find_one(query))\
                                                  .path)
            
            self.routines.append(node)
        
        for link in self.links:
            link = BaseObject(**link)
            link.source = BaseObject(**link.source)
            link.target = BaseObject(**link.target)
            
            if link.source.type == "property":
                setattr(self.nodes[link.target.index],
                        link.target.name,
                        getattr(self.routines[link.source.index],
                                link.source.name))
            elif link.source.type == "method":
                setattr(self.nodes[link.target.index],
                        link.target.name,
                        getattr(self.routines[link.source.index],
                                link.source.name)())

        for rule in self.rules:
            self.scenarios.append(Scenario(**rule))
    
        for scenario in self.scenarios:
            scenario.build(self)

class Scenario(BaseObject):
    def __init__(self,name,*args,**kwargs):
        self.behavior = None
        
        self.context = self
        
        BaseObject.__init__(self,*args,**kwargs)
        
        assert isinstance(name,types.StringTypes)
        assert isinstance(getattr(kwargs,"from",[]),types.ListType)
        assert isinstance(getattr(kwargs,"when",[]),types.ListType)
        assert isinstance(getattr(kwargs,"given",{}),types.DictType)
        assert isinstance(getattr(kwargs,"then",[]),types.ListType)
        assert isinstance(getattr(kwargs,"to",[]),types.ListType)
        
        self.name = name
        self["from"] = getattr(kwargs,"from",[])
        self["when"] = getattr(kwargs,"when",[])
        self["given"] = getattr(kwargs,"given",{})
        self["then"] = getattr(kwargs,"then",[])
        self["to"] = getattr(kwargs,"to",[])
        
    def build(self,behavior):
        self.behavior = behavior
        
        for index in self["from"]:
            self.From(**self.behavior.routines[index])
        
        for index in self["when"]:
            self.When(**self.behavior.routines[index])
        
        for index in self["given"]:
            self.Given(**self.behavior.routines[index]) \
                .Is(self["given"][index])
        
        for index in self["then"]:
            self.Then(**self.behavior.routines[index])
        
        for index in self["to"]:
            self.To(**self.behavior.routines[index])
    
    def From(self,description,routine):
        assert isinstance(self.context,Scenario)
        
        self.context = FromClause(description,routine)

        if routine.type is agenda.PERIODIC:
            self.behavior \
                .application \
                .processor.periodic(routine,routine.timeout).start()
        elif routine.type is agenda.DELAYED:
            self.behavior \
                .application \
                .processor.delayed(routine,routine.timeout).start()
        elif routine.type is agenda.HANDLER:
            self.behavior \
                .application \
                .processor.handler(routine,routine.handle,routine.event)
        
        return self
    
    def When(self,description,routine):
        assert isinstance(self.context,(FromClause,
                                        WhenClause))
        
        self.context = WhenClause(description,routine,self.context)
        
        return self
    
    def Given(self,description,routine):
        assert isinstance(self.context,(Scenario,
                                        FromClause,
                                        WhenClause,
                                        GivenClause))
        
        self.context = GivenClause(description,routine,self.context)
        
        return self
    
    def Then(self,description,routine):
        assert isinstance(self.context,(Scenario,
                                        FromClause,
                                        WhenClause,
                                        GivenClause,
                                        ThenClause))
        
        self.context = ThenClause(description,routine,self.context)
        
        return self
    
    def To(self,description,routine):
        assert isinstance(self.context,(FromClause,
                                        WhenClause,
                                        GivenClause,
                                        ThenClause,
                                        ToClause))
        
        self.context = ToClause(description,routine,self.context)
        
        return self
    
    def And(self,description,routine):        
        if isinstance(self.context,FromClause):
            self.context = FromClause(description,routine,self.context)
        elif isinstance(self.context,WhenClause):
            self.context = WhenClause(description,routine,self.context)
        elif isinstance(self.context,GivenClause):
            self.context = GivenClause(description,routine,self.context)
        elif isinstance(self.context,ThenClause):
            self.context = ThenClause(description,routine,self.context)
        elif isinstance(self.context,ToClause):
            self.context = ToClause(description,routine,self.context)
        else:
            raise Exception
        
        return self
    
    def Is(self,mode):
        assert isinstance(mode,bool)
        assert isinstance(self.context,GivenClause)
        
        self.context.routine.mode = mode
        
        return self
    
class BaseClause(object):
    def __init__(self,description,routine,context):
        assert isinstance(description,types.StringTypes)
        
        self.description = description
        self.routine = routine
        
        if isinstance(context,BaseClause):
            self.routine.set_source(context.routine)
            context.routine.set_target(self.routine)

class FromClause(BaseClause):
    def __init__(self,description,routine,context=None):
        assert isinstance(routine,SourceRoutine)
        
        BaseClause.__init__(self,description,routine,context)
        
class ToClause(BaseClause):
    def __init__(self,description,routine,context=None):
        assert isinstance(routine,TargetRoutine)
        
        BaseClause.__init__(self,description,routine,context)

class GivenClause(BaseClause):
    def __init__(self,description,routine,context=None):
        assert isinstance(routine,ConditionRoutine)
        
        BaseClause.__init__(self,description,routine,context)
        
class WhenClause(BaseClause):
    def __init__(self,description,routine,context=None):
        assert isinstance(routine,EventRoutine)
        
        BaseClause.__init__(self,description,routine,context)
        
class ThenClause(BaseClause):
    def __init__(self,description,routine,context=None):
        assert isinstance(routine,ActionRoutine)
        
        BaseClause.__init__(self,description,routine,context)