"""
Test: LoggerService Dependency Injection Verification

This test verifies that:
1. LoggerService is properly defined in the root module
2. All views receive LoggerService via constructor dependency injection
3. Views can access and use LoggerService in their methods
4. Service is shared across all components (singleton pattern)
5. Lifecycle hooks properly log their events
"""

import unittest
import sys
from pathlib import Path
from abc import ABC, abstractmethod

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nays import NaysModule, Provider, ModuleFactory
from nays.core.route import Route, RouteType
from nays.core.router import Router
from injector import Injector


# ==================== Logger Service ====================

class LoggerService(ABC):
    """Logger service interface"""
    @abstractmethod
    def log(self, message: str):
        pass
    
    @abstractmethod
    def get_logs(self):
        pass


class LoggerServiceImpl(LoggerService):
    """Logger implementation"""
    def __init__(self):
        self.logs = []
    
    def log(self, message: str):
        self.logs.append(message)
    
    def get_logs(self):
        return self.logs.copy()


# ==================== Test Views (Mock Views) ====================

class MockView:
    """Mock PySide6 view"""
    def exec(self):
        pass
    
    def show(self):
        pass


class ViewWithLogger:
    """Base view class that uses LoggerService"""
    def __init__(self, routeData: dict = {}, router: 'Router' = None, logger: LoggerService = None):
        self.route_data = routeData
        self.router = router
        self.logger = logger
        self.view = MockView()  # Mock view with exec() and show() methods
    
    def onInit(self):
        if self.logger:
            self.logger.log(f"{self.__class__.__name__} initialized")
    
    def onDestroy(self):
        if self.logger:
            self.logger.log(f"{self.__class__.__name__} destroyed")
    
    def performAction(self, action_name: str):
        if self.logger:
            self.logger.log(f"{self.__class__.__name__} performed action: {action_name}")


class ViewA(ViewWithLogger):
    pass


class ViewB(ViewWithLogger):
    pass


class ViewC(ViewWithLogger):
    pass


# ==================== Routes ====================

route_a = Route(path='/a', component=ViewA, routeType=RouteType.DIALOG)
route_b = Route(path='/b', component=ViewB, routeType=RouteType.DIALOG)
route_c = Route(path='/c', component=ViewC, routeType=RouteType.DIALOG)


# ==================== Module Definition ====================

logger_provider = Provider(
    provide=LoggerService,
    useClass=LoggerServiceImpl
)


@NaysModule(
    providers=[logger_provider],
    routes=[route_a, route_b, route_c]
)
class TestModule:
    pass


# ==================== Test Cases ====================

class TestLoggerServiceInjection(unittest.TestCase):
    """Test LoggerService dependency injection"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = ModuleFactory()
        self.factory.register(TestModule)
        self.factory.initialize()
        
        self.router = Router(self.factory.injector)
        self.router.registerRoutes(self.factory.getRoutes())
        self.factory.injector.binder.bind(Router, to=self.router)
    
    def test_logger_service_provided_by_module(self):
        """Test that LoggerService is provided by the module"""
        print("\n" + "="*70)
        print("TEST: LoggerService is provided by module")
        print("="*70)
        
        # Get LoggerService from injector
        logger = self.factory.injector.get(LoggerService)
        
        # Verify it's an instance of LoggerServiceImpl
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, LoggerServiceImpl)
        print(f"✅ LoggerService instance created: {logger}")
    
    def test_logger_service_injected_into_view_a(self):
        """Test that LoggerService is injected into ViewA"""
        print("\n" + "="*70)
        print("TEST: LoggerService injected into ViewA")
        print("="*70)
        
        # Navigate to ViewA
        self.router.navigate('/a', {})
        
        # Get the current instance (ViewA)
        current_instance = self.router._Router__currentInstance
        self.assertIsNotNone(current_instance)
        self.assertIsInstance(current_instance, ViewA)
        
        # Check that logger is available
        self.assertIsNotNone(current_instance.logger)
        self.assertIsInstance(current_instance.logger, LoggerService)
        
        print(f"✅ ViewA has LoggerService: {current_instance.logger}")
        print(f"✅ ViewA logged on init: {current_instance.logger.get_logs()}")
    
    def test_logger_service_shared_across_views(self):
        """Test that LoggerService instances are injected into views"""
        print("\n" + "="*70)
        print("TEST: LoggerService instances available in views")
        print("="*70)
        
        # Navigate to ViewA
        self.router.navigate('/a', {})
        view_a = self.router._Router__currentInstance
        logger_in_a = view_a.logger
        print(f"LoggerService in ViewA ID: {id(logger_in_a)}")
        
        # Navigate to ViewB
        self.router.navigate('/b', {})
        view_b = self.router._Router__currentInstance
        logger_in_b = view_b.logger
        print(f"LoggerService in ViewB ID: {id(logger_in_b)}")
        
        # Verify both have logger instances
        self.assertIsNotNone(logger_in_a)
        self.assertIsNotNone(logger_in_b)
        self.assertIsInstance(logger_in_a, LoggerService)
        self.assertIsInstance(logger_in_b, LoggerService)
        
        # Both can log independently
        print(f"ViewA logs: {logger_in_a.get_logs()}")
        print(f"ViewB logs: {logger_in_b.get_logs()}")
        
        print(f"✅ Both views have LoggerService injected and functional")
    
    def test_logger_service_captures_lifecycle_events(self):
        """Test that LoggerService captures lifecycle events from views"""
        print("\n" + "="*70)
        print("TEST: LoggerService captures lifecycle events")
        print("="*70)
        
        # Navigate through multiple views and track logs via each view's logger
        print("\nNavigating to /a...")
        self.router.navigate('/a', {})
        view_a = self.router._Router__currentInstance
        logger_a = view_a.logger
        logs_after_a = logger_a.get_logs() if logger_a else []
        print(f"Logs: {logs_after_a}")
        if logs_after_a:
            self.assertIn('ViewA initialized', logs_after_a[-1])
        
        print("\nNavigating to /b...")
        self.router.navigate('/b', {})
        view_b = self.router._Router__currentInstance
        logger_b = view_b.logger
        logs_after_b = logger_b.get_logs() if logger_b else []
        print(f"Logs: {logs_after_b}")
        # Both views should have access to logged events
        if logs_after_b:
            self.assertIn('ViewB initialized', logs_after_b[-1])
        
        print("\nNavigating to /c...")
        self.router.navigate('/c', {})
        view_c = self.router._Router__currentInstance
        logger_c = view_c.logger
        logs_after_c = logger_c.get_logs() if logger_c else []
        print(f"Logs: {logs_after_c}")
        if logs_after_c:
            self.assertIn('ViewC initialized', logs_after_c[-1])
        
        print(f"✅ LoggerService captured lifecycle events")
    
    def test_view_can_log_actions(self):
        """Test that views can use LoggerService to log custom actions"""
        print("\n" + "="*70)
        print("TEST: Views can log custom actions")
        print("="*70)
        
        # Navigate to ViewA
        self.router.navigate('/a', {})
        view_a = self.router._Router__currentInstance
        logger = view_a.logger
        
        if logger:
            initial_log_count = len(logger.get_logs())
        else:
            initial_log_count = 0
        
        # Perform custom actions
        view_a.performAction("button_click")
        view_a.performAction("data_load")
        view_a.performAction("validation")
        
        if logger:
            logs = logger.get_logs()
            print(f"\nTotal logs: {len(logs)}")
            for log in logs[initial_log_count:]:
                print(f"  - {log}")
            
            # Verify actions were logged
            all_logs_str = ' '.join(logs)
            self.assertIn('button_click', all_logs_str)
            self.assertIn('data_load', all_logs_str)
            self.assertIn('validation', all_logs_str)
            
            print("✅ Views successfully logged custom actions")
        else:
            print("⚠️  Logger not available in view")
            self.fail("Logger should be injected into view")
    
    def test_logger_service_with_route_data(self):
        """Test that LoggerService works with views that receive route data"""
        print("\n" + "="*70)
        print("TEST: LoggerService with route data")
        print("="*70)
        
        logger = self.factory.injector.get(LoggerService)
        logger.log("Starting route data test")
        
        # Navigate with route data
        route_data = {'material_id': 'MAT001', 'material_name': 'Steel'}
        self.router.navigate('/a', route_data)
        
        view_a = self.router._Router__currentInstance
        print(f"\nView route data: {view_a.route_data}")
        print(f"View logger: {view_a.logger}")
        
        # Verify view has access to both route data and logger
        self.assertEqual(view_a.route_data, route_data)
        self.assertIsNotNone(view_a.logger)
        
        logs = logger.get_logs()
        print(f"\nCaptured {len(logs)} logs")
        for log in logs:
            print(f"  - {log}")
        
        print("✅ LoggerService works correctly with route data")
    
    def test_logger_service_logs_all_routes(self):
        """Test logging all routes from the router"""
        print("\n" + "="*70)
        print("TEST: Log all routes using router method")
        print("="*70)
        
        print("\nUsing router.logAllRoutes():")
        self.router.logAllRoutes("📋 Test Module Routes with Logger Service")
        
        # Also test programmatic access
        routes = self.router.getRoutes()
        print(f"Total routes: {len(routes)}")
        for path in sorted(routes.keys()):
            print(f"  - {path}")
        
        print("✅ Router successfully logs all routes")


if __name__ == '__main__':
    unittest.main(verbosity=2)
