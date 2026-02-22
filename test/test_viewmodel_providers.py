"""
Test ViewModel Providers with NaysModule - Singleton Pattern
Verifies that ViewModels can be registered as providers and used as singletons.
Demonstrates the practical pattern for ViewModel registration using @singleton from injector.
"""

import unittest
from typing import Optional

from injector import singleton
from PySide6.QtCore import QObject, Signal

from nays import ModuleFactory, NaysModule, OnInit, Provider, Route, Router, RouteType
from nays.ui.base_view_model import BaseViewModel

# ============ View Models (Singleton Providers) ============


@singleton
class UserProfileViewModel(BaseViewModel):
    """ViewModel for user profile - registered as singleton provider"""

    user_changed = Signal(dict)
    status_changed = Signal(str)

    instance_count = 0  # Track how many instances created

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        UserProfileViewModel.instance_count += 1
        self.instance_number = UserProfileViewModel.instance_count
        self.status = "created"
        self.current_user = {"name": "John Doe"}

    def onInit(self):
        """Initialize and load user"""
        self.status = "initialized"
        self.user_changed.emit(self.current_user)


@singleton
class DataListViewModel(BaseViewModel):
    """ViewModel for data list - registered as singleton provider"""

    data_changed = Signal(dict)
    status_changed = Signal(str)

    instance_count = 0  # Track how many instances created

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        DataListViewModel.instance_count += 1
        self.instance_number = DataListViewModel.instance_count
        self.status = "created"
        self.data = {"items": [1, 2, 3, 4, 5]}

    def onInit(self):
        """Initialize and load data"""
        self.status = "initialized"
        self.data_changed.emit(self.data)


@singleton
class DashboardViewModel(BaseViewModel):
    """ViewModel for dashboard - registered as singleton provider"""

    dashboard_data_changed = Signal(dict)
    status_changed = Signal(str)

    instance_count = 0  # Track how many instances created

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        DashboardViewModel.instance_count += 1
        self.instance_number = DashboardViewModel.instance_count
        self.status = "created"
        self.dashboard_data = {}

    def onInit(self):
        """Initialize dashboard"""
        self.status = "initialized"
        self.dashboard_data_changed.emit(self.dashboard_data)


# ============ View Components ============


class UserProfileView(OnInit):
    """View component using UserProfileViewModel"""

    def __init__(self, user_profile_view_model: UserProfileViewModel, routeData=None):
        self.view_model = user_profile_view_model
        self.routeData = routeData
        self.status = "created"
        self.vm_instance_number = user_profile_view_model.instance_number

    def show(self):
        pass

    def onInit(self):
        self.view_model.onInit()
        self.status = "initialized"


class DataListView(OnInit):
    """View component using DataListViewModel"""

    def __init__(self, data_list_view_model: DataListViewModel, routeData=None):
        self.view_model = data_list_view_model
        self.routeData = routeData
        self.status = "created"
        self.vm_instance_number = data_list_view_model.instance_number

    def show(self):
        pass

    def onInit(self):
        self.view_model.onInit()
        self.status = "initialized"


class DashboardView(OnInit):
    """View component using DashboardViewModel"""

    def __init__(self, dashboard_view_model: DashboardViewModel, routeData=None):
        self.view_model = dashboard_view_model
        self.routeData = routeData
        self.status = "created"
        self.vm_instance_number = dashboard_view_model.instance_number

    def show(self):
        pass

    def onInit(self):
        self.view_model.onInit()
        self.status = "initialized"


# ============ Tests ============


class TestViewModelProvidersSingleton(unittest.TestCase):
    """Test ViewModels as singleton providers in NaysModule"""

    def setUp(self):
        """Reset instance counts before each test"""
        UserProfileViewModel.instance_count = 0
        DataListViewModel.instance_count = 0
        DashboardViewModel.instance_count = 0

    def test_single_viewmodel_provider(self):
        """Test registering single ViewModel as provider"""
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)

        @NaysModule(providers=[user_vm_provider])
        class UserModule:
            pass

        factory = ModuleFactory()
        factory.register(UserModule)
        factory.initialize()

        # Get ViewModel instance
        user_vm = factory.get(UserProfileViewModel)

        self.assertIsNotNone(user_vm)
        self.assertIsInstance(user_vm, UserProfileViewModel)
        self.assertEqual(user_vm.status, "created")
        self.assertEqual(user_vm.instance_number, 1)  # First instance

    def test_viewmodel_singleton_behavior(self):
        """Test that ViewModel provider is singleton"""
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)

        @NaysModule(providers=[user_vm_provider])
        class UserModule:
            pass

        factory = ModuleFactory()
        factory.register(UserModule)
        factory.initialize()

        # Get ViewModel instance multiple times
        user_vm_1 = factory.get(UserProfileViewModel)
        user_vm_2 = factory.get(UserProfileViewModel)
        user_vm_3 = factory.get(UserProfileViewModel)

        # All should be the same instance
        self.assertIs(user_vm_1, user_vm_2)
        self.assertIs(user_vm_2, user_vm_3)

        # All should have same instance number (1 - only one created)
        self.assertEqual(user_vm_1.instance_number, 1)
        self.assertEqual(user_vm_2.instance_number, 1)
        self.assertEqual(user_vm_3.instance_number, 1)

        # Instance count should be 1 (only created once)
        self.assertEqual(UserProfileViewModel.instance_count, 1)

    def test_multiple_viewmodel_providers(self):
        """Test registering multiple ViewModels as providers"""
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)
        data_vm_provider = Provider(provide=DataListViewModel, useClass=DataListViewModel)

        @NaysModule(providers=[user_vm_provider, data_vm_provider])
        class DashboardModule:
            pass

        factory = ModuleFactory()
        factory.register(DashboardModule)
        factory.initialize()

        # Get both ViewModels
        user_vm = factory.get(UserProfileViewModel)
        data_vm = factory.get(DataListViewModel)

        self.assertIsNotNone(user_vm)
        self.assertIsNotNone(data_vm)
        self.assertIsInstance(user_vm, UserProfileViewModel)
        self.assertIsInstance(data_vm, DataListViewModel)

        # Should be different instances
        self.assertIsNot(user_vm, data_vm)

        # Each should be singleton
        self.assertEqual(UserProfileViewModel.instance_count, 1)
        self.assertEqual(DataListViewModel.instance_count, 1)

    def test_viewmodel_provider_singleton_across_multiple_requests(self):
        """Test ViewModel singleton across multiple factory.get() calls"""
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)
        data_vm_provider = Provider(provide=DataListViewModel, useClass=DataListViewModel)

        @NaysModule(providers=[user_vm_provider, data_vm_provider])
        class DashboardModule:
            pass

        factory = ModuleFactory()
        factory.register(DashboardModule)
        factory.initialize()

        # Get ViewModels multiple times
        instances_user = [factory.get(UserProfileViewModel) for _ in range(5)]
        instances_data = [factory.get(DataListViewModel) for _ in range(5)]

        # All user VMs should be same singleton
        for vm in instances_user[1:]:
            self.assertIs(instances_user[0], vm)

        # All data VMs should be same singleton
        for vm in instances_data[1:]:
            self.assertIs(instances_data[0], vm)

        # Each only created once
        self.assertEqual(UserProfileViewModel.instance_count, 1)
        self.assertEqual(DataListViewModel.instance_count, 1)

    def test_viewmodel_provider_with_routes(self):
        """Test ViewModel provider integrated with multiple routes"""
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)

        user_route = Route(
            name="user_profile",
            path="/user-profile",
            component=UserProfileView,
            routeType=RouteType.WINDOW,
        )

        user_edit_route = Route(
            name="user_edit",
            path="/user-edit",
            component=UserProfileView,  # Same view, same ViewModel
            routeType=RouteType.WINDOW,
        )

        @NaysModule(providers=[user_vm_provider], routes=[user_route, user_edit_route])
        class UserModule:
            pass

        factory = ModuleFactory()
        factory.register(UserModule)
        factory.initialize()

        # Verify routes registered
        routes = factory.getRoutes()
        self.assertIn("/user-profile", routes)
        self.assertIn("/user-edit", routes)

        # Verify ViewModel still singleton
        user_vm_1 = factory.get(UserProfileViewModel)
        user_vm_2 = factory.get(UserProfileViewModel)
        self.assertIs(user_vm_1, user_vm_2)
        self.assertEqual(UserProfileViewModel.instance_count, 1)

    def test_viewmodel_provider_exports_for_module_hierarchy(self):
        """Test exporting ViewModel providers for other modules to use"""
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)

        @NaysModule(providers=[user_vm_provider], exports=[UserProfileViewModel])
        class UserModule:
            pass

        @NaysModule(imports=[UserModule])
        class AppModule:
            pass

        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()

        # Get ViewModel through module hierarchy
        user_vm = factory.get(UserProfileViewModel)

        self.assertIsNotNone(user_vm)
        self.assertIsInstance(user_vm, UserProfileViewModel)
        self.assertEqual(UserProfileViewModel.instance_count, 1)

    def test_viewmodel_provider_with_router_navigation(self):
        """Test ViewModels work correctly with router navigation"""
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)
        data_vm_provider = Provider(provide=DataListViewModel, useClass=DataListViewModel)

        user_route = Route(
            name="user", path="/user", component=UserProfileView, routeType=RouteType.WINDOW
        )

        data_route = Route(
            name="data", path="/data", component=DataListView, routeType=RouteType.WINDOW
        )

        @NaysModule(providers=[user_vm_provider, data_vm_provider], routes=[user_route, data_route])
        class AppModule:
            pass

        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()

        # Verify routes registered
        routes = factory.getRoutes()
        self.assertIn("/user", routes)
        self.assertIn("/data", routes)

        # Verify ViewModels are singletons across multiple gets
        user_vm_1 = factory.get(UserProfileViewModel)
        data_vm_1 = factory.get(DataListViewModel)

        user_vm_2 = factory.get(UserProfileViewModel)
        data_vm_2 = factory.get(DataListViewModel)

        # Singletons maintained
        self.assertIs(user_vm_1, user_vm_2)
        self.assertIs(data_vm_1, data_vm_2)
        self.assertEqual(UserProfileViewModel.instance_count, 1)
        self.assertEqual(DataListViewModel.instance_count, 1)

    def test_complete_app_scenario_with_viewmodel_providers(self):
        """Test complete app scenario with module hierarchy and ViewModels"""
        # User Module with ViewModel provider
        user_vm_provider = Provider(provide=UserProfileViewModel, useClass=UserProfileViewModel)

        user_route = Route(
            name="user", path="/user", component=UserProfileView, routeType=RouteType.WINDOW
        )

        @NaysModule(
            providers=[user_vm_provider], routes=[user_route], exports=[UserProfileViewModel]
        )
        class UserModule:
            pass

        # Data Module with ViewModel provider
        data_vm_provider = Provider(provide=DataListViewModel, useClass=DataListViewModel)

        data_route = Route(
            name="data", path="/data", component=DataListView, routeType=RouteType.WINDOW
        )

        @NaysModule(providers=[data_vm_provider], routes=[data_route], exports=[DataListViewModel])
        class DataModule:
            pass

        # Dashboard Module with ViewModel provider
        dashboard_vm_provider = Provider(provide=DashboardViewModel, useClass=DashboardViewModel)

        dashboard_route = Route(
            name="dashboard", path="/dashboard", component=DashboardView, routeType=RouteType.WINDOW
        )

        @NaysModule(
            imports=[UserModule, DataModule],
            providers=[dashboard_vm_provider],
            routes=[dashboard_route],
        )
        class AppModule:
            pass

        # Initialize
        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()

        # Get all ViewModels and verify singleton behavior
        user_vm_1 = factory.get(UserProfileViewModel)
        user_vm_2 = factory.get(UserProfileViewModel)

        data_vm_1 = factory.get(DataListViewModel)
        data_vm_2 = factory.get(DataListViewModel)

        dashboard_vm_1 = factory.get(DashboardViewModel)
        dashboard_vm_2 = factory.get(DashboardViewModel)

        # Verify singletons
        self.assertIs(user_vm_1, user_vm_2)
        self.assertIs(data_vm_1, data_vm_2)
        self.assertIs(dashboard_vm_1, dashboard_vm_2)

        # Each created exactly once
        self.assertEqual(UserProfileViewModel.instance_count, 1)
        self.assertEqual(DataListViewModel.instance_count, 1)
        self.assertEqual(DashboardViewModel.instance_count, 1)

        # Verify routes
        routes = factory.getRoutes()
        self.assertIn("/user", routes)
        self.assertIn("/data", routes)
        self.assertIn("/dashboard", routes)


if __name__ == "__main__":
    unittest.main()
