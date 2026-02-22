import sys
import unittest
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from injector import Injector

from nays import ModuleFactory, NaysModule, NaysModuleBase, Provider
from nays.core.lifecycle import OnDestroy, OnInit
from nays.core.route import Route, RouteType
from nays.core.router import Router

# ============ Root-Level Services (Available to all modules) ============


class LoggerService(ABC):
    """Logging service - available to all modules"""

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


class ConfigService(ABC):
    """Configuration service - available to all modules"""

    @abstractmethod
    def get(self, key: str):
        pass


class ConfigServiceImpl(ConfigService):
    """Config implementation"""

    def __init__(self):
        self.config = {"app_name": "Nays App", "version": "1.0.0", "debug": True}

    def get(self, key: str):
        return self.config.get(key)


# ============ HydroDynamic Module Services ============


class HydroDataService(ABC):
    """Service for handling hydro-dynamic data"""

    @abstractmethod
    def fetch_data(self):
        pass


class HydroDataServiceImpl(HydroDataService):
    """Implementation of hydro-dynamic data service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.data = {"type": "hydro", "pressure": 100, "flow": 50}

    def fetch_data(self):
        self.logger.log("HydroDynamic: Fetching data")
        return self.data


class HydroProcessingService(ABC):
    """Service for processing hydro-dynamic data"""

    @abstractmethod
    def process(self, data):
        pass


class HydroProcessingServiceImpl(HydroProcessingService):
    """Implementation of hydro-dynamic processing service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger

    def process(self, data):
        self.logger.log(f"HydroDynamic: Processing {data}")
        return {"processed": True, "result": data}


class HydroCalculationService(ABC):
    """Service for hydro-dynamic calculations"""

    @abstractmethod
    def calculate(self):
        pass


class HydroCalculationServiceImpl(HydroCalculationService):
    """Implementation of hydro-dynamic calculations"""

    def __init__(self, hydro_data: HydroDataService, logger: LoggerService):
        self.hydro_data = hydro_data
        self.logger = logger

    def calculate(self):
        self.logger.log("HydroDynamic: Performing calculations")
        data = self.hydro_data.fetch_data()
        return {"calculation": data["pressure"] * data["flow"]}


# ============ Line Module Services ============


class LineDataService(ABC):
    """Service for handling line data"""

    @abstractmethod
    def fetch_data(self):
        pass


class LineDataServiceImpl(LineDataService):
    """Implementation of line data service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.data = {"type": "line", "voltage": 220, "current": 10}

    def fetch_data(self):
        self.logger.log("Line: Fetching data")
        return self.data


class LineProcessingService(ABC):
    """Service for processing line data"""

    @abstractmethod
    def process(self, data):
        pass


class LineProcessingServiceImpl(LineProcessingService):
    """Implementation of line processing service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger

    def process(self, data):
        self.logger.log(f"Line: Processing {data}")
        return {"processed": True, "result": data}


class LineCalculationService(ABC):
    """Service for line calculations"""

    @abstractmethod
    def calculate(self):
        pass


class LineCalculationServiceImpl(LineCalculationService):
    """Implementation of line calculations"""

    def __init__(self, line_data: LineDataService, logger: LoggerService):
        self.line_data = line_data
        self.logger = logger

    def calculate(self):
        self.logger.log("Line: Performing calculations")
        data = self.line_data.fetch_data()
        return {"calculation": data["voltage"] * data["current"]}


# ============ Route Components ============


class HydroDashboardView(OnInit):
    """Hydro dashboard view - uses hydro services and root logger"""

    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.status = "idle"

    def show(self):
        pass

    def exec(self):
        pass

    def onInit(self):
        self.status = "initialized"


class LineMonitorView(OnInit):
    """Line monitor view - uses line services and root logger"""

    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.status = "idle"

    def show(self):
        pass

    def exec(self):
        pass

    def onInit(self):
        self.status = "initialized"


class MainDashboardView(OnInit):
    """Main dashboard view - uses root services"""

    def __init__(self, routeData=None):
        self.routeData = routeData
        self.view = self
        self.status = "idle"

    def show(self):
        pass

    def exec(self):
        pass

    def onInit(self):
        self.status = "initialized"


# ============ Tests ============


class TestModuleScenarioWithImports(unittest.TestCase):
    """Test scenario with RootModule importing HydroDynamic and Line modules"""

    def test_root_module_basic_setup(self):
        """Test that RootModule can be set up with basic providers"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        config_provider = Provider(provide=ConfigService, useClass=ConfigServiceImpl)

        @NaysModule(
            providers=[logger_provider, config_provider], exports=[LoggerService, ConfigService]
        )
        class RootModule:
            pass

        self.assertEqual(len(RootModule.providers), 2)
        self.assertEqual(len(RootModule.exports), 2)

    def test_hydro_module_with_own_providers(self):
        """Test HydroDynamic module with its own providers"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)
        hydro_processing_provider = Provider(
            provide=HydroProcessingService, useClass=HydroProcessingServiceImpl
        )

        @NaysModule(
            providers=[hydro_data_provider, hydro_processing_provider],
            exports=[HydroDataService, HydroProcessingService],
        )
        class HydroDynamicModule:
            pass

        self.assertEqual(len(HydroDynamicModule.providers), 2)
        self.assertEqual(len(HydroDynamicModule.exports), 2)

    def test_line_module_with_own_providers(self):
        """Test Line module with its own providers"""
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)
        line_processing_provider = Provider(
            provide=LineProcessingService, useClass=LineProcessingServiceImpl
        )

        @NaysModule(
            providers=[line_data_provider, line_processing_provider],
            exports=[LineDataService, LineProcessingService],
        )
        class LineModule:
            pass

        self.assertEqual(len(LineModule.providers), 2)
        self.assertEqual(len(LineModule.exports), 2)

    def test_root_module_imports_submodules(self):
        """Test RootModule importing HydroDynamic and Line modules"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        config_provider = Provider(provide=ConfigService, useClass=ConfigServiceImpl)

        # Hydro module
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)
        hydro_processing_provider = Provider(
            provide=HydroProcessingService, useClass=HydroProcessingServiceImpl
        )

        @NaysModule(
            providers=[hydro_data_provider, hydro_processing_provider],
            exports=[HydroDataService, HydroProcessingService],
        )
        class HydroDynamicModule:
            pass

        # Line module
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)
        line_processing_provider = Provider(
            provide=LineProcessingService, useClass=LineProcessingServiceImpl
        )

        @NaysModule(
            providers=[line_data_provider, line_processing_provider],
            exports=[LineDataService, LineProcessingService],
        )
        class LineModule:
            pass

        # Root module imports both
        @NaysModule(
            providers=[logger_provider, config_provider],
            imports=[HydroDynamicModule, LineModule],
            exports=[LoggerService, ConfigService],
        )
        class RootModule:
            pass

        self.assertEqual(len(RootModule.providers), 2)
        self.assertEqual(len(RootModule.imports), 2)
        self.assertEqual(len(RootModule.exports), 2)

    def test_all_providers_available_via_factory(self):
        """Test that all providers are available when registered via ModuleFactory"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        config_provider = Provider(provide=ConfigService, useClass=ConfigServiceImpl)

        # Hydro module
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)
        hydro_calc_provider = Provider(
            provide=HydroCalculationService,
            useClass=HydroCalculationServiceImpl,
            inject=[HydroDataService, LoggerService],
        )

        @NaysModule(
            providers=[hydro_data_provider, hydro_calc_provider],
            exports=[HydroDataService, HydroCalculationService],
        )
        class HydroDynamicModule:
            pass

        # Line module
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)
        line_calc_provider = Provider(
            provide=LineCalculationService,
            useClass=LineCalculationServiceImpl,
            inject=[LineDataService, LoggerService],
        )

        @NaysModule(
            providers=[line_data_provider, line_calc_provider],
            exports=[LineDataService, LineCalculationService],
        )
        class LineModule:
            pass

        # Root module
        @NaysModule(
            providers=[logger_provider, config_provider], imports=[HydroDynamicModule, LineModule]
        )
        class RootModule:
            pass

        # Register and initialize
        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Verify all providers are registered
        self.assertIn(LoggerService, factory.container.providers)
        self.assertIn(ConfigService, factory.container.providers)
        self.assertIn(HydroDataService, factory.container.providers)
        self.assertIn(LineDataService, factory.container.providers)

    def test_submodule_can_access_root_providers(self):
        """Test that submodules can use root-level providers"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)

        # Hydro module - registers in same namespace as root
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)

        @NaysModule(providers=[hydro_data_provider], exports=[HydroDataService])
        class HydroDynamicModule:
            pass

        # Line module - registers in same namespace as root
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)

        @NaysModule(providers=[line_data_provider], exports=[LineDataService])
        class LineModule:
            pass

        # Root module
        @NaysModule(providers=[logger_provider], imports=[HydroDynamicModule, LineModule])
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Get logger - should work
        logger = factory.get(LoggerService)
        self.assertIsInstance(logger, LoggerService)

        # Verify all providers are registered in the container
        self.assertIn(HydroDataService, factory.container.providers)
        self.assertIn(LineDataService, factory.container.providers)
        self.assertIn(LoggerService, factory.container.providers)

    def test_module_factory_with_routes_and_imports(self):
        """Test ModuleFactory with routes across imported modules"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        config_provider = Provider(provide=ConfigService, useClass=ConfigServiceImpl)

        # Hydro module with routes
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)
        hydro_route = Route(
            name="hydro_dashboard",
            path="/hydro",
            component=HydroDashboardView,
            routeType=RouteType.WINDOW,
        )

        @NaysModule(
            providers=[hydro_data_provider], exports=[HydroDataService], routes=[hydro_route]
        )
        class HydroDynamicModule:
            pass

        # Line module with routes
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)
        line_route = Route(
            name="line_monitor", path="/line", component=LineMonitorView, routeType=RouteType.WINDOW
        )

        @NaysModule(providers=[line_data_provider], exports=[LineDataService], routes=[line_route])
        class LineModule:
            pass

        # Root module with main route
        main_route = Route(
            name="main", path="/main", component=MainDashboardView, routeType=RouteType.WINDOW
        )

        @NaysModule(
            providers=[logger_provider, config_provider],
            imports=[HydroDynamicModule, LineModule],
            routes=[main_route],
        )
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Verify all routes are registered
        routes = factory.getRoutes()
        self.assertEqual(len(routes), 3)
        self.assertIn("/main", routes)
        self.assertIn("/hydro", routes)
        self.assertIn("/line", routes)

    def test_router_navigation_across_modules(self):
        """Test router navigation with routes from different modules"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)

        # Hydro module
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)
        hydro_route = Route(
            name="hydro_dashboard",
            path="/hydro",
            component=HydroDashboardView,
            routeType=RouteType.WINDOW,
        )

        @NaysModule(providers=[hydro_data_provider], routes=[hydro_route])
        class HydroDynamicModule:
            pass

        # Line module
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)
        line_route = Route(
            name="line_monitor", path="/line", component=LineMonitorView, routeType=RouteType.WINDOW
        )

        @NaysModule(providers=[line_data_provider], routes=[line_route])
        class LineModule:
            pass

        # Root module
        main_route = Route(
            name="main", path="/main", component=MainDashboardView, routeType=RouteType.WINDOW
        )

        @NaysModule(
            providers=[logger_provider],
            imports=[HydroDynamicModule, LineModule],
            routes=[main_route],
        )
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())

        # Navigate to main route
        router.navigate("/main")
        current_route = router.getCurrentRoute()
        self.assertEqual(current_route.path, "/main")

        # Navigate to hydro route
        router.navigate("/hydro")
        current_route = router.getCurrentRoute()
        self.assertEqual(current_route.path, "/hydro")

        # Navigate to line route
        router.navigate("/line")
        current_route = router.getCurrentRoute()
        self.assertEqual(current_route.path, "/line")

    def test_hydro_module_providers_only_in_hydro_routes(self):
        """Test that HydroDynamic-specific providers are registered"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)

        # Hydro module - specific services
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)
        hydro_processing_provider = Provider(
            provide=HydroProcessingService, useClass=HydroProcessingServiceImpl
        )

        @NaysModule(
            providers=[hydro_data_provider, hydro_processing_provider],
            exports=[HydroDataService, HydroProcessingService],
        )
        class HydroDynamicModule:
            pass

        # Line module
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)

        @NaysModule(providers=[line_data_provider], exports=[LineDataService])
        class LineModule:
            pass

        # Root module
        @NaysModule(providers=[logger_provider], imports=[HydroDynamicModule, LineModule])
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Verify hydro-specific providers are registered
        self.assertIn(HydroDataService, factory.container.providers)
        self.assertIn(HydroProcessingService, factory.container.providers)

        # Verify root logger is also available
        self.assertIn(LoggerService, factory.container.providers)

    def test_line_module_providers_only_in_line_routes(self):
        """Test that Line-specific providers are registered"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)

        # Hydro module
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)

        @NaysModule(providers=[hydro_data_provider], exports=[HydroDataService])
        class HydroDynamicModule:
            pass

        # Line module - specific services
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)
        line_processing_provider = Provider(
            provide=LineProcessingService, useClass=LineProcessingServiceImpl
        )

        @NaysModule(
            providers=[line_data_provider, line_processing_provider],
            exports=[LineDataService, LineProcessingService],
        )
        class LineModule:
            pass

        # Root module
        @NaysModule(providers=[logger_provider], imports=[HydroDynamicModule, LineModule])
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Verify line-specific providers are registered
        self.assertIn(LineDataService, factory.container.providers)
        self.assertIn(LineProcessingService, factory.container.providers)

        # Verify root logger is also available
        self.assertIn(LoggerService, factory.container.providers)

    def test_all_modules_share_root_logger(self):
        """Test that all modules share the same root logger instance"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)

        # Hydro module
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)

        @NaysModule(providers=[hydro_data_provider])
        class HydroDynamicModule:
            pass

        # Line module
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)

        @NaysModule(providers=[line_data_provider])
        class LineModule:
            pass

        # Root module
        @NaysModule(providers=[logger_provider], imports=[HydroDynamicModule, LineModule])
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Get logger instance
        logger = factory.get(LoggerService)
        self.assertIsInstance(logger, LoggerService)

        # Log some messages
        logger.log("Test message 1")
        logger.log("Test message 2")

        # Verify logs were recorded
        logs = logger.get_logs()
        self.assertEqual(len(logs), 2)
        self.assertIn("Test message 1", logs)
        self.assertIn("Test message 2", logs)

    def test_complex_module_hierarchy(self):
        """Test complex module hierarchy with multiple levels of imports and providers"""
        # Root providers
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        config_provider = Provider(provide=ConfigService, useClass=ConfigServiceImpl)

        # Hydro module
        hydro_data_provider = Provider(provide=HydroDataService, useClass=HydroDataServiceImpl)
        hydro_processing_provider = Provider(
            provide=HydroProcessingService, useClass=HydroProcessingServiceImpl
        )

        @NaysModule(
            providers=[hydro_data_provider, hydro_processing_provider],
            exports=[HydroDataService, HydroProcessingService],
        )
        class HydroDynamicModule:
            pass

        # Line module
        line_data_provider = Provider(provide=LineDataService, useClass=LineDataServiceImpl)
        line_processing_provider = Provider(
            provide=LineProcessingService, useClass=LineProcessingServiceImpl
        )

        @NaysModule(
            providers=[line_data_provider, line_processing_provider],
            exports=[LineDataService, LineProcessingService],
        )
        class LineModule:
            pass

        # Root module with all imports
        @NaysModule(
            providers=[logger_provider, config_provider],
            imports=[HydroDynamicModule, LineModule],
            exports=[LoggerService, ConfigService],
        )
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Verify all providers are registered
        expected_providers = [
            LoggerService,
            ConfigService,
            HydroDataService,
            HydroProcessingService,
            LineDataService,
            LineProcessingService,
        ]

        for provider in expected_providers:
            self.assertIn(provider, factory.container.providers)

        # Verify we can get root services
        logger = factory.get(LoggerService)
        config = factory.get(ConfigService)
        self.assertIsInstance(logger, LoggerService)
        self.assertIsInstance(config, ConfigService)


if __name__ == "__main__":
    unittest.main()
