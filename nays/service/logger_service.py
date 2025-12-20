from abc import ABC, abstractmethod

from nays.core.logger import setupLogger


class LoggerService(ABC):
    """Abstract logger service interface"""
    @abstractmethod
    def debug(self, message: str):
        pass
    
    @abstractmethod
    def info(self, message: str):
        pass
    
    @abstractmethod
    def warning(self, message: str):
        pass
    
    @abstractmethod
    def error(self, message: str):
        pass


class LoggerServiceImpl(LoggerService):
    """Logger service implementation using setupLogger"""
    
    def __init__(self):
        self.logger = setupLogger(self)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)