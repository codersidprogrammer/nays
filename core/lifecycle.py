from abc import ABC, abstractmethod


class OnInit(ABC):
    
    @abstractmethod
    def onInit(self):
        raise NotImplementedError
    
class OnDestroy(ABC):
    
    @abstractmethod
    def onDestroy(self):
        raise NotImplementedError