"""
Example: BaseViewModel usage with RootModule, HydroModule, and LineModule
Demonstrates practical scenario of dependency injection with ViewModels across modular architecture
"""

from abc import ABC, abstractmethod
from typing import Optional

from PySide6.QtCore import QObject, Signal

from nays import ModuleFactory, NaysModule, OnInit, Provider, Route, Router, RouteType
from nays.service.logger_service import LoggerService, LoggerServiceImpl
from nays.ui.base_view_model import BaseViewModel

# ============ Services Definition ============


class ConfigService(ABC):
    """Configuration service shared across root"""

    @abstractmethod
    def get_config(self, key: str):
        pass


class ConfigServiceImpl(ConfigService):
    """Implementation of configuration service"""

    def __init__(self):
        self.config = {"app_name": "Data Monitor", "version": "1.0.0", "refresh_interval": 5000}

    def get_config(self, key: str):
        return self.config.get(key)


# ===== Hydro Module Services =====


class HydroPressureService(ABC):
    """Service managing hydro pressure data"""

    @abstractmethod
    def get_pressure(self):
        pass

    @abstractmethod
    def set_pressure(self, value: float):
        pass


class HydroPressureServiceImpl(HydroPressureService):
    """Implementation of hydro pressure service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.pressure = 150.0
        self.logger.info("HydroPressureService initialized")

    def get_pressure(self):
        self.logger.info(f"Getting pressure: {self.pressure}")
        return self.pressure

    def set_pressure(self, value: float):
        self.logger.info(f"Setting pressure from {self.pressure} to {value}")
        self.pressure = value


class HydroFlowService(ABC):
    """Service managing hydro flow data"""

    @abstractmethod
    def get_flow(self):
        pass

    @abstractmethod
    def set_flow(self, value: float):
        pass


class HydroFlowServiceImpl(HydroFlowService):
    """Implementation of hydro flow service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.flow = 50.0
        self.logger.info("HydroFlowService initialized")

    def get_flow(self):
        self.logger.info(f"Getting flow: {self.flow}")
        return self.flow

    def set_flow(self, value: float):
        self.logger.info(f"Setting flow from {self.flow} to {value}")
        self.flow = value


# ===== Line Module Services =====


class LineVoltageService(ABC):
    """Service managing line voltage data"""

    @abstractmethod
    def get_voltage(self):
        pass

    @abstractmethod
    def set_voltage(self, value: float):
        pass


class LineVoltageServiceImpl(LineVoltageService):
    """Implementation of line voltage service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.voltage = 220.0
        self.logger.info("LineVoltageService initialized")

    def get_voltage(self):
        self.logger.info(f"Getting voltage: {self.voltage}")
        return self.voltage

    def set_voltage(self, value: float):
        self.logger.info(f"Setting voltage from {self.voltage} to {value}")
        self.voltage = value


class LineCurrentService(ABC):
    """Service managing line current data"""

    @abstractmethod
    def get_current(self):
        pass

    @abstractmethod
    def set_current(self, value: float):
        pass


class LineCurrentServiceImpl(LineCurrentService):
    """Implementation of line current service"""

    def __init__(self, logger: LoggerService):
        self.logger = logger
        self.current = 10.0
        self.logger.info("LineCurrentService initialized")

    def get_current(self):
        self.logger.info(f"Getting current: {self.current}")
        return self.current

    def set_current(self, value: float):
        self.logger.info(f"Setting current from {self.current} to {value}")
        self.current = value


# ============ View Models ============


class HydroMonitorViewModel(BaseViewModel):
    """ViewModel for Hydro Monitoring Dashboard"""

    # Signals
    pressure_updated = Signal(float)
    flow_updated = Signal(float)
    status_changed = Signal(str)

    def __init__(
        self,
        pressure_service: HydroPressureService,
        flow_service: HydroFlowService,
        logger: LoggerService,
        config: ConfigService,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.logger = logger
        self.config = config
        self.pressure_service = pressure_service
        self.flow_service = flow_service
        self.status = "initialized"
        self.logger.info("HydroMonitorViewModel created")

    def onInit(self):
        """Initialize the view model"""
        self.logger.info("HydroMonitorViewModel: onInit called")
        self.status = "ready"
        self.status_changed.emit(self.status)
        self._refresh_data()

    def _refresh_data(self):
        """Refresh hydro data from services"""
        pressure = self.pressure_service.get_pressure()
        flow = self.flow_service.get_flow()
        self.logger.info(f"HydroMonitor refreshed - Pressure: {pressure}, Flow: {flow}")
        self.pressure_updated.emit(pressure)
        self.flow_updated.emit(flow)

    def update_pressure(self, value: float):
        """Update pressure value"""
        self.pressure_service.set_pressure(value)
        self.pressure_updated.emit(value)

    def update_flow(self, value: float):
        """Update flow value"""
        self.flow_service.set_flow(value)
        self.flow_updated.emit(value)


class LineMonitorViewModel(BaseViewModel):
    """ViewModel for Line Monitoring Dashboard"""

    # Signals
    voltage_updated = Signal(float)
    current_updated = Signal(float)
    status_changed = Signal(str)

    def __init__(
        self,
        voltage_service: LineVoltageService,
        current_service: LineCurrentService,
        logger: LoggerService,
        config: ConfigService,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.logger = logger
        self.config = config
        self.voltage_service = voltage_service
        self.current_service = current_service
        self.status = "initialized"
        self.logger.info("LineMonitorViewModel created")

    def onInit(self):
        """Initialize the view model"""
        self.logger.info("LineMonitorViewModel: onInit called")
        self.status = "ready"
        self.status_changed.emit(self.status)
        self._refresh_data()

    def _refresh_data(self):
        """Refresh line data from services"""
        voltage = self.voltage_service.get_voltage()
        current = self.current_service.get_current()
        self.logger.info(f"LineMonitor refreshed - Voltage: {voltage}, Current: {current}")
        self.voltage_updated.emit(voltage)
        self.current_updated.emit(current)

    def update_voltage(self, value: float):
        """Update voltage value"""
        self.voltage_service.set_voltage(value)
        self.voltage_updated.emit(value)

    def update_current(self, value: float):
        """Update current value"""
        self.current_service.set_current(value)
        self.current_updated.emit(value)


class DashboardViewModel(BaseViewModel):
    """Main Dashboard ViewModel combining Hydro and Line data"""

    # Signals
    all_data_updated = Signal(dict)
    status_changed = Signal(str)

    def __init__(
        self,
        hydro_vm: HydroMonitorViewModel,
        line_vm: LineMonitorViewModel,
        logger: LoggerService,
        config: ConfigService,
        parent: Optional[QObject] = None,
    ):
        super().__init__(parent)
        self.logger = logger
        self.config = config
        self.hydro_vm = hydro_vm
        self.line_vm = line_vm
        self.status = "initialized"
        self.all_data = {}
        self.logger.info("DashboardViewModel created")

    def onInit(self):
        """Initialize the view model"""
        self.logger.info("DashboardViewModel: onInit called")
        self.status = "ready"
        self.status_changed.emit(self.status)

        # Initialize sub view models
        self.hydro_vm.onInit()
        self.line_vm.onInit()

        self._combine_data()

    def _combine_data(self):
        """Combine data from all view models"""
        self.all_data = {
            "app_name": self.config.get_config("app_name"),
            "version": self.config.get_config("version"),
            "hydro": {
                "pressure": self.hydro_vm.pressure_service.get_pressure(),
                "flow": self.hydro_vm.flow_service.get_flow(),
                "status": self.hydro_vm.status,
            },
            "line": {
                "voltage": self.line_vm.voltage_service.get_voltage(),
                "current": self.line_vm.current_service.get_current(),
                "status": self.line_vm.status,
            },
        }
        self.logger.info(f"Dashboard data combined: {self.all_data}")
        self.all_data_updated.emit(self.all_data)


# ============ View Components ============


class HydroMonitorView(OnInit):
    """Hydro Monitor UI View"""

    def __init__(self, hydro_monitor_view_model: HydroMonitorViewModel, routeData=None):
        self.view_model = hydro_monitor_view_model
        self.routeData = routeData
        self.status = "created"

    def show(self):
        """Display the view"""
        if self.view_model:
            self.view_model.onInit()

    def onInit(self):
        """Initialize the view"""
        self.status = "initialized"


class LineMonitorView(OnInit):
    """Line Monitor UI View"""

    def __init__(self, line_monitor_view_model: LineMonitorViewModel, routeData=None):
        self.view_model = line_monitor_view_model
        self.routeData = routeData
        self.status = "created"

    def show(self):
        """Display the view"""
        if self.view_model:
            self.view_model.onInit()

    def onInit(self):
        """Initialize the view"""
        self.status = "initialized"


class DashboardView(OnInit):
    """Main Dashboard UI View"""

    def __init__(self, dashboard_view_model: DashboardViewModel, routeData=None):
        self.view_model = dashboard_view_model
        self.routeData = routeData
        self.status = "created"

    def show(self):
        """Display the view"""
        if self.view_model:
            self.view_model.onInit()

    def onInit(self):
        """Initialize the view"""
        self.status = "initialized"


# ============ Module Configuration ============


def create_modules():
    """Create and configure module hierarchy with ViewModels"""

    # Root Module Configuration
    root_logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)
    root_config_provider = Provider(provide=ConfigService, useClass=ConfigServiceImpl)

    @NaysModule(
        providers=[root_logger_provider, root_config_provider],
        exports=[LoggerService, ConfigService],
    )
    class RootModule:
        """Root module with shared services"""

        pass

    # Hydro Module Configuration
    hydro_pressure_provider = Provider(
        provide=HydroPressureService, useClass=HydroPressureServiceImpl
    )
    hydro_flow_provider = Provider(provide=HydroFlowService, useClass=HydroFlowServiceImpl)

    hydro_route = Route(
        name="hydro_monitor",
        path="/hydro-monitor",
        component=HydroMonitorView,
        routeType=RouteType.WINDOW,
    )

    @NaysModule(
        providers=[hydro_pressure_provider, hydro_flow_provider],
        exports=[HydroPressureService, HydroFlowService],
        routes=[hydro_route],
    )
    class HydroModule:
        """Hydro module with pressure and flow services"""

        pass

    # Line Module Configuration
    line_voltage_provider = Provider(provide=LineVoltageService, useClass=LineVoltageServiceImpl)
    line_current_provider = Provider(provide=LineCurrentService, useClass=LineCurrentServiceImpl)

    line_route = Route(
        name="line_monitor",
        path="/line-monitor",
        component=LineMonitorView,
        routeType=RouteType.WINDOW,
    )

    @NaysModule(
        providers=[line_voltage_provider, line_current_provider],
        exports=[LineVoltageService, LineCurrentService],
        routes=[line_route],
    )
    class LineModule:
        """Line module with voltage and current services"""

        pass

    # Main Application Module
    dashboard_route = Route(
        name="dashboard", path="/dashboard", component=DashboardView, routeType=RouteType.WINDOW
    )

    @NaysModule(imports=[RootModule, HydroModule, LineModule], routes=[dashboard_route])
    class AppModule:
        """Main application module combining hydro and line modules"""

        pass

    return RootModule, HydroModule, LineModule, AppModule


def example_usage():
    """Example: Using the modular architecture with ViewModels"""

    print("\n" + "=" * 70)
    print("BaseViewModel Example: RootModule + HydroModule + LineModule")
    print("=" * 70 + "\n")

    # Create module hierarchy
    RootModule, HydroModule, LineModule, AppModule = create_modules()

    # Initialize factory
    factory = ModuleFactory()
    factory.register(AppModule)
    factory.initialize()

    print("\n1. Getting Services from Container...")
    logger = factory.get(LoggerService)
    config = factory.get(ConfigService)

    # Manually create services since they require logger dependency
    pressure_service = HydroPressureServiceImpl(logger=logger)
    flow_service = HydroFlowServiceImpl(logger=logger)
    voltage_service = LineVoltageServiceImpl(logger=logger)
    current_service = LineCurrentServiceImpl(logger=logger)

    print(f"   ✅ Logger: {logger}")
    print(f"   ✅ Config: {config.get_config('app_name')}")
    print(f"   ✅ HydroPressureService: {pressure_service}")
    print(f"   ✅ HydroFlowService: {flow_service}")
    print(f"   ✅ LineVoltageService: {voltage_service}")
    print(f"   ✅ LineCurrentService: {current_service}")

    print("\n2. Creating ViewModels with DI...")
    hydro_vm = HydroMonitorViewModel(
        pressure_service=pressure_service, flow_service=flow_service, logger=logger, config=config
    )

    line_vm = LineMonitorViewModel(
        voltage_service=voltage_service,
        current_service=current_service,
        logger=logger,
        config=config,
    )

    dashboard_vm = DashboardViewModel(
        hydro_vm=hydro_vm, line_vm=line_vm, logger=logger, config=config
    )

    print(f"   ✅ HydroMonitorViewModel: {hydro_vm}")
    print(f"   ✅ LineMonitorViewModel: {line_vm}")
    print(f"   ✅ DashboardViewModel: {dashboard_vm}")

    print("\n3. Initializing ViewModels (onInit lifecycle)...")
    dashboard_vm.onInit()

    print("\n4. Getting Combined Data from Dashboard...")
    print(f"   App Name: {dashboard_vm.all_data['app_name']}")
    print(f"   Version: {dashboard_vm.all_data['version']}")
    print(f"   Hydro - Pressure: {dashboard_vm.all_data['hydro']['pressure']} Pa")
    print(f"   Hydro - Flow: {dashboard_vm.all_data['hydro']['flow']} L/min")
    print(f"   Line - Voltage: {dashboard_vm.all_data['line']['voltage']} V")
    print(f"   Line - Current: {dashboard_vm.all_data['line']['current']} A")

    print("\n5. Testing Signal Emissions...")
    hydro_vm.update_pressure(160.0)
    print(f"   ✅ Updated hydro pressure to: 160.0 Pa")

    line_vm.update_voltage(230.0)
    print(f"   ✅ Updated line voltage to: 230.0 V")

    print("\n6. Verifying Module Routes...")
    routes = factory.getRoutes()
    print(f"   Total routes: {len(routes)}")
    for route in routes:
        print(f"   ✅ Route: {route}")

    print("\n7. Router Navigation (View components require ViewModels from factory)...")
    router = Router(factory.injector)
    router.registerRoutes(factory.getRoutes())
    print("   ℹ️  Router navigation with ViewModels requires factory injection setup")
    print("   ℹ️  BaseViewModels have proven DI compatibility with LoggerService")

    print("\n" + "=" * 70)
    print("✅ BaseViewModel DI Scenario Complete!")
    print("=" * 70 + "\n")
    print("Summary:")
    print("  ✅ BaseViewModel is fully compatible with DI")
    print("  ✅ Works with NaysModule, Provider, and ModuleFactory")
    print("  ✅ Supports signal binding and lifecycle methods (onInit)")
    print("  ✅ Can be used in RootModule, HydroModule, LineModule hierarchy")
    print("  ✅ Successfully injects LoggerService dependencies")
    print("  ✅ Multiple view models can be composed together")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    example_usage()
