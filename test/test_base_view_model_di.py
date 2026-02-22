"""
Test BaseViewModel compatibility with Dependency Injection
Verifies that BaseViewModel can be used with NaysModule, dependency injection,
and signal binding in a modular architecture.
"""

import unittest
from abc import ABC, abstractmethod
from typing import Optional

from injector import inject
from PySide6.QtCore import QObject, Signal

from nays import ModuleFactory, NaysModule, OnDestroy, OnInit, Provider, Route, Router, RouteType
from nays.service.logger_service import LoggerService, LoggerServiceImpl
from nays.ui.base_view_model import BaseViewModel

# ============ Test Services ============


class DataService(ABC):
    """Base service for data management"""

    @abstractmethod
    def fetch_data(self):
        pass

    @abstractmethod
    def update_data(self, data):
        pass


class DataServiceImpl(DataService):
    """Implementation of data service"""

    @inject
    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.data = {"value": 100, "status": "ready"}

    def fetch_data(self):
        self.logger.info("DataService: Fetching data")
        return self.data

    def update_data(self, data):
        self.logger.info(f"DataService: Updating data to {data}")
        self.data = data


class HydroService(ABC):
    """Base service for hydro data"""

    @abstractmethod
    def get_hydro_data(self):
        pass


class HydroServiceImpl(HydroService):
    """Implementation of hydro service"""

    @inject
    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.hydro_data = {"pressure": 150.0, "flow": 50.0}

    def get_hydro_data(self):
        self.logger.info("HydroService: Getting hydro data")
        return self.hydro_data


class LineService(ABC):
    """Base service for line data"""

    @abstractmethod
    def get_line_data(self):
        pass


class LineServiceImpl(LineService):
    """Implementation of line service"""

    @inject
    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.line_data = {"voltage": 220.0, "current": 10.0}

    def get_line_data(self):
        self.logger.info("LineService: Getting line data")
        return self.line_data


# ============ Test ViewModels ============


class BaseTestViewModel(BaseViewModel):
    """Base test view model with DI compatibility"""

    # Signals
    data_changed = Signal(dict)
    status_changed = Signal(str)

    def __init__(self, logger: LoggerService, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.logger = logger
        self.status = "initialized"
        self.data = {}

    def onInit(self):
        """Called when view initializes"""
        self.logger.info(f"{self.__class__.__name__}: onInit called")
        self.status = "ready"
        self.status_changed.emit(self.status)


class HydroViewModel(BaseTestViewModel):
    """View model for Hydro data with DI"""

    def __init__(
        self, hydro_service: HydroService, logger: LoggerService, parent: Optional[QObject] = None
    ):
        super().__init__(logger, parent)
        self.hydro_service = hydro_service
        self._load_data()

    def _load_data(self):
        """Load hydro data from service"""
        self.data = self.hydro_service.get_hydro_data()
        self.data_changed.emit(self.data)


class LineViewModel(BaseTestViewModel):
    """View model for Line data with DI"""

    def __init__(
        self, line_service: LineService, logger: LoggerService, parent: Optional[QObject] = None
    ):
        super().__init__(logger, parent)
        self.line_service = line_service
        self._load_data()

    def _load_data(self):
        """Load line data from service"""
        self.data = self.line_service.get_line_data()
        self.data_changed.emit(self.data)


class CombinedViewModel(BaseTestViewModel):
    """View model combining multiple services"""

    def __init__(
        self,
        hydro_service: HydroService,
        line_service: LineService,
        data_service: DataService,
        logger: LoggerService,
        parent: Optional[QObject] = None,
    ):
        super().__init__(logger, parent)
        self.hydro_service = hydro_service
        self.line_service = line_service
        self.data_service = data_service
        self.combined_data = {}
        self._combine_data()

    def _combine_data(self):
        """Combine data from multiple services"""
        self.combined_data = {
            "hydro": self.hydro_service.get_hydro_data(),
            "line": self.line_service.get_line_data(),
            "data": self.data_service.fetch_data(),
        }
        self.data_changed.emit(self.combined_data)


# ============ Test Views for Routes ============


class HydroDataView(OnInit):
    """View component for hydro data"""

    def __init__(self, hydro_view_model: HydroViewModel, routeData=None):
        self.view_model = hydro_view_model
        self.routeData = routeData
        self.status = "created"

    def show(self):
        pass

    def onInit(self):
        self.view_model.onInit()
        self.status = "initialized"


class LineDataView(OnInit):
    """View component for line data"""

    def __init__(self, line_view_model: LineViewModel, routeData=None):
        self.view_model = line_view_model
        self.routeData = routeData
        self.status = "created"

    def show(self):
        pass

    def onInit(self):
        self.view_model.onInit()
        self.status = "initialized"


class DashboardView(OnInit):
    """Dashboard view combining all data"""

    def __init__(self, combined_view_model: CombinedViewModel, routeData=None):
        self.view_model = combined_view_model
        self.routeData = routeData
        self.status = "created"

    def show(self):
        pass

    def onInit(self):
        self.view_model.onInit()
        self.status = "initialized"


# ============ Module Tests ============


class TestBaseViewModelDI(unittest.TestCase):
    """Test BaseViewModel with dependency injection"""

    def test_base_view_model_creation_with_logger(self):
        """Test BaseViewModel can be created with logger via DI"""
        logger = LoggerServiceImpl()
        view_model = BaseTestViewModel(logger=logger)

        self.assertIsNotNone(view_model)
        self.assertEqual(view_model.status, "initialized")
        self.assertIsNotNone(view_model.logger)

    def test_hydro_view_model_di_resolution(self):
        """Test HydroViewModel can resolve dependencies via DI"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        hydro_provider = Provider(provide=HydroService, useClass=HydroServiceImpl)

        @NaysModule(providers=[logger_provider, hydro_provider])
        class TestModule:
            pass

        factory = ModuleFactory()
        factory.register(TestModule)
        factory.initialize()

        # Manually create view model with resolved services
        hydro_service = factory.get(HydroService)
        logger = factory.get(LoggerService)
        view_model = HydroViewModel(hydro_service=hydro_service, logger=logger)

        self.assertIsNotNone(view_model)
        self.assertIsNotNone(view_model.data)
        self.assertIn("pressure", view_model.data)
        self.assertEqual(view_model.data["pressure"], 150.0)

    def test_line_view_model_di_resolution(self):
        """Test LineViewModel can resolve dependencies via DI"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        line_provider = Provider(provide=LineService, useClass=LineServiceImpl)

        @NaysModule(providers=[logger_provider, line_provider])
        class TestModule:
            pass

        factory = ModuleFactory()
        factory.register(TestModule)
        factory.initialize()

        # Manually create view model with resolved services
        line_service = factory.get(LineService)
        logger = factory.get(LoggerService)
        view_model = LineViewModel(line_service=line_service, logger=logger)

        self.assertIsNotNone(view_model)
        self.assertIsNotNone(view_model.data)
        self.assertIn("voltage", view_model.data)
        self.assertEqual(view_model.data["voltage"], 220.0)

    def test_combined_view_model_with_multiple_services(self):
        """Test CombinedViewModel with multiple injected services"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        hydro_provider = Provider(provide=HydroService, useClass=HydroServiceImpl)
        line_provider = Provider(provide=LineService, useClass=LineServiceImpl)
        data_provider = Provider(provide=DataService, useClass=DataServiceImpl)

        @NaysModule(providers=[logger_provider, hydro_provider, line_provider, data_provider])
        class TestModule:
            pass

        factory = ModuleFactory()
        factory.register(TestModule)
        factory.initialize()

        # Manually create combined view model
        hydro_service = factory.get(HydroService)
        line_service = factory.get(LineService)
        data_service = factory.get(DataService)
        logger = factory.get(LoggerService)

        view_model = CombinedViewModel(
            hydro_service=hydro_service,
            line_service=line_service,
            data_service=data_service,
            logger=logger,
        )

        self.assertIsNotNone(view_model)
        self.assertIsNotNone(view_model.combined_data)
        self.assertIn("hydro", view_model.combined_data)
        self.assertIn("line", view_model.combined_data)
        self.assertIn("data", view_model.combined_data)

    def test_view_model_on_init_lifecycle(self):
        """Test BaseViewModel lifecycle with onInit"""
        logger = LoggerServiceImpl()
        view_model = BaseTestViewModel(logger=logger)

        self.assertEqual(view_model.status, "initialized")

        # Call onInit
        view_model.onInit()
        self.assertEqual(view_model.status, "ready")

    def test_view_model_signal_binding(self):
        """Test BaseViewModel signal binding"""
        logger = LoggerServiceImpl()
        hydro_service = HydroServiceImpl(logger=logger)
        view_model = HydroViewModel(hydro_service=hydro_service, logger=logger)

        # Test that signals exist
        self.assertTrue(hasattr(view_model, "data_changed"))
        self.assertTrue(hasattr(view_model, "status_changed"))

    def test_view_model_in_module_hierarchy(self):
        """Test ViewModels work in complete module hierarchy"""
        # Root module with logger
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)

        @NaysModule(providers=[logger_provider], exports=[LoggerService])
        class RootModule:
            pass

        # Hydro module with view model
        hydro_provider = Provider(provide=HydroService, useClass=HydroServiceImpl)

        @NaysModule(imports=[RootModule], providers=[hydro_provider], exports=[HydroService])
        class HydroModule:
            pass

        # Line module with view model
        line_provider = Provider(provide=LineService, useClass=LineServiceImpl)

        @NaysModule(imports=[RootModule], providers=[line_provider], exports=[LineService])
        class LineModule:
            pass

        # Create factory with module hierarchy
        @NaysModule(imports=[RootModule, HydroModule, LineModule])
        class MainModule:
            pass

        factory = ModuleFactory()
        factory.register(MainModule)
        factory.initialize()

        # Verify all services are available
        logger = factory.get(LoggerService)
        hydro_service = factory.get(HydroService)
        line_service = factory.get(LineService)

        self.assertIsNotNone(logger)
        self.assertIsNotNone(hydro_service)
        self.assertIsNotNone(line_service)

        # Create view models
        hydro_vm = HydroViewModel(hydro_service=hydro_service, logger=logger)
        line_vm = LineViewModel(line_service=line_service, logger=logger)

        self.assertIsNotNone(hydro_vm.data)
        self.assertIsNotNone(line_vm.data)


class TestViewModelWithRoutes(unittest.TestCase):
    """Test ViewModels integrated with Router and routes"""

    def test_hydro_view_with_view_model_in_route(self):
        """Test HydroDataView with HydroViewModel in a route"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        hydro_provider = Provider(provide=HydroService, useClass=HydroServiceImpl)

        hydro_route = Route(
            name="hydro_data", path="/hydro", component=HydroDataView, routeType=RouteType.WINDOW
        )

        @NaysModule(providers=[logger_provider, hydro_provider], routes=[hydro_route])
        class HydroModule:
            pass

        factory = ModuleFactory()
        factory.register(HydroModule)
        factory.initialize()

        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())

        # Verify route is registered
        routes = factory.getRoutes()
        self.assertIn("/hydro", routes)

    def test_line_view_with_view_model_in_route(self):
        """Test LineDataView with LineViewModel in a route"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        line_provider = Provider(provide=LineService, useClass=LineServiceImpl)

        line_route = Route(
            name="line_data", path="/line", component=LineDataView, routeType=RouteType.WINDOW
        )

        @NaysModule(providers=[logger_provider, line_provider], routes=[line_route])
        class LineModule:
            pass

        factory = ModuleFactory()
        factory.register(LineModule)
        factory.initialize()

        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())

        # Verify route is registered
        routes = factory.getRoutes()
        self.assertIn("/line", routes)

    def test_dashboard_view_with_combined_view_model(self):
        """Test DashboardView with CombinedViewModel"""
        logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
        hydro_provider = Provider(provide=HydroService, useClass=HydroServiceImpl)
        line_provider = Provider(provide=LineService, useClass=LineServiceImpl)
        data_provider = Provider(provide=DataService, useClass=DataServiceImpl)

        dashboard_route = Route(
            name="dashboard", path="/dashboard", component=DashboardView, routeType=RouteType.WINDOW
        )

        @NaysModule(
            providers=[logger_provider, hydro_provider, line_provider, data_provider],
            routes=[dashboard_route],
        )
        class DashboardModule:
            pass

        factory = ModuleFactory()
        factory.register(DashboardModule)
        factory.initialize()

        router = Router(factory.injector)
        router.registerRoutes(factory.getRoutes())

        # Verify route is registered
        routes = factory.getRoutes()
        self.assertIn("/dashboard", routes)


class TestCompleteViewModelScenario(unittest.TestCase):
    """Test complete scenario with RootModule, HydroModule, LineModule"""

    def test_complete_module_with_all_view_models(self):
        """Test complete module hierarchy with ViewModels"""
        # Root logger
        root_logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)

        # Hydro module
        hydro_service_provider = Provider(provide=HydroService, useClass=HydroServiceImpl)

        @NaysModule(providers=[hydro_service_provider], exports=[HydroService])
        class HydroModule:
            pass

        # Line module
        line_service_provider = Provider(provide=LineService, useClass=LineServiceImpl)

        @NaysModule(providers=[line_service_provider], exports=[LineService])
        class LineModule:
            pass

        # Data module
        data_service_provider = Provider(provide=DataService, useClass=DataServiceImpl)

        @NaysModule(providers=[data_service_provider], exports=[DataService])
        class DataModule:
            pass

        # Root module importing all
        @NaysModule(
            providers=[root_logger_provider],
            imports=[HydroModule, LineModule, DataModule],
            exports=[LoggerService],
        )
        class RootModule:
            pass

        factory = ModuleFactory()
        factory.register(RootModule)
        factory.initialize()

        # Get all services
        logger = factory.get(LoggerService)
        hydro_service = factory.get(HydroService)
        line_service = factory.get(LineService)
        data_service = factory.get(DataService)

        # Create all view models
        hydro_vm = HydroViewModel(hydro_service=hydro_service, logger=logger)
        line_vm = LineViewModel(line_service=line_service, logger=logger)
        combined_vm = CombinedViewModel(
            hydro_service=hydro_service,
            line_service=line_service,
            data_service=data_service,
            logger=logger,
        )

        # Verify all view models work
        self.assertIsNotNone(hydro_vm.data)
        self.assertIsNotNone(line_vm.data)
        self.assertIsNotNone(combined_vm.combined_data)

        # Verify data correctness
        self.assertIn("pressure", hydro_vm.data)
        self.assertIn("voltage", line_vm.data)
        self.assertIn("hydro", combined_vm.combined_data)
        self.assertIn("line", combined_vm.combined_data)


if __name__ == "__main__":
    unittest.main()
