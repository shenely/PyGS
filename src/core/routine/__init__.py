import logging
from .. import coroutine

__all__ = ["SourceRoutine",
           "TargetRoutine",
           "ConditionRoutine",
           "EventRoutine",
           "ActionRoutine"]

class BaseRoutine(object):
    name = "Core.Base"
    
    def __init__(self):
        self.source = list()
        self.target = None
        
        self.routine = self._routine()
    
    @coroutine
    def _routine(self): 
        message,opipe = None,None
               
        logging.debug("{0}:  Starting".\
                      format(self.name))
        while True:
            try:
                message,ipipe = yield message,opipe
            except GeneratorExit:
                logging.warn("{0}:  Stopping".\
                             format(self.name))
                
                return
            else:
                logging.info("{0}:  Processing".\
                             format(self.name))
                
                message,opipe = self._process(message,ipipe)
        
                logging.info("{0}:  Processed".\
                             format(self.name))
    
    def _process(self,message,ipipe):
        raise NotImplemented
    
    def set_source(self,source):
        assert isinstance(source,BaseRoutine)
        
        if len(self.source) == 0:
            logging.info("{0}:  Single source defined".\
                         format(self.name))
        else:
            logging.warn("{0}:  Multiple sources defined".\
                         format(self.name))
        
        self.source.append(source)
    
    def set_target(self,target):
        assert isinstance(target,BaseRoutine)
        
        if self.target is None:
            logging.info("{0}:  Target defined".\
                         format(self.name))
        else:
            logging.error("{0}:  Target redefined".\
                          format(self.name))
        
        self.target = target

class SourceRoutine(BaseRoutine):
    name = "Core.Source"
    
    def _process(self,message,ipipe):
        logging.info("{0}:  Receiving".\
                     format(self.name))
        
        message = self._receive()
        opipe = self.target
        
        logging.info("{0}:  Received".\
                     format(self.name))
        
        return message,opipe
    
    def _receive(self):
        raise NotImplemented

class TargetRoutine(BaseRoutine):
    name = "Core.Target"
    
    def _process(self,message,ipipe):
        logging.info("{0}:  Sending".\
                     format(self.name))
        
        self._send(message)
        opipe = self.target
        
        logging.info("{0}:  Sent".\
                     format(self.name))
        
        return message,opipe
    
    def _send(self,message):
        raise NotImplemented

class ConditionRoutine(BaseRoutine):
    name = "Core.Condition"
    
    def _process(self,message,ipipe):
        logging.info("{0}:  Satisfying".\
                     format(self.name))
            
        if self._satisfy(message):
            logging.info("{0}:  Satisfied".\
                         format(self.name))
            
            opipe = self.target[True]
        else:
            logging.info("{0}:  Not satisfied".\
                         format(self.name))
            
            opipe = self.target[False]
            
        return message,opipe
    
    def _satisfy(self,message):
        raise NotImplemented
    
    def set_target(self,target):
        assert isinstance(target,BaseRoutine)
        
        if self.mode not in self.target:
            logging.info("{0}:  {1} target defined".\
                         format(self.name,self.mode))
        else:
            logging.error("{0}:  Target redefined".\
                          format(self.name,self.mode))
        
        self.target[self.mode] = target

class EventRoutine(BaseRoutine):
    name = "Core.Event"
    
    def _process(self,message,ipipe):
        logging.info("{0}:  Occurring".\
                     format(self.name))
        
        message = self._occur(message)
        
        if message is not None:
            logging.info("{0}:  Occurred".\
                         format(self.name))
            
            opipe = self.target
        else:
            logging.warn("{0}:  False alarm".\
                         format(self.name))
            
            opipe = None
            
        return message,opipe
    
    def _occur(self,message):
        raise NotImplemented

class ActionRoutine(BaseRoutine):
    name = "Core.Action"
    
    def _process(self,message,ipipe):
        logging.info("{0}:  Executing".\
                     format(self.name))
        
        message = self._execute(message)
        opipe = self.target
        
        logging.info("{0}:  Executed".\
                     format(self.name))
            
        return message,opipe
    
    def _execute(self,message):
        raise NotImplemented