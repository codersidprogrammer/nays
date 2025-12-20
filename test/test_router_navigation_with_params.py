"""
Test router.navigate() with params/routeData.
Ensures route data is properly passed to components and accessible throughout lifecycle.

This test suite bypasses router.navigate() dialog blocking by directly testing
the parameter passing mechanism at the injector level.
"""

import unittest
import sys
from pathlib import Path
from abc import ABC, abstractmethod

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication

from nays import NaysModule, Provider, ModuleFactory
from nays.core.route import Route, RouteType
from nays.core.router import Router
from nays.core.lifecycle import OnInit, OnDestroy
from nays.core.logger import setupLogger

# Create QApplication before importing views
app = QApplication.instance() or QApplication(sys.argv)


# ==================== Logger Service ====================
class LoggerService(ABC):
    """Abstract logger service interface"""
    @abstractmethod
    def log(self, message: str):
        pass


class LoggerServiceImpl(LoggerService):
    """Logger service implementation"""
    
    def __init__(self):
        self.logger = setupLogger(self)
    
    def log(self, message: str):
        self.logger.info(message)


# ==================== Test Views ====================
from nays.ui.base_dialog import BaseDialogView


class TestParamView(BaseDialogView):
    """Test view that tracks params and lifecycle"""
    
    def __init__(self, routeData: dict = {}):
        BaseDialogView.__init__(self, routeData=routeData)
        self.received_params = routeData
        self.init_called = False
        self.destroy_called = False
        self.params_at_init = None
        self.params_at_destroy = None
        
        self.setWindowTitle("Test Param View")
        self.setGeometry(100, 100, 400, 300)
    
    def onInit(self):
        """Capture params at init time"""
        self.init_called = True
        self.params_at_init = self.received_params.copy() if self.received_params else {}
    
    def onDestroy(self):
        """Capture params at destroy time"""
        self.destroy_called = True
        self.params_at_destroy = self.received_params.copy() if self.received_params else {}


# ==================== Routes ====================
test_route = Route(
    path="/test",
    component=TestParamView,
    routeType=RouteType.DIALOG
)


# ==================== Modules ====================
logger_provider = Provider(
    provide=LoggerService,
    useClass=LoggerServiceImpl
)


@NaysModule(
    providers=[logger_provider],
    routes=[test_route],
)
class TestModule:
    """Test module with test route"""
    pass


# ==================== Tests ====================
class TestRouterNavigationWithParams(unittest.TestCase):
    """Test router parameter passing via injector"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = ModuleFactory()
        self.factory.register(TestModule)
        self.factory.initialize()
        self.router = Router(self.factory.injector)
        self.router.registerRoutes(self.factory.getRoutes())
    
    def _create_instance_with_params(self, params: dict):
        """Helper to create view instance with params without calling navigate"""
        instance = self.router._Router__injector.create_object(TestParamView, {
            'routeData': params
        })
        return instance
    
    def test_route_registered(self):
        """Test that test route is registered"""
        routes = self.router._Router__routes
        self.assertIn("/test", routes)
    
    def test_create_view_without_params(self):
        """Test creating view without params"""
        instance = self._create_instance_with_params({})
        
        self.assertIsNotNone(instance)
        self.assertEqual(instance.received_params, {})
    
    def test_create_view_with_single_param(self):
        """Test creating view with single param"""
        params = {"user_id": "USER123"}
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params, params)
        self.assertEqual(instance.received_params["user_id"], "USER123")
    
    def test_create_view_with_multiple_params(self):
        """Test creating view with multiple params"""
        params = {
            "user_id": "USER123",
            "user_name": "John Doe",
            "role": "admin"
        }
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params, params)
        self.assertEqual(instance.received_params["user_id"], "USER123")
        self.assertEqual(instance.received_params["user_name"], "John Doe")
        self.assertEqual(instance.received_params["role"], "admin")
    
    def test_create_view_with_nested_params(self):
        """Test creating view with nested params"""
        params = {
            "user_id": "USER123",
            "profile": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params, params)
        self.assertEqual(instance.received_params["profile"]["name"], "John Doe")
        self.assertTrue(instance.received_params["settings"]["notifications"])
    
    def test_create_view_params_accessible(self):
        """Test that params are accessible in view instance"""
        params = {"action": "edit", "id": "123"}
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params["action"], "edit")
        self.assertEqual(instance.received_params["id"], "123")
    
    def test_view_lifecycle_onInit_receives_params(self):
        """Test that onInit receives params"""
        params = {"action": "edit", "id": "123"}
        instance = self._create_instance_with_params(params)
        
        instance.onInit()
        
        self.assertTrue(instance.init_called)
        self.assertEqual(instance.params_at_init, params)
    
    def test_view_lifecycle_onDestroy_has_access_to_params(self):
        """Test that onDestroy has access to params"""
        params = {"action": "edit", "id": "123"}
        instance = self._create_instance_with_params(params)
        
        instance.onInit()
        instance.onDestroy()
        
        self.assertTrue(instance.destroy_called)
        self.assertEqual(instance.params_at_destroy, params)
    
    def test_params_not_modified_during_lifecycle(self):
        """Test that params are not modified during lifecycle"""
        params = {"id": "123", "name": "Test"}
        instance = self._create_instance_with_params(params)
        
        original_params = params.copy()
        instance.onInit()
        instance.onDestroy()
        
        self.assertEqual(instance.received_params, original_params)
    
    def test_create_view_with_numeric_params(self):
        """Test creating view with numeric parameters"""
        params = {"count": 42, "price": 99.99, "quantity": 0}
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params["count"], 42)
        self.assertEqual(instance.received_params["price"], 99.99)
        self.assertEqual(instance.received_params["quantity"], 0)
    
    def test_create_view_with_boolean_params(self):
        """Test creating view with boolean parameters"""
        params = {"enabled": True, "visible": False, "active": True}
        instance = self._create_instance_with_params(params)
        
        self.assertTrue(instance.received_params["enabled"])
        self.assertFalse(instance.received_params["visible"])
        self.assertTrue(instance.received_params["active"])
    
    def test_create_view_with_list_params(self):
        """Test creating view with list parameters"""
        params = {"items": [1, 2, 3], "names": ["Alice", "Bob", "Charlie"]}
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params["items"], [1, 2, 3])
        self.assertEqual(instance.received_params["names"], ["Alice", "Bob", "Charlie"])
    
    def test_create_view_with_null_values(self):
        """Test creating view with null/None values in params"""
        params = {"value": None, "data": None, "field": "something"}
        instance = self._create_instance_with_params(params)
        
        self.assertIsNone(instance.received_params["value"])
        self.assertIsNone(instance.received_params["data"])
        self.assertEqual(instance.received_params["field"], "something")
    
    def test_create_view_with_special_characters(self):
        """Test creating view with special characters in string params"""
        params = {
            "name": "John's \"Data\"",
            "path": "/home/user/documents",
            "expression": "a > b && c < d"
        }
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params["name"], "John's \"Data\"")
        self.assertEqual(instance.received_params["path"], "/home/user/documents")
        self.assertEqual(instance.received_params["expression"], "a > b && c < d")
    
    def test_create_view_with_empty_string_param(self):
        """Test creating view with empty string parameter"""
        params = {"empty": "", "filled": "value"}
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params["empty"], "")
        self.assertEqual(instance.received_params["filled"], "value")
    
    def test_create_multiple_views_with_same_params(self):
        """Test creating multiple views with same params"""
        params = {"id": "SAME", "value": "consistent"}
        
        instance1 = self._create_instance_with_params(params)
        instance2 = self._create_instance_with_params(params)
        instance3 = self._create_instance_with_params(params)
        
        self.assertEqual(instance1.received_params, params)
        self.assertEqual(instance2.received_params, params)
        self.assertEqual(instance3.received_params, params)
    
    def test_create_multiple_views_with_varied_params(self):
        """Test creating multiple views with varied params"""
        params_list = [
            {"screen": 1, "width": 800},
            {"screen": 2, "width": 1024},
            {"screen": 1, "width": 800}
        ]
        
        instances = []
        for params in params_list:
            instance = self._create_instance_with_params(params)
            instances.append(instance)
            self.assertEqual(instance.received_params, params)
        
        # Verify each instance has correct params
        self.assertEqual(instances[0].received_params["screen"], 1)
        self.assertEqual(instances[1].received_params["screen"], 2)
        self.assertEqual(instances[2].received_params["screen"], 1)
    
    def test_create_view_with_large_data_structure(self):
        """Test creating view with large/complex data structures"""
        params = {
            "items": [{"id": i, "name": f"Item {i}"} for i in range(100)],
            "matrix": [[j for j in range(10)] for i in range(10)]
        }
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(len(instance.received_params["items"]), 100)
        self.assertEqual(len(instance.received_params["matrix"]), 10)
        self.assertEqual(instance.received_params["items"][0]["id"], 0)
        self.assertEqual(instance.received_params["items"][99]["id"], 99)
    
    def test_params_available_before_and_after_init(self):
        """Test that params are available before and after onInit"""
        params = {"test_id": "T123"}
        instance = self._create_instance_with_params(params)
        
        # Before init
        self.assertEqual(instance.received_params, params)
        
        # After init
        instance.onInit()
        self.assertEqual(instance.received_params, params)
        self.assertEqual(instance.params_at_init, params)
    
    def test_params_available_after_destroy(self):
        """Test that params are available after onDestroy"""
        params = {"test_id": "T123"}
        instance = self._create_instance_with_params(params)
        
        instance.onInit()
        instance.onDestroy()
        
        self.assertEqual(instance.received_params, params)
        self.assertEqual(instance.params_at_destroy, params)
    
    def test_create_view_with_mixed_type_params(self):
        """Test creating view with mixed type parameters"""
        params = {
            "string": "text",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }
        instance = self._create_instance_with_params(params)
        
        self.assertEqual(instance.received_params["string"], "text")
        self.assertEqual(instance.received_params["number"], 42)
        self.assertEqual(instance.received_params["float"], 3.14)
        self.assertTrue(instance.received_params["boolean"])
        self.assertIsNone(instance.received_params["null"])
        self.assertEqual(instance.received_params["list"], [1, 2, 3])
        self.assertEqual(instance.received_params["dict"]["key"], "value")
    
    def test_route_params_attribute_set(self):
        """Test that routeParams attribute is set on view"""
        params = {"data": "test"}
        instance = self._create_instance_with_params(params)
        
        # routeParams should be set from BaseDialogView
        self.assertTrue(hasattr(instance, 'routeParams'))
    
    def test_multiple_sequential_views_with_different_params(self):
        """Test creating multiple views sequentially with different params"""
        params_sequence = [
            {"step": 1, "data": "first"},
            {"step": 2, "data": "second"},
            {"step": 3, "data": "third"}
        ]
        
        instances = []
        for params in params_sequence:
            instance = self._create_instance_with_params(params)
            instance.onInit()
            instances.append(instance)
        
        # Verify each instance captured correct params at init
        self.assertEqual(instances[0].params_at_init["step"], 1)
        self.assertEqual(instances[1].params_at_init["step"], 2)
        self.assertEqual(instances[2].params_at_init["step"], 3)
    
    def test_invalid_route_path_raises_error(self):
        """Test that navigating to invalid route raises error"""
        with self.assertRaises(ValueError):
            self.router.navigate("/invalid_route")
    
    def test_route_exist_check(self):
        """Test checking if route exists"""
        routes = self.router._Router__routes
        
        self.assertIn("/test", routes)
        self.assertNotIn("/nonexistent", routes)
    
    def test_params_independence_between_instances(self):
        """Test that params are independent between different instances"""
        params1 = {"id": "P1", "value": 100}
        params2 = {"id": "P2", "value": 200}
        
        instance1 = self._create_instance_with_params(params1)
        instance2 = self._create_instance_with_params(params2)
        
        # Verify they have different params
        self.assertEqual(instance1.received_params["id"], "P1")
        self.assertEqual(instance2.received_params["id"], "P2")
        self.assertEqual(instance1.received_params["value"], 100)
        self.assertEqual(instance2.received_params["value"], 200)


if __name__ == '__main__':
    unittest.main()

