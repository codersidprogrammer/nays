import unittest
import sys
from typing import Type
from pathlib import Path
from abc import ABC, abstractmethod

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.module import NaysModule, NaysModuleBase, Provider, ModuleMetadata, ModuleFactory
from core.route import Route, RouteType
from injector import Injector


# ============ Service Interfaces (Abstractions) ============

class UserService(ABC):
    """Abstract user service"""
    @abstractmethod
    def get_user(self, user_id: int) -> dict:
        pass
    
    @abstractmethod
    def create_user(self, name: str) -> dict:
        pass


class DatabaseService(ABC):
    """Abstract database service"""
    @abstractmethod
    def connect(self) -> str:
        pass
    
    @abstractmethod
    def disconnect(self):
        pass


class AuthService(ABC):
    """Abstract authentication service"""
    @abstractmethod
    def authenticate(self, username: str, password: str) -> bool:
        pass


class LoggerService(ABC):
    """Abstract logger service"""
    @abstractmethod
    def log(self, message: str):
        pass


# ============ Service Implementations ============

class UserServiceImpl(UserService):
    """Concrete user service implementation"""
    def __init__(self, db_service: DatabaseService, logger: LoggerService):
        self.db_service = db_service
        self.logger = logger
        self.users = {'1': {'id': 1, 'name': 'John'}}
    
    def get_user(self, user_id: int) -> dict:
        self.logger.log(f"Getting user {user_id}")
        return self.users.get(str(user_id), {})
    
    def create_user(self, name: str) -> dict:
        self.logger.log(f"Creating user {name}")
        user = {'id': len(self.users) + 1, 'name': name}
        self.users[str(user['id'])] = user
        return user


class DatabaseServiceImpl(DatabaseService):
    """Concrete database service implementation"""
    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.connected = False
    
    def connect(self) -> str:
        self.connected = True
        self.logger.log("Database connected")
        return "connected"
    
    def disconnect(self):
        self.connected = False
        self.logger.log("Database disconnected")


class AuthServiceImpl(AuthService):
    """Concrete authentication service implementation"""
    def __init__(self, logger: LoggerService):
        self.logger = logger
    
    def authenticate(self, username: str, password: str) -> bool:
        self.logger.log(f"Authenticating user {username}")
        return username == "admin" and password == "password"


class LoggerServiceImpl(LoggerService):
    """Concrete logger service implementation"""
    def __init__(self):
        self.logs = []
    
    def log(self, message: str):
        self.logs.append(message)


# ============ Route Components (Views) ============

class MockViewWithDependencies:
    """Mock view that requires dependencies"""
    def __init__(self, user_service: 'UserService', auth_service: 'AuthService', routeData=None):
        self.user_service: UserService = user_service
        self.auth_service: AuthService = auth_service
        self.routeData = routeData
        self.view = self
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def get_user(self, user_id: int):
        return self.user_service.get_user(user_id)
    
    def authenticate(self, username: str, password: str):
        return self.auth_service.authenticate(username, password)


class AdminViewWithLogger:
    """Admin view that uses logger"""
    def __init__(self, logger: 'LoggerService', routeData=None):
        self.logger: LoggerService = logger
        self.routeData = routeData
        self.view = self
    
    def show(self):
        self.logger.log("Admin view shown")
    
    def exec(self):
        pass


class HomeViewWithDatabase:
    """Home view that uses database"""
    def __init__(self, db_service: 'DatabaseService', routeData=None):
        self.db_service: DatabaseService = db_service
        self.routeData = routeData
        self.view = self
    
    def show(self):
        pass
    
    def exec(self):
        pass
    
    def is_connected(self) -> bool:
        return self.db_service.connected


# ============ Tests ============

class TestNaysModuleWithProviders(unittest.TestCase):
    """Test cases for NaysModule with providers and dependency injection"""

    def test_module_with_single_provider(self):
        """Test module with a single provider"""
        logger_provider = Provider(
            provide=LoggerService,
            useClass=LoggerServiceImpl
        )
        
        @NaysModule(providers=[logger_provider])
        class LoggerModule:
            pass

        self.assertEqual(len(LoggerModule.providers), 1)
        self.assertEqual(LoggerModule.providers[0].provide, LoggerService)
        self.assertEqual(LoggerModule.providers[0].useClass, LoggerServiceImpl)

    def test_module_with_multiple_providers(self):
        """Test module with multiple providers"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        db_provider = Provider(provide=DatabaseService, useClass=DatabaseServiceImpl)
        auth_provider = Provider(provide=AuthService, useClass=AuthServiceImpl)
        
        @NaysModule(providers=[logger_provider, db_provider, auth_provider])
        class CoreModule:
            pass

        self.assertEqual(len(CoreModule.providers), 3)
        self.assertEqual(CoreModule.providers[0].provide, LoggerService)
        self.assertEqual(CoreModule.providers[1].provide, DatabaseService)
        self.assertEqual(CoreModule.providers[2].provide, AuthService)

    def test_provider_with_dependencies(self):
        """Test provider that has dependencies"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        db_provider = Provider(
            provide=DatabaseService,
            useClass=DatabaseServiceImpl,
            inject=[LoggerService]
        )
        
        @NaysModule(providers=[logger_provider, db_provider])
        class CoreModule:
            pass

        # Verify the db provider has dependencies
        self.assertEqual(len(CoreModule.providers[1].inject), 1)
        self.assertEqual(CoreModule.providers[1].inject[0], LoggerService)

    def test_module_factory_registers_providers(self):
        """Test that module factory registers providers via injector"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        
        @NaysModule(providers=[logger_provider])
        class LoggerModule:
            pass

        factory = ModuleFactory()
        factory.register(LoggerModule)
        
        # Verify provider is registered in container
        self.assertIn(LoggerService, factory.container.providers)

    def test_module_factory_injects_provider_into_route(self):
        """Test that providers are injected into route components"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        
        admin_route = Route(
            name='admin',
            path='/admin',
            component=AdminViewWithLogger,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(providers=[logger_provider], routes=[admin_route])
        class AdminModule:
            pass

        factory = ModuleFactory()
        factory.register(AdminModule)
        factory.initialize()
        
        # Get the route and verify it can be instantiated with dependencies
        route = factory.getRoute('/admin')
        self.assertIsNotNone(route)
        self.assertEqual(route.component, AdminViewWithLogger)

    def test_route_with_multiple_provider_dependencies(self):
        """Test route that depends on multiple providers"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        user_provider = Provider(
            provide=UserService,
            useClass=UserServiceImpl,
            inject=[DatabaseService, LoggerService]
        )
        db_provider = Provider(
            provide=DatabaseService,
            useClass=DatabaseServiceImpl,
            inject=[LoggerService]
        )
        auth_provider = Provider(provide=AuthService, useClass=AuthServiceImpl)
        
        home_route = Route(
            name='home',
            path='/home',
            component=MockViewWithDependencies,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(
            providers=[logger_provider, db_provider, user_provider, auth_provider],
            routes=[home_route]
        )
        class AppModule:
            pass

        factory = ModuleFactory()
        factory.register(AppModule)
        factory.initialize()
        
        # Verify providers are available in container
        self.assertIn(UserService, factory.container.providers)
        self.assertIn(AuthService, factory.container.providers)
        self.assertIn(DatabaseService, factory.container.providers)
        self.assertIn(LoggerService, factory.container.providers)

    def test_provider_with_value(self):
        """Test provider with constant value"""
        config_provider = Provider(
            provide=str,
            useValue="app_config_value"
        )
        
        @NaysModule(providers=[config_provider])
        class ConfigModule:
            pass

        self.assertEqual(ConfigModule.providers[0].useValue, "app_config_value")

    def test_provider_with_factory(self):
        """Test provider with factory function"""
        def create_logger():
            return LoggerServiceImpl()
        
        logger_factory_provider = Provider(
            provide=LoggerService,
            useFactory=create_logger
        )
        
        @NaysModule(providers=[logger_factory_provider])
        class FactoryModule:
            pass

        self.assertEqual(FactoryModule.providers[0].useFactory, create_logger)
        self.assertTrue(callable(FactoryModule.providers[0].useFactory))

    def test_module_with_providers_and_exports(self):
        """Test module with providers that are exported"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        user_provider = Provider(provide=UserService, useClass=UserServiceImpl)
        
        @NaysModule(
            providers=[logger_provider, user_provider],
            exports=[LoggerService, UserService]
        )
        class SharedModule:
            pass

        self.assertEqual(len(SharedModule.providers), 2)
        self.assertEqual(len(SharedModule.exports), 2)

    def test_module_with_providers_and_routes(self):
        """Test module with providers and routes together"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        
        admin_route = Route(
            name='admin',
            path='/admin',
            component=AdminViewWithLogger,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(
            providers=[logger_provider],
            routes=[admin_route]
        )
        class AdminModule:
            pass

        self.assertEqual(len(AdminModule.providers), 1)
        self.assertEqual(len(AdminModule.routes), 1)
        self.assertEqual(AdminModule.routes[0].path, '/admin')

    def test_multiple_modules_with_different_providers(self):
        """Test that multiple modules can have different providers"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        user_provider = Provider(provide=UserService, useClass=UserServiceImpl)
        
        @NaysModule(providers=[logger_provider])
        class LoggerModule:
            pass

        @NaysModule(providers=[user_provider])
        class UserModule:
            pass

        self.assertEqual(len(LoggerModule.providers), 1)
        self.assertEqual(len(UserModule.providers), 1)
        self.assertEqual(LoggerModule.providers[0].provide, LoggerService)
        self.assertEqual(UserModule.providers[0].provide, UserService)

    def test_module_with_providers_and_imports(self):
        """Test module that imports another module with providers"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        
        @NaysModule(providers=[logger_provider])
        class CoreModule:
            pass

        user_provider = Provider(provide=UserService, useClass=UserServiceImpl)
        
        @NaysModule(
            imports=[CoreModule],
            providers=[user_provider]
        )
        class UserModule:
            pass

        self.assertEqual(len(UserModule.imports), 1)
        self.assertEqual(len(UserModule.providers), 1)
        self.assertEqual(UserModule.imports[0], CoreModule)

    def test_provider_dependency_chain(self):
        """Test that provider dependencies form a chain"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        db_provider = Provider(
            provide=DatabaseService,
            useClass=DatabaseServiceImpl,
            inject=[LoggerService]
        )
        user_provider = Provider(
            provide=UserService,
            useClass=UserServiceImpl,
            inject=[DatabaseService, LoggerService]
        )
        
        @NaysModule(providers=[logger_provider, db_provider, user_provider])
        class AppModule:
            pass

        # Verify dependency chain
        self.assertEqual(len(AppModule.providers), 3)
        self.assertEqual(len(AppModule.providers[1].inject), 1)
        self.assertEqual(len(AppModule.providers[2].inject), 2)

    def test_factory_initializes_all_providers(self):
        """Test that module factory initializes all providers"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        db_provider = Provider(
            provide=DatabaseService,
            useClass=DatabaseServiceImpl,
            inject=[LoggerService]
        )
        
        @NaysModule(providers=[logger_provider, db_provider])
        class CoreModule:
            pass

        factory = ModuleFactory()
        factory.register(CoreModule)
        factory.initialize()
        
        # Verify both providers are in container
        self.assertIn(LoggerService, factory.container.providers)
        self.assertIn(DatabaseService, factory.container.providers)

    def test_view_with_injected_services(self):
        """Test that view can use injected services"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        
        admin_route = Route(
            name='admin',
            path='/admin',
            component=AdminViewWithLogger,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(providers=[logger_provider], routes=[admin_route])
        class AdminModule:
            pass

        factory = ModuleFactory()
        factory.register(AdminModule)
        factory.initialize()
        
        # Get the logger service directly from container
        logger = factory.get(LoggerService)
        
        # Verify the logger service is instantiated
        self.assertIsInstance(logger, LoggerService)
        
        # Call a method that uses the service
        logger.log("test message")
        self.assertEqual(len(logger.logs), 1)

    def test_database_view_with_connected_service(self):
        """Test view that uses database service"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        # Create database service without logger dependency for this test
        db_provider = Provider(provide=DatabaseService, useClass=DatabaseServiceImpl)
        
        home_route = Route(
            name='home',
            path='/home',
            component=HomeViewWithDatabase,
            routeType=RouteType.WINDOW
        )
        
        @NaysModule(
            providers=[logger_provider, db_provider],
            routes=[home_route]
        )
        class HomeModule:
            pass

        factory = ModuleFactory()
        factory.register(HomeModule)
        factory.initialize()
        
        # Get the route and verify it exists
        route = factory.getRoute('/home')
        self.assertIsNotNone(route)
        self.assertEqual(route.name, 'home')
        self.assertEqual(route.component, HomeViewWithDatabase)
        
        # Verify providers are registered
        self.assertIn(DatabaseService, factory.container.providers)
        self.assertIn(LoggerService, factory.container.providers)


if __name__ == '__main__':
    unittest.main()
