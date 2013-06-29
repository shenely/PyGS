from .agenda import *
from .routine import *

__all__ = ["Application"]

class Application(object):
    def __init__(self,name,scheduler):
        self.name = name
        self.scheduler = scheduler
        
    def Behavior(self,name):
        assert isinstance(name,basestring)
        
        self.context = Behavior(name)
        
        return self
    
    def Scenario(self,name):
        assert isinstance(name,basestring)
        
        self.context = Scenario(name)
        
        return self
    
    def From(self,name,routine):
        assert isinstance(self.context,Scenario)
        
        self.context = FromClause(name,routine)

        if routine.type is PERIODIC:
            self.scheduler.periodic(routine,routine.timeout).start()
        elif routine.type is DELAYED:
            self.scheduler.delayed(routine,routine.timeout).start()
        elif routine.type is HANDLER:
            self.scheduler.delayed(routine,routine.handle,routine.event)
        
        return self
    
    def When(self,name,routine):
        assert isinstance(self.context,FromClause)
        
        self.context = WhenClause(name,routine,self.context)
        
        return self
    
    def Given(self,name,routine):
        assert isinstance(self.context,(FromClause,
                                        WhenClause))
        
        self.context = GivenClause(name,routine,self.context)
        
        return self
    
    def Then(self,name,routine):
        assert isinstance(self.context,(FromClause,
                                        WhenClause,
                                        GivenClause))
        
        self.context = ThenClause(name,routine,self.context)
        
        return self
    
    def To(self,name,routine):
        assert isinstance(self.context,(FromClause,
                                        WhenClause,
                                        GivenClause,
                                        ThenClause))
        
        self.context = ToClause(name,routine,self.context)
        
        return self
    
    def And(self,name,routine):        
        if isinstance(self.context,FromClause):
            self.context = FromClause(name,routine,self.context)
        elif isinstance(self.context,WhenClause):
            self.context = WhenClause(name,routine,self.context)
        elif isinstance(self.context,GivenClause):
            self.context = GivenClause(name,routine,self.context)
        elif isinstance(self.context,ThenClause):
            self.context = ThenClause(name,routine,self.context)
        elif isinstance(self.context,ThenClause):
            self.context = ToClause(name,routine,self.context)
        else:
            raise Exception
        
        return self
    
    def Is(self,mode):
        assert isinstance(mode,bool)
        assert isinstance(self.context,GivenClause)
        
        self.context.routine.mode = mode
        
        return self

class Behavior:
    def __init__(self,name):
        self.name = name

class Scenario:
    def __init__(self,name):
        self.name = name

class BaseClause(object):
    def __init__(self,name,routine,context):
        assert isinstance(name,basestring)
        
        self.name = name
        self.routine = routine
        
        if isinstance(context,BaseClause):
            self.routine.set_source(context.routine)
            context.routine.set_target(self.routine)

class FromClause(BaseClause):
    def __init__(self,name,routine,context=None):
        assert isinstance(routine,SourceRoutine)
        
        BaseClause.__init__(self,name,routine,context)
        
class ToClause(BaseClause):
    def __init__(self,name,routine,context=None):
        assert isinstance(routine,TargetRoutine)
        
        BaseClause.__init__(self,name,routine,context)

class GivenClause(BaseClause):
    def __init__(self,name,routine,context=None):
        assert isinstance(routine,ConditionRoutine)
        
        BaseClause.__init__(self,name,routine,context)
        
class WhenClause(BaseClause):
    def __init__(self,name,routine,context=None):
        assert isinstance(routine,EventRoutine)
        
        BaseClause.__init__(self,name,routine,context)
        
class ThenClause(BaseClause):
    def __init__(self,name,routine,context=None):
        assert isinstance(routine,ActionRoutine)
        
        BaseClause.__init__(self,name,routine,context)