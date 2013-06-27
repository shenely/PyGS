from .service import schedule
from .behavior import *
from .scenario import *
from .clause import *

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

        if routine.type is schedule.PERIODIC:
            self.scheduler.periodic(routine,routine.timeout).start()
        elif routine.type is schedule.DELAYED:
            self.scheduler.delayed(routine,routine.timeout).start()
        elif routine.type is schedule.HANDLER:
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
