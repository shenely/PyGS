from routine import *

__all__ = ["FromClause",
           "ToClause",
           "GivenClause",
           "WhenClause",
           "ThenClause"]

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