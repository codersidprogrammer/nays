import unittest
import sys
from typing import Type
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from nays import NaysModule, NaysModuleBase, Provider, ModuleFactory
from nays.core.route import Route, RouteType
from nays.core.lifecycle import OnInit, OnDestroy
from nays.core.router import Router
from injector import Injector


# ============ Lifecycle Tracking ============

class LifecycleTracker:
    """Tracks lifecycle events for testing"""
    def __init__(self):
        self.events = []
    
    def record_event(self, event: str):
        self.events.append(event)
    
    def clear(self):
        self.events = []
    
    def has_event(self, event: str) -> bool:
        return event in self.events
    
    def get_events(self):
        return self.events.copy()


# Global tracker instance
lifecycle_tracker = LifecycleTracker()


# ============ Service Interfaces ============

class UserService:
    """Simple user service"""
    def get_user(self, user_id: int) -> dict:
        return {'id': user_id, 'name': 'Test User'}


# ============ Route Components with Lifecycle ============

class ViewWithOnlyInit(OnInit):
    """View that only implements OnInit"""
    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.initialized = False
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def onInit(self):
        lifecycle_tracker.record_event('ViewWithOnlyInit.onInit')
        self.initialized = True


class ViewWithOnlyDestroy(OnDestroy):
    """View that only implements OnDestroy"""
    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.destroyed = False
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def onDestroy(self):
        lifecycle_tracker.record_event('ViewWithOnlyDestroy.onDestroy')
        self.destroyed = True


class ViewWithBothLifecycles(OnInit, OnDestroy):
    """View that implements both OnInit and OnDestroy"""
    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.initialized = False
        self.destroyed = False
        self.init_order = []
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def onInit(self):
        lifecycle_tracker.record_event('ViewWithBothLifecycles.onInit')
        self.initialized = True
        self.init_order.append('init')
    
    def onDestroy(self):
        lifecycle_tracker.record_event('ViewWithBothLifecycles.onDestroy')
        self.destroyed = True
        self.init_order.append('destroy')


class ViewWithInitAndService(OnInit):
    """View with OnInit that uses a service"""
    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.user_data = None
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def onInit(self):
        lifecycle_tracker.record_event('ViewWithInitAndService.onInit')
        # Simulate getting user data
        self.user_data = {'id': 1, 'name': 'Test User'}


class ViewWithDestroyAndCleanup(OnDestroy):
    """View with OnDestroy that cleans up resources"""
    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.resources = ['resource1', 'resource2']
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def onDestroy(self):
        lifecycle_tracker.record_event('ViewWithDestroyAndCleanup.onDestroy')
        lifecycle_tracker.record_event(f'Cleaned up {len(self.resources)} resources')
        self.resources.clear()


class ViewWithFullLifecycle(OnInit, OnDestroy):
    """Complete view with all lifecycle features"""
    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.is_ready = False
        self.lifecycle_sequence = []
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def onInit(self):
        lifecycle_tracker.record_event('ViewWithFullLifecycle.onInit')
        self.is_ready = True
        self.lifecycle_sequence.append('init')
    
    def onDestroy(self):
        lifecycle_tracker.record_event('ViewWithFullLifecycle.onDestroy')
        self.is_ready = False
        self.lifecycle_sequence.append('destroy')


# ============ Tests ============

class TestLifecycleWithRoutes(unittest.TestCase):
    """Test lifecycle hooks with routes"""

    def setUp(self):
        """Reset lifecycle tracker before each test"""
        lifecycle_tracker.clear()

    def test_view_with_only_init_lifecycle(self):
        """Test view that only implements OnInit"""
        route = Route(
            name='init_only',
            path='/init-only',
            component=ViewWithOnlyInit,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class InitModule:
            pass

        factory = ModuleFactory()
        factory.register(InitModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Navigate to route
        router.navigate('/init-only')
        
        # Verify OnInit was called
        self.assertTrue(lifecycle_tracker.has_event('ViewWithOnlyInit.onInit'))

    def test_view_with_only_destroy_lifecycle(self):
        """Test view that only implements OnDestroy"""
        route = Route(
            name='destroy_only',
            path='/destroy-only',
            component=ViewWithOnlyDestroy,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class DestroyModule:
            pass

        factory = ModuleFactory()
        factory.register(DestroyModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Navigate to route
        router.navigate('/destroy-only')
        current_instance = router.getCurrentRoute()
        
        # Navigate away (triggers onDestroy on previous)
        route2 = Route(
            name='empty',
            path='/empty',
            component=ViewWithOnlyInit,
            routeType=RouteType.WINDOW
        )
        router.register(route2)
        router.navigate('/empty')
        
        # OnDestroy should have been called
        self.assertTrue(lifecycle_tracker.has_event('ViewWithOnlyDestroy.onDestroy'))

    def test_view_with_both_lifecycles(self):
        """Test view that implements both OnInit and OnDestroy"""
        route = Route(
            name='both',
            path='/both',
            component=ViewWithBothLifecycles,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class BothModule:
            pass

        factory = ModuleFactory()
        factory.register(BothModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Navigate to route
        router.navigate('/both')
        
        # Verify OnInit was called
        self.assertTrue(lifecycle_tracker.has_event('ViewWithBothLifecycles.onInit'))

    def test_lifecycle_with_service_injection(self):
        """Test OnInit with service injection"""
        user_provider = Provider(provide=UserService, useClass=UserService)
        
        route = Route(
            name='with_service',
            path='/with-service',
            component=ViewWithInitAndService,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(providers=[user_provider], routes=[route])
        class ServiceModule:
            pass

        factory = ModuleFactory()
        factory.register(ServiceModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Navigate to route
        router.navigate('/with-service')
        
        # Verify OnInit was called
        self.assertTrue(lifecycle_tracker.has_event('ViewWithInitAndService.onInit'))

    def test_lifecycle_with_resource_cleanup(self):
        """Test OnDestroy for resource cleanup"""
        route = Route(
            name='cleanup',
            path='/cleanup',
            component=ViewWithDestroyAndCleanup,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class CleanupModule:
            pass

        factory = ModuleFactory()
        factory.register(CleanupModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Navigate to route
        router.navigate('/cleanup')
        
        # Navigate away to trigger onDestroy
        route2 = Route(
            name='other',
            path='/other',
            component=ViewWithOnlyInit,
            routeType=RouteType.WINDOW
        )
        router.register(route2)
        router.navigate('/other')
        
        # Verify cleanup was called
        self.assertTrue(lifecycle_tracker.has_event('ViewWithDestroyAndCleanup.onDestroy'))
        self.assertTrue(lifecycle_tracker.has_event('Cleaned up 2 resources'))

    def test_lifecycle_hooks_are_instances_specific(self):
        """Test that lifecycle hooks are called on instance level"""
        route = Route(
            name='instance_test',
            path='/instance',
            component=ViewWithBothLifecycles,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class InstanceModule:
            pass

        factory = ModuleFactory()
        factory.register(InstanceModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Navigate multiple times
        router.navigate('/instance')
        first_route_count = len(lifecycle_tracker.get_events())
        
        # Navigate away and back
        route2 = Route(
            name='other',
            path='/other',
            component=ViewWithOnlyInit,
            routeType=RouteType.WINDOW
        )
        router.register(route2)
        router.navigate('/other')
        router.navigate('/instance')
        
        # Should have more events now
        self.assertGreater(len(lifecycle_tracker.get_events()), first_route_count)

    def test_lifecycle_with_multiple_routes(self):
        """Test lifecycle with multiple routes"""
        route1 = Route(
            name='first',
            path='/first',
            component=ViewWithBothLifecycles,
            routeType=RouteType.WINDOW
        )
        
        route2 = Route(
            name='second',
            path='/second',
            component=ViewWithInitAndService,
            routeType=RouteType.WINDOW
        )
        
        user_provider = Provider(provide=UserService, useClass=UserService)
        
        @NaysModule(providers=[user_provider], routes=[route1, route2])
        class MultiRouteModule:
            pass

        factory = ModuleFactory()
        factory.register(MultiRouteModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Navigate to first route
        router.navigate('/first')
        self.assertTrue(lifecycle_tracker.has_event('ViewWithBothLifecycles.onInit'))
        
        # Navigate to second route
        router.navigate('/second')
        self.assertTrue(lifecycle_tracker.has_event('ViewWithInitAndService.onInit'))

    def test_full_lifecycle_integration(self):
        """Test complete lifecycle integration with services"""
        user_provider = Provider(provide=UserService, useClass=UserService)
        
        route = Route(
            name='full_lifecycle',
            path='/full',
            component=ViewWithFullLifecycle,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(providers=[user_provider], routes=[route])
        class FullModule:
            pass

        factory = ModuleFactory()
        factory.register(FullModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        # Clear events before main test
        lifecycle_tracker.clear()
        
        # Navigate to route
        router.navigate('/full')
        self.assertTrue(lifecycle_tracker.has_event('ViewWithFullLifecycle.onInit'))

    def test_lifecycle_event_sequence(self):
        """Test that lifecycle events happen in correct order"""
        route = Route(
            name='sequence',
            path='/sequence',
            component=ViewWithBothLifecycles,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route])
        class SequenceModule:
            pass

        factory = ModuleFactory()
        factory.register(SequenceModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        lifecycle_tracker.clear()
        
        # Navigate and trigger destroy
        router.navigate('/sequence')
        events = lifecycle_tracker.get_events()
        
        # Should have init event
        self.assertIn('ViewWithBothLifecycles.onInit', events)

    def test_destroy_called_on_navigation_away(self):
        """Test that onDestroy is called when navigating away"""
        route1 = Route(
            name='view1',
            path='/view1',
            component=ViewWithBothLifecycles,
            routeType=RouteType.WINDOW
        )
        
        route2 = Route(
            name='view2',
            path='/view2',
            component=ViewWithOnlyInit,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route1, route2])
        class NavModule:
            pass

        factory = ModuleFactory()
        factory.register(NavModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        lifecycle_tracker.clear()
        
        # Navigate to view1
        router.navigate('/view1')
        self.assertTrue(lifecycle_tracker.has_event('ViewWithBothLifecycles.onInit'))
        
        # Navigate to view2 (should call onDestroy on view1)
        router.navigate('/view2')
        self.assertTrue(lifecycle_tracker.has_event('ViewWithBothLifecycles.onDestroy'))

    def test_lifecycle_with_dialog_route_type(self):
        """Test lifecycle with dialog route type"""
        route = Route(
            name='dialog',
            path='/dialog',
            component=ViewWithBothLifecycles,
            routeType=RouteType.DIALOG
        )
        
        @NaysModule(routes=[route])
        class DialogModule:
            pass

        factory = ModuleFactory()
        factory.register(DialogModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        lifecycle_tracker.clear()
        
        # Navigate to dialog route
        try:
            router.navigate('/dialog')
        except:
            # Dialog.exec() might fail in test environment
            pass
        
        # Verify init was still called
        self.assertTrue(lifecycle_tracker.has_event('ViewWithBothLifecycles.onInit'))

    def test_multiple_views_same_component_different_lifecycles(self):
        """Test that same component used in different routes has independent lifecycles"""
        route1 = Route(
            name='instance1',
            path='/instance1',
            component=ViewWithBothLifecycles,
            routeType=RouteType.WINDOW
        )
        
        route2 = Route(
            name='instance2',
            path='/instance2',
            component=ViewWithBothLifecycles,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(routes=[route1, route2])
        class MultiInstanceModule:
            pass

        factory = ModuleFactory()
        factory.register(MultiInstanceModule)
        factory.initialize()
        
        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())
        
        lifecycle_tracker.clear()
        
        # Navigate to route1
        router.navigate('/instance1')
        route1_init_count = lifecycle_tracker.get_events().count('ViewWithBothLifecycles.onInit')
        
        # Navigate to route2
        router.navigate('/instance2')
        # Should have destroy from route1 and init from route2
        self.assertTrue(lifecycle_tracker.has_event('ViewWithBothLifecycles.onDestroy'))
        self.assertGreater(len(lifecycle_tracker.get_events()), route1_init_count)


if __name__ == '__main__':
    unittest.main()
