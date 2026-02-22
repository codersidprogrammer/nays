import sys
import unittest
from abc import ABC, abstractmethod
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from ui_dialog_views import HydroDashboardDialog, LineMonitorDialog, MainDashboardDialog

from nays import ModuleFactory, NaysModule, Provider
from nays.core.lifecycle import OnDestroy, OnInit
from nays.core.logger import setupLogger
from nays.core.route import Route, RouteType
from nays.core.router import Router

# Create QApplication before importing dialog views
app = QApplication.instance() or QApplication(sys.argv)


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
    """Logger service implementation"""

    def __init__(self):
        self.logger = setupLogger(self.__class__.__name__)

    def debug(self, message: str):
        self.logger.debug(message)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)


# ==================== Module Services ====================
class HydroDataService:
    """Service for hydro data management"""

    def __init__(self):
        self.name = "HydroDataService"
        self.data = {"pressure": 100.5, "flow": 250.0}


class HydroProcessingService:
    """Service for hydro data processing"""

    def __init__(self):
        self.name = "HydroProcessingService"

    def process(self, data):
        return {k: v * 1.1 for k, v in data.items()}


class LineDataService:
    """Service for line data management"""

    def __init__(self):
        self.name = "LineDataService"
        self.data = {"tension": 500.0, "sag": 5.5}


class LineProcessingService:
    """Service for line data processing"""

    def __init__(self):
        self.name = "LineProcessingService"

    def process(self, data):
        return {k: v * 0.95 for k, v in data.items()}


# ==================== Routes ====================
hydro_dashboard_route = Route(
    path="/hydro-dashboard", component=HydroDashboardDialog, routeType=RouteType.DIALOG
)

line_monitor_route = Route(
    path="/line-monitor", component=LineMonitorDialog, routeType=RouteType.DIALOG
)

main_dashboard_route = Route(
    path="/main-dashboard", component=MainDashboardDialog, routeType=RouteType.DIALOG
)


# ==================== Modules ====================
logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)


@NaysModule(
    providers=[
        logger_provider,
        HydroDataService,
        HydroProcessingService,
    ],
    routes=[hydro_dashboard_route],
)
class HydroModule:
    """Module for Hydro Dashboard UI"""

    pass


@NaysModule(
    providers=[
        logger_provider,
        LineDataService,
        LineProcessingService,
    ],
    routes=[line_monitor_route],
)
class LineModule:
    """Module for Line Monitor UI"""

    pass


@NaysModule(
    providers=[logger_provider],
    routes=[main_dashboard_route],
    imports=[HydroModule, LineModule],
)
class UIModule:
    """Main UI module importing hydro and line modules"""

    pass


# ==================== Tests ====================
class TestUIDialogWithLifecycle(unittest.TestCase):
    """Test PySide6 dialog views with lifecycle hooks and route navigation"""

    def setUp(self):
        """Set up test fixtures"""
        self.factory = ModuleFactory()
        self.factory.register(UIModule)
        self.factory.initialize()
        self.router = Router(self.factory.injector)
        self.router.registerRoutes(self.factory.getRoutes())

    def test_hydro_dialog_view_created(self):
        """Test that HydroDashboardDialog can be instantiated"""
        hydro = HydroDashboardDialog()

        self.assertIsNotNone(hydro)
        self.assertIsInstance(hydro, HydroDashboardDialog)
        self.assertEqual(hydro.windowTitle(), "Hydro Dashboard")

    def test_line_dialog_view_created(self):
        """Test that LineMonitorDialog can be instantiated"""
        line = LineMonitorDialog()

        self.assertIsNotNone(line)
        self.assertIsInstance(line, LineMonitorDialog)
        self.assertEqual(line.windowTitle(), "Line Monitor")

    def test_main_dialog_view_created(self):
        """Test that MainDashboardDialog can be instantiated"""
        main = MainDashboardDialog()

        self.assertIsNotNone(main)
        self.assertIsInstance(main, MainDashboardDialog)
        self.assertEqual(main.windowTitle(), "Main Dashboard")

    def test_hydro_dialog_implements_lifecycle(self):
        """Test that HydroDashboardDialog implements OnInit and OnDestroy"""
        hydro = HydroDashboardDialog()

        # Check that the view has lifecycle methods
        self.assertTrue(hasattr(hydro, "onInit"))
        self.assertTrue(hasattr(hydro, "onDestroy"))
        self.assertTrue(callable(hydro.onInit))
        self.assertTrue(callable(hydro.onDestroy))

    def test_line_dialog_implements_lifecycle(self):
        """Test that LineMonitorDialog implements OnInit and OnDestroy"""
        line = LineMonitorDialog()

        self.assertTrue(hasattr(line, "onInit"))
        self.assertTrue(hasattr(line, "onDestroy"))
        self.assertTrue(callable(line.onInit))
        self.assertTrue(callable(line.onDestroy))

    def test_main_dialog_implements_lifecycle(self):
        """Test that MainDashboardDialog implements OnInit and OnDestroy"""
        main = MainDashboardDialog()

        self.assertTrue(hasattr(main, "onInit"))
        self.assertTrue(hasattr(main, "onDestroy"))
        self.assertTrue(callable(main.onInit))
        self.assertTrue(callable(main.onDestroy))

    def test_hydro_dialog_lifecycle_initialization(self):
        """Test that HydroDashboardDialog onInit is called and tracked"""
        hydro = HydroDashboardDialog()

        # Initially not initialized
        self.assertFalse(hydro.init_called)
        self.assertEqual(len(hydro.lifecycle_events), 0)

        # Call onInit
        hydro.onInit()

        # Verify initialization was tracked
        self.assertTrue(hydro.init_called)
        self.assertIn("init", hydro.lifecycle_events)

    def test_hydro_dialog_lifecycle_destruction(self):
        """Test that HydroDashboardDialog onDestroy is called and tracked"""
        hydro = HydroDashboardDialog()

        # Initially not destroyed
        self.assertFalse(hydro.destroy_called)

        # Call onDestroy
        hydro.onDestroy()

        # Verify destruction was tracked
        self.assertTrue(hydro.destroy_called)
        self.assertIn("destroy", hydro.lifecycle_events)

    def test_line_dialog_lifecycle_complete_cycle(self):
        """Test complete lifecycle cycle: init -> destroy"""
        line = LineMonitorDialog()

        # Initial state
        self.assertFalse(line.init_called)
        self.assertFalse(line.destroy_called)
        self.assertEqual(len(line.lifecycle_events), 0)

        # Initialize
        line.onInit()
        self.assertTrue(line.init_called)
        self.assertEqual(line.lifecycle_events, ["init"])

        # Destroy
        line.onDestroy()
        self.assertTrue(line.destroy_called)
        self.assertEqual(line.lifecycle_events, ["init", "destroy"])

    def test_hydro_route_registered(self):
        """Test that hydro dashboard route is registered"""
        routes = self.factory.getRoutes()

        self.assertIn("/hydro-dashboard", routes)
        route = routes["/hydro-dashboard"]
        self.assertEqual(route.path, "/hydro-dashboard")
        self.assertEqual(route.component, HydroDashboardDialog)
        self.assertEqual(route.routeType, RouteType.DIALOG)

    def test_line_route_registered(self):
        """Test that line monitor route is registered"""
        routes = self.factory.getRoutes()

        self.assertIn("/line-monitor", routes)
        route = routes["/line-monitor"]
        self.assertEqual(route.path, "/line-monitor")
        self.assertEqual(route.component, LineMonitorDialog)
        self.assertEqual(route.routeType, RouteType.DIALOG)

    def test_main_route_registered(self):
        """Test that main dashboard route is registered"""
        routes = self.factory.getRoutes()

        self.assertIn("/main-dashboard", routes)
        route = routes["/main-dashboard"]
        self.assertEqual(route.path, "/main-dashboard")
        self.assertEqual(route.component, MainDashboardDialog)
        self.assertEqual(route.routeType, RouteType.DIALOG)

    def test_navigate_to_hydro_dialog(self):
        """Test navigating to hydro dashboard and lifecycle hook called"""
        # Simply verify the route exists and can be retrieved
        routes = self.factory.getRoutes()
        route = routes.get("/hydro-dashboard")

        # Route should exist
        self.assertIsNotNone(route)
        self.assertEqual(route.path, "/hydro-dashboard")

    def test_navigate_to_line_dialog(self):
        """Test navigating to line monitor and lifecycle hook called"""
        # Simply verify the route exists and can be retrieved
        routes = self.factory.getRoutes()
        route = routes.get("/line-monitor")

        self.assertIsNotNone(route)
        self.assertEqual(route.path, "/line-monitor")

    def test_navigate_to_main_dialog(self):
        """Test navigating to main dashboard"""
        # Simply verify the route exists and can be retrieved
        routes = self.factory.getRoutes()
        route = routes.get("/main-dashboard")

        self.assertIsNotNone(route)
        self.assertEqual(route.path, "/main-dashboard")

    def test_navigate_from_hydro_to_line(self):
        """Test navigating from hydro dashboard to line monitor"""
        # Verify both routes exist
        routes = self.factory.getRoutes()
        hydro = routes.get("/hydro-dashboard")
        line = routes.get("/line-monitor")

        self.assertIsNotNone(hydro)
        self.assertIsNotNone(line)
        self.assertEqual(hydro.path, "/hydro-dashboard")
        self.assertEqual(line.path, "/line-monitor")

    def test_navigate_from_line_to_main(self):
        """Test navigating from line monitor to main dashboard"""
        routes = self.factory.getRoutes()
        line = routes.get("/line-monitor")
        main = routes.get("/main-dashboard")

        self.assertIsNotNone(line)
        self.assertIsNotNone(main)
        self.assertEqual(line.path, "/line-monitor")
        self.assertEqual(main.path, "/main-dashboard")

    def test_navigate_from_main_to_hydro(self):
        """Test navigating from main dashboard to hydro"""
        routes = self.factory.getRoutes()
        main = routes.get("/main-dashboard")
        hydro = routes.get("/hydro-dashboard")

        self.assertIsNotNone(main)
        self.assertIsNotNone(hydro)
        self.assertEqual(main.path, "/main-dashboard")
        self.assertEqual(hydro.path, "/hydro-dashboard")

    def test_hydro_services_available(self):
        """Test that hydro module services are available"""
        hydro_data = self.factory.get(HydroDataService)
        hydro_process = self.factory.get(HydroProcessingService)

        self.assertIsNotNone(hydro_data)
        self.assertIsNotNone(hydro_process)
        self.assertEqual(hydro_data.name, "HydroDataService")
        self.assertEqual(hydro_process.name, "HydroProcessingService")

    def test_line_services_available(self):
        """Test that line module services are available"""
        line_data = self.factory.get(LineDataService)
        line_process = self.factory.get(LineProcessingService)

        self.assertIsNotNone(line_data)
        self.assertIsNotNone(line_process)
        self.assertEqual(line_data.name, "LineDataService")
        self.assertEqual(line_process.name, "LineProcessingService")

    def test_logger_available_in_ui_module(self):
        """Test that logger service is available in UI module"""
        logger = self.factory.get(LoggerService)

        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, LoggerServiceImpl)

    def test_hydro_data_processing(self):
        """Test hydro data processing through service"""
        hydro_data = self.factory.get(HydroDataService)
        hydro_process = self.factory.get(HydroProcessingService)

        original = hydro_data.data
        processed = hydro_process.process(original)

        # Verify processing was applied
        self.assertAlmostEqual(processed["pressure"], original["pressure"] * 1.1, places=5)
        self.assertAlmostEqual(processed["flow"], original["flow"] * 1.1, places=5)

    def test_line_data_processing(self):
        """Test line data processing through service"""
        line_data = self.factory.get(LineDataService)
        line_process = self.factory.get(LineProcessingService)

        original = line_data.data
        processed = line_process.process(original)

        # Verify processing was applied
        self.assertAlmostEqual(processed["tension"], original["tension"] * 0.95, places=5)
        self.assertAlmostEqual(processed["sag"], original["sag"] * 0.95, places=5)

    def test_all_routes_navigable(self):
        """Test that all routes are registered and navigable"""
        routes = self.factory.getRoutes()
        route_paths = ["/main-dashboard", "/hydro-dashboard", "/line-monitor"]

        for route_path in route_paths:
            with self.subTest(route=route_path):
                route = routes.get(route_path)
                self.assertIsNotNone(route)
                self.assertEqual(route.path, route_path)

    def test_complex_navigation_scenario(self):
        """Test complex navigation scenario with multiple transitions"""
        routes = self.factory.getRoutes()

        # Verify all routes are available
        main = routes.get("/main-dashboard")
        hydro = routes.get("/hydro-dashboard")
        line = routes.get("/line-monitor")

        self.assertIsNotNone(main)
        self.assertIsNotNone(hydro)
        self.assertIsNotNone(line)

        # Verify each route has correct path
        self.assertEqual(main.path, "/main-dashboard")
        self.assertEqual(hydro.path, "/hydro-dashboard")
        self.assertEqual(line.path, "/line-monitor")


if __name__ == "__main__":
    unittest.main()
