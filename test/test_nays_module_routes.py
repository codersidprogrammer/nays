import unittest
import sys
from typing import Type
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nays import NaysModule, NaysModuleBase, Provider, ModuleMetadata
from nays.core.route import Route, RouteType


class MockView:
    """Mock view component for testing"""
    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
    
    def show(self):
        pass
    
    def exec(self):
        pass


class TestNaysModuleWithRoutes(unittest.TestCase):
    """Test cases for NaysModule decorator with routes"""

    def test_module_with_single_route(self):
        """Test module with a single route"""
        route = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class HomeModule:
            pass

        self.assertTrue(issubclass(HomeModule, NaysModuleBase))
        self.assertEqual(len(HomeModule.routes), 1)
        self.assertEqual(HomeModule.routes[0], route)
        self.assertEqual(HomeModule.routes[0].path, '/home')
        self.assertEqual(HomeModule.routes[0].name, 'home')

    def test_module_with_multiple_routes(self):
        """Test module with multiple routes"""
        homeRoute = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        aboutRoute = Route(
            name='about',
            path='/about',
            component=MockView,
            routeType=RouteType.WIDGET
        )
        
        settingsRoute = Route(
            name='settings',
            path='/settings',
            component=MockView,
            routeType=RouteType.DIALOG
        )
        
        @NaysModule(routes=[homeRoute, aboutRoute, settingsRoute])
        class MainModule:
            pass

        self.assertEqual(len(MainModule.routes), 3)
        self.assertEqual(MainModule.routes[0].path, '/home')
        self.assertEqual(MainModule.routes[1].path, '/about')
        self.assertEqual(MainModule.routes[2].path, '/settings')

    def test_route_type_window(self):
        """Test route with WINDOW type"""
        route = Route(
            name='main_window',
            path='/main',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class WindowModule:
            pass

        self.assertEqual(WindowModule.routes[0].routeType, RouteType.WINDOW)

    def test_route_type_dialog(self):
        """Test route with DIALOG type"""
        route = Route(
            name='dialog',
            path='/dialog',
            component=MockView,
            routeType=RouteType.DIALOG
        )
        
        @NaysModule(routes=[route])
        class DialogModule:
            pass

        self.assertEqual(DialogModule.routes[0].routeType, RouteType.DIALOG)

    def test_route_type_widget(self):
        """Test route with WIDGET type"""
        route = Route(
            name='widget',
            path='/widget',
            component=MockView,
            routeType=RouteType.WIDGET
        )
        
        @NaysModule(routes=[route])
        class WidgetModule:
            pass

        self.assertEqual(WidgetModule.routes[0].routeType, RouteType.WIDGET)

    def test_module_with_routes_and_providers(self):
        """Test module with both routes and providers"""
        route = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        class UserService:
            pass
        
        provider = Provider(provide=UserService, useClass=UserService)
        
        @NaysModule(
            providers=[provider],
            routes=[route]
        )
        class FullModule:
            pass

        self.assertEqual(len(FullModule.routes), 1)
        self.assertEqual(len(FullModule.providers), 1)
        self.assertEqual(FullModule.routes[0].path, '/home')
        self.assertEqual(FullModule.providers[0], provider)

    def test_module_with_routes_and_imports(self):
        """Test module with routes and imports"""
        route = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[])
        class SharedModule:
            pass
        
        @NaysModule(
            imports=[SharedModule],
            routes=[route]
        )
        class MainModule:
            pass

        self.assertEqual(len(MainModule.routes), 1)
        self.assertEqual(len(MainModule.imports), 1)
        self.assertEqual(MainModule.imports[0], SharedModule)

    def test_module_with_routes_and_exports(self):
        """Test module with routes and exports"""
        route = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        class SharedService:
            pass
        
        @NaysModule(
            exports=[SharedService],
            routes=[route]
        )
        class ExportModule:
            pass

        self.assertEqual(len(ExportModule.routes), 1)
        self.assertEqual(len(ExportModule.exports), 1)
        self.assertEqual(ExportModule.exports[0], SharedService)

    def test_module_with_all_metadata_and_routes(self):
        """Test module with all metadata types including routes"""
        route1 = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        route2 = Route(
            name='dashboard',
            path='/dashboard',
            component=MockView,
            routeType=RouteType.WIDGET
        )
        
        @NaysModule()
        class ImportedModule:
            pass
        
        class UserService:
            pass
        
        provider = Provider(provide=UserService, useClass=UserService)
        
        @NaysModule(
            providers=[provider],
            imports=[ImportedModule],
            exports=[UserService],
            routes=[route1, route2]
        )
        class CompleteModule:
            pass

        self.assertEqual(len(CompleteModule.routes), 2)
        self.assertEqual(len(CompleteModule.providers), 1)
        self.assertEqual(len(CompleteModule.imports), 1)
        self.assertEqual(len(CompleteModule.exports), 1)
        self.assertEqual(CompleteModule.routes[0].path, '/home')
        self.assertEqual(CompleteModule.routes[1].path, '/dashboard')

    def test_route_component_instantiation(self):
        """Test that route component can be instantiated"""
        route = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class ComponentModule:
            pass

        # Verify component can be instantiated
        component_instance = ComponentModule.routes[0].component()
        self.assertIsInstance(component_instance, MockView)

    def test_routes_metadata_in_getMetadata(self):
        """Test that routes are included in getMetadata"""
        route = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class MetadataModule:
            pass

        metadata = MetadataModule.getMetadata()
        
        self.assertIsInstance(metadata, ModuleMetadata)
        self.assertEqual(len(metadata.routes), 1)
        self.assertEqual(metadata.routes[0].path, '/home')

    def test_routes_in_register_method(self):
        """Test that routes are updated via register method"""
        @NaysModule(routes=[])
        class RegisterModule:
            pass

        route = Route(
            name='new_route',
            path='/new',
            component=MockView,
            routeType=RouteType.DIALOG
        )
        
        new_metadata = ModuleMetadata(routes=[route])
        RegisterModule.register(new_metadata)
        
        self.assertEqual(len(RegisterModule.routes), 1)
        self.assertEqual(RegisterModule.routes[0].path, '/new')

    def test_multiple_modules_with_different_routes(self):
        """Test that multiple modules can have different routes"""
        homeRoute = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        settingsRoute = Route(
            name='settings',
            path='/settings',
            component=MockView,
            routeType=RouteType.DIALOG
        )
        
        @NaysModule(routes=[homeRoute])
        class HomeModule:
            pass

        @NaysModule(routes=[settingsRoute])
        class SettingsModule:
            pass

        self.assertEqual(len(HomeModule.routes), 1)
        self.assertEqual(len(SettingsModule.routes), 1)
        self.assertEqual(HomeModule.routes[0].path, '/home')
        self.assertEqual(SettingsModule.routes[0].path, '/settings')

    def test_route_name_and_path_properties(self):
        """Test route name and path properties"""
        route = Route(
            name='user_profile',
            path='/user/:id',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class RoutePropertiesModule:
            pass

        self.assertEqual(RoutePropertiesModule.routes[0].name, 'user_profile')
        self.assertEqual(RoutePropertiesModule.routes[0].path, '/user/:id')

    def test_module_routes_independence(self):
        """Test that module routes are independent"""
        route1 = Route(
            name='home',
            path='/home',
            component=MockView,
            routeType=RouteType.WINDOW
        )
        
        route2 = Route(
            name='about',
            path='/about',
            component=MockView,
            routeType=RouteType.WIDGET
        )
        
        @NaysModule(routes=[route1])
        class Module1:
            pass

        @NaysModule(routes=[route2])
        class Module2:
            pass

        # Modify Module1 routes
        Module1.routes.append(route2)
        
        # Module2 should not be affected
        self.assertEqual(len(Module1.routes), 2)
        self.assertEqual(len(Module2.routes), 1)


if __name__ == '__main__':
    unittest.main()
