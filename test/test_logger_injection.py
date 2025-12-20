import unittest
import logging
import sys
from pathlib import Path
from typing import Union
from abc import ABC, abstractmethod

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.module import NaysModule, Provider, ModuleFactory
from core.route import Route, RouteType
from core.lifecycle import OnInit
from core.logger import setupLogger


# ==================== Logger Service ====================
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


# ==================== Module Services ====================
class DatabaseService:
    """Database service for RootModule"""
    def __init__(self):
        self.name = "DatabaseService"


class CacheService:
    """Cache service for RootModule"""
    def __init__(self):
        self.name = "CacheService"


class PaymentService:
    """Payment service for PaymentModule"""
    def __init__(self):
        self.name = "PaymentService"


class NotificationService:
    """Notification service for NotificationModule"""
    def __init__(self):
        self.name = "NotificationService"


# ==================== Routes ====================
class RootDashboardRoute(OnInit):
    """Root dashboard route with logger injection"""
    def __init__(self):
        self.initialized = False
        self.logger_messages = []
    
    def onInit(self):
        self.initialized = True
        self.logger_messages.append("RootDashboardRoute initialized")


class PaymentRoute(OnInit):
    """Payment route with logger injection"""
    def __init__(self):
        self.initialized = False
        self.logger_messages = []
    
    def onInit(self):
        self.initialized = True
        self.logger_messages.append("PaymentRoute initialized")


class NotificationRoute(OnInit):
    """Notification route with logger injection"""
    def __init__(self):
        self.initialized = False
        self.logger_messages = []
    
    def onInit(self):
        self.initialized = True
        self.logger_messages.append("NotificationRoute initialized")


# ==================== Modules ====================
logger_provider = Provider(
    provide=LoggerService,
    useClass=LoggerServiceImpl
)

root_dashboard = Route(path="/dashboard", component=RootDashboardRoute, routeType=RouteType.WINDOW)
payment_route = Route(path="/payment", component=PaymentRoute, routeType=RouteType.WINDOW)
notification_route = Route(path="/notification", component=NotificationRoute, routeType=RouteType.WINDOW)


@NaysModule(
    providers=[
        logger_provider,
        DatabaseService,
        CacheService,
    ],
    routes=[root_dashboard],
)
class RootModule:
    pass


@NaysModule(
    providers=[PaymentService],
    routes=[payment_route],
)
class PaymentModule:
    pass


@NaysModule(
    providers=[NotificationService],
    routes=[notification_route],
)
class NotificationModule:
    pass


@NaysModule(
    providers=[logger_provider],
    imports=[PaymentModule, NotificationModule],
)
class AppModule:
    pass


# ==================== Tests ====================
class TestLoggerInjection(unittest.TestCase):
    """Test logger injection across module hierarchy"""
    
    def test_logger_available_in_root_module(self):
        """Test that logger is available in root module"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        # Get logger instance from factory
        logger = factory.get(LoggerService)
        
        # Verify logger instance is created
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, LoggerServiceImpl)
    
    def test_logger_available_across_imported_modules(self):
        """Test that logger is available across imported modules"""
        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()
        
        # Get logger instance - should be available from root registration
        logger = factory.get(LoggerService)
        
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, LoggerServiceImpl)
    
    def test_logger_service_can_log_messages(self):
        """Test that logger service can log messages"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        logger = factory.get(LoggerService)
        
        # These should not raise exceptions
        try:
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            log_success = True
        except Exception as e:
            log_success = False
        
        self.assertTrue(log_success)
    
    def test_logger_has_correct_handler(self):
        """Test that logger has StreamHandler configured"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        logger = factory.get(LoggerService)
        internal_logger = logger.logger
        
        # Verify logger has handlers
        self.assertTrue(len(internal_logger.handlers) > 0)
        
        # Verify handler is StreamHandler
        handler_types = [type(h).__name__ for h in internal_logger.handlers]
        self.assertIn('StreamHandler', handler_types)
    
    def test_logger_has_color_formatter(self):
        """Test that logger uses ColorFormatter"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        logger = factory.get(LoggerService)
        internal_logger = logger.logger
        
        # Get first handler and its formatter
        handler = internal_logger.handlers[0]
        formatter = handler.formatter
        
        # Verify formatter exists
        self.assertIsNotNone(formatter)
        
        # Verify format contains expected parts
        format_str = formatter._fmt
        self.assertIn('[%(name)s]', format_str)
        self.assertIn('[%(levelname)s]', format_str)
        self.assertIn('%(message)s', format_str)
    
    def test_logger_service_impl_creates_logger_with_classname(self):
        """Test that LoggerServiceImpl creates logger with class name"""
        impl = LoggerServiceImpl()
        
        # Verify logger name matches class name
        self.assertEqual(impl.logger.name, 'LoggerServiceImpl')
    
    def test_multiple_modules_share_same_logger_provider(self):
        """Test that multiple modules can share the same logger provider"""
        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()
        
        # Get all registered providers
        routes = factory.getRoutes()
        
        # Verify AppModule's imported modules' routes are registered
        # (RootModule's route is not imported unless RootModule is included)
        self.assertIn('/payment', routes)
        self.assertIn('/notification', routes)
        
        # All routes should be available
        self.assertTrue(len(routes) >= 2)
    
    def test_logger_propagate_is_false(self):
        """Test that logger propagate is set to False"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        logger = factory.get(LoggerService)
        internal_logger = logger.logger
        
        # Verify propagate is False
        self.assertFalse(internal_logger.propagate)
    
    def test_logger_level_is_debug(self):
        """Test that logger level is set to DEBUG"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        logger = factory.get(LoggerService)
        internal_logger = logger.logger
        
        # Verify level is DEBUG
        self.assertEqual(internal_logger.level, logging.DEBUG)
    
    def test_logger_injected_in_module_with_imports(self):
        """Test that logger is properly injected in module with imports"""
        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()
        
        # AppModule imports PaymentModule and NotificationModule
        # and all should have access to logger provider
        logger = factory.get(LoggerService)
        
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, LoggerServiceImpl)
    
    def test_root_module_services_available_with_logger(self):
        """Test that root module services are available alongside logger"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        # Get multiple services from root module
        logger = factory.get(LoggerService)
        database = factory.get(DatabaseService)
        cache = factory.get(CacheService)
        
        # All should be available
        self.assertIsNotNone(logger)
        self.assertIsNotNone(database)
        self.assertIsNotNone(cache)
        
        # Logger should be functional
        self.assertIsInstance(logger, LoggerServiceImpl)
    
    def test_payment_module_can_access_root_logger(self):
        """Test that PaymentModule can access logger from root"""
        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()
        
        # PaymentModule is imported by AppModule
        # It should have access to logger through the module hierarchy
        logger = factory.get(LoggerService)
        payment_service = factory.get(PaymentService)
        
        # Both should be available
        self.assertIsNotNone(logger)
        self.assertIsNotNone(payment_service)
    
    def test_notification_module_can_access_root_logger(self):
        """Test that NotificationModule can access logger from root"""
        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()
        
        # NotificationModule is imported by AppModule
        logger = factory.get(LoggerService)
        notification_service = factory.get(NotificationService)
        
        # Both should be available
        self.assertIsNotNone(logger)
        self.assertIsNotNone(notification_service)
    
    def test_logger_methods_return_none(self):
        """Test that logger methods don't raise exceptions"""
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()
        
        logger = factory.get(LoggerService)
        
        # All methods should complete without error
        result_debug = logger.debug("test")
        result_info = logger.info("test")
        result_warning = logger.warning("test")
        result_error = logger.error("test")
        
        # All should return None (implicit)
        self.assertIsNone(result_debug)
        self.assertIsNone(result_info)
        self.assertIsNone(result_warning)
        self.assertIsNone(result_error)


if __name__ == '__main__':
    unittest.main()
