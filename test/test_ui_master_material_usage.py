"""
Test for Master Material UI views with module structure.
RootModule with entry window, and two feature modules with dialogs.
All views receive route params/data when navigated.
"""

import unittest
import sys
from pathlib import Path
from abc import ABC, abstractmethod

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication

from core.module import NaysModule, Provider, ModuleFactory
from core.route import Route, RouteType
from core.router import Router
from core.lifecycle import OnInit, OnDestroy
from core.logger import setupLogger
from ui_master_material_views import (
    MasterMaterialView,
    MasterMaterialEditView,
    EntryWindowView
)

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
        self.logger = setupLogger(self)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)


# ==================== Material Services ====================
class MaterialService:
    """Service for managing material data"""
    def __init__(self):
        self.name = "MaterialService"
        self.materials = {
            "MAT001": {"id": "MAT001", "name": "Steel Pipe"},
            "MAT002": {"id": "MAT002", "name": "Aluminum Tube"}
        }
    
    def get_material(self, material_id: str):
        return self.materials.get(material_id)
    
    def list_materials(self):
        return list(self.materials.values())


class MaterialCalculationService:
    """Service for material calculations"""
    def __init__(self):
        self.name = "MaterialCalculationService"
    
    def calculate(self, parameters: dict):
        """Calculate properties from input parameters"""
        return {"calculated": True, "result": parameters}


# ==================== Routes ====================
entry_window_route = Route(
    path="/",
    component=EntryWindowView,
    routeType=RouteType.WINDOW
)

view_material_route = Route(
    path="/material/view",
    component=MasterMaterialView,
    routeType=RouteType.DIALOG
)

edit_material_route = Route(
    path="/material/edit",
    component=MasterMaterialEditView,
    routeType=RouteType.DIALOG
)


# ==================== Modules ====================
logger_provider = Provider(
    provide=LoggerService,
    useClass=LoggerServiceImpl
)


@NaysModule(
    providers=[
        logger_provider,
        MaterialService,
        MaterialCalculationService,
    ],
    routes=[view_material_route],
)
class MaterialViewModule:
    """Module for viewing material"""
    pass


@NaysModule(
    providers=[
        logger_provider,
        MaterialService,
        MaterialCalculationService,
    ],
    routes=[edit_material_route],
)
class MaterialEditModule:
    """Module for editing material"""
    pass


@NaysModule(
    providers=[logger_provider],
    routes=[entry_window_route],
    imports=[MaterialViewModule, MaterialEditModule],
)
class RootModule:
    """Root module with entry window"""
    pass


# ==================== Tests ====================
class TestMasterMaterialUIUsage(unittest.TestCase):
    """Test Master Material UI views with module structure and route params"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.factory = ModuleFactory()
        self.factory.register(RootModule)
        self.factory.initialize()
        self.router = Router(self.factory.injector)
        self.router.registerRoutes(self.factory.getRoutes())
        
        # Register router in the injector for DI into views
        self.factory.injector.binder.bind(Router, to=self.router)
    
    def test_root_module_registered(self):
        """Test that RootModule is registered"""
        routes = self.factory.getRoutes()
        
        self.assertIn("/", routes)
        self.assertEqual(routes["/"].component, EntryWindowView)
    
    def test_material_view_route_registered(self):
        """Test that material view route is registered"""
        routes = self.factory.getRoutes()
        
        self.assertIn("/material/view", routes)
        self.assertEqual(routes["/material/view"].component, MasterMaterialView)
    
    def test_material_edit_route_registered(self):
        """Test that material edit route is registered"""
        routes = self.factory.getRoutes()
        
        self.assertIn("/material/edit", routes)
        self.assertEqual(routes["/material/edit"].component, MasterMaterialEditView)
    
    def test_entry_window_view_created(self):
        """Test that EntryWindowView can be instantiated"""
        entry = EntryWindowView()
        
        self.assertIsNotNone(entry)
        self.assertIsInstance(entry, EntryWindowView)
        self.assertEqual(entry.windowTitle(), "Material Management - Entry Window")
    
    def test_master_material_view_created(self):
        """Test that MasterMaterialView can be instantiated"""
        view = MasterMaterialView()
        
        self.assertIsNotNone(view)
        self.assertIsInstance(view, MasterMaterialView)
        self.assertIn("Master Material", view.windowTitle())
    
    def test_master_material_edit_view_created(self):
        """Test that MasterMaterialEditView can be instantiated"""
        view = MasterMaterialEditView()
        
        self.assertIsNotNone(view)
        self.assertIsInstance(view, MasterMaterialEditView)
        self.assertIn("Master Material", view.windowTitle())
    
    def test_entry_window_has_lifecycle(self):
        """Test that EntryWindowView has lifecycle methods"""
        entry = EntryWindowView()
        
        self.assertTrue(hasattr(entry, 'onInit'))
        self.assertTrue(hasattr(entry, 'onDestroy'))
        self.assertTrue(callable(entry.onInit))
        self.assertTrue(callable(entry.onDestroy))
    
    def test_material_view_has_lifecycle(self):
        """Test that MasterMaterialView has lifecycle methods"""
        view = MasterMaterialView()
        
        self.assertTrue(hasattr(view, 'onInit'))
        self.assertTrue(hasattr(view, 'onDestroy'))
    
    def test_material_edit_view_has_lifecycle(self):
        """Test that MasterMaterialEditView has lifecycle methods"""
        view = MasterMaterialEditView()
        
        self.assertTrue(hasattr(view, 'onInit'))
        self.assertTrue(hasattr(view, 'onDestroy'))
    
    def test_entry_window_lifecycle_init(self):
        """Test EntryWindowView initialization lifecycle"""
        entry = EntryWindowView()
        
        self.assertFalse(entry.init_called)
        self.assertEqual(len(entry.lifecycle_events), 0)
        
        entry.onInit()
        
        self.assertTrue(entry.init_called)
        self.assertIn("init", entry.lifecycle_events)
    
    def test_entry_window_lifecycle_destroy(self):
        """Test EntryWindowView destroy lifecycle"""
        entry = EntryWindowView()
        
        entry.onDestroy()
        
        self.assertTrue(entry.destroy_called)
        self.assertIn("destroy", entry.lifecycle_events)
    
    def test_material_view_lifecycle_complete(self):
        """Test MasterMaterialView complete lifecycle cycle"""
        view = MasterMaterialView()
        
        view.onInit()
        self.assertTrue(view.init_called)
        self.assertIn("init", view.lifecycle_events)
        
        view.onDestroy()
        self.assertTrue(view.destroy_called)
        self.assertIn("destroy", view.lifecycle_events)
        self.assertEqual(view.lifecycle_events, ["init", "destroy"])
    
    def test_material_view_with_route_data(self):
        """Test MasterMaterialView receives and uses route data"""
        route_data = {"material_id": "MAT001", "material_name": "Steel Pipe"}
        view = MasterMaterialView(routeData=route_data)
        
        self.assertEqual(view.route_data, route_data)
        
        # Lifecycle hook updates the title with route data
        view.onInit()
        self.assertIn("Steel Pipe", view.windowTitle())
    
    def test_material_edit_view_with_route_data(self):
        """Test MasterMaterialEditView receives and populates route data"""
        route_data = {"material_id": "MAT001", "material_name": "Steel Pipe"}
        view = MasterMaterialEditView(routeData=route_data)
        
        self.assertEqual(view.route_data, route_data)
        self.assertEqual(view.ui.lineEditMaterialID.text(), "MAT001")
        self.assertEqual(view.ui.lineEditMaterialName.text(), "Steel Pipe")
    
    def test_entry_window_has_ui_elements(self):
        """Test that EntryWindowView has required UI elements"""
        entry = EntryWindowView()
        
        # Check that window has status label
        self.assertTrue(hasattr(entry, 'status_label'))
    
    def test_material_view_has_generated_ui(self):
        """Test that MasterMaterialView has generated UI components"""
        view = MasterMaterialView()
        
        # Check that UI is loaded
        self.assertTrue(hasattr(view, 'ui'))
        self.assertTrue(hasattr(view.ui, 'treeMaterial'))
        self.assertTrue(hasattr(view.ui, 'tableDetail'))
    
    def test_material_edit_view_has_generated_ui(self):
        """Test that MasterMaterialEditView has generated UI components"""
        view = MasterMaterialEditView()
        
        # Check that UI is loaded
        self.assertTrue(hasattr(view, 'ui'))
        self.assertTrue(hasattr(view.ui, 'lineEditMaterialID'))
        self.assertTrue(hasattr(view.ui, 'lineEditMaterialName'))
        self.assertTrue(hasattr(view.ui, 'tableInputParameters'))
        self.assertTrue(hasattr(view.ui, 'tableCalculatedParameters'))
        self.assertTrue(hasattr(view.ui, 'pbCalculate'))
    
    def test_material_service_available(self):
        """Test that MaterialService is available from factory"""
        service = self.factory.get(MaterialService)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.name, "MaterialService")
    
    def test_material_calculation_service_available(self):
        """Test that MaterialCalculationService is available"""
        service = self.factory.get(MaterialCalculationService)
        
        self.assertIsNotNone(service)
        self.assertEqual(service.name, "MaterialCalculationService")
    
    def test_logger_service_available(self):
        """Test that LoggerService is available in RootModule"""
        logger = self.factory.get(LoggerService)
        
        self.assertIsNotNone(logger)
        self.assertIsInstance(logger, LoggerServiceImpl)
    
    def test_material_service_get_material(self):
        """Test MaterialService can retrieve materials"""
        service = self.factory.get(MaterialService)
        
        material = service.get_material("MAT001")
        
        self.assertIsNotNone(material)
        self.assertEqual(material["id"], "MAT001")
        self.assertEqual(material["name"], "Steel Pipe")
    
    def test_material_service_list_materials(self):
        """Test MaterialService can list all materials"""
        service = self.factory.get(MaterialService)
        
        materials = service.list_materials()
        
        self.assertEqual(len(materials), 2)
        self.assertEqual(materials[0]["id"], "MAT001")
        self.assertEqual(materials[1]["id"], "MAT002")
    
    def test_entry_window_navigation_events(self):
        """Test that entry window can track navigation events"""
        entry = EntryWindowView()
        
        # Simulate navigation button clicks
        entry.on_view_material()
        entry.on_edit_material()
        
        self.assertIn("navigate_to_view", entry.lifecycle_events)
        self.assertIn("navigate_to_edit", entry.lifecycle_events)
    
    def test_material_edit_view_calculate_button(self):
        """Test that calculate button triggers event"""
        view = MasterMaterialEditView()
        
        # Simulate calculate button click
        view.on_calculate_clicked()
        
        self.assertIn("calculate", view.lifecycle_events)
    
    def test_module_hierarchy(self):
        """Test module hierarchy: RootModule imports MaterialViewModule and MaterialEditModule"""
        routes = self.factory.getRoutes()
        
        # All routes should be available
        self.assertEqual(len(routes), 3)  # /, /material/view, /material/edit
        
        # Entry route from root
        self.assertIn("/", routes)
        # View and edit routes from imported modules
        self.assertIn("/material/view", routes)
        self.assertIn("/material/edit", routes)
    
    def test_all_routes_have_correct_types(self):
        """Test that all routes have correct RouteType"""
        routes = self.factory.getRoutes()
        
        self.assertEqual(routes["/"].routeType, RouteType.WINDOW)
        self.assertEqual(routes["/material/view"].routeType, RouteType.DIALOG)
        self.assertEqual(routes["/material/edit"].routeType, RouteType.DIALOG)
    
    def test_route_data_persistence_across_lifecycle(self):
        """Test that route data persists through lifecycle"""
        route_data = {
            "material_id": "MAT002",
            "material_name": "Aluminum Tube",
            "metadata": {"version": 1}
        }
        view = MasterMaterialEditView(routeData=route_data)
        
        # Before lifecycle
        self.assertEqual(view.route_data, route_data)
        
        # After init
        view.onInit()
        self.assertEqual(view.route_data, route_data)
        
        # After destroy
        view.onDestroy()
        self.assertEqual(view.route_data, route_data)
    
    def test_complex_scenario_material_workflow(self):
        """Test complex scenario: View material -> Edit material -> Calculate"""
        # Get material service
        material_service = self.factory.get(MaterialService)
        
        # Step 1: Get material from service
        material = material_service.get_material("MAT001")
        route_data = {"material_id": material["id"], "material_name": material["name"]}
        
        # Step 2: Navigate to view
        view = MasterMaterialView(routeData=route_data)
        view.onInit()
        self.assertIn(material["name"], view.windowTitle())
        
        # Step 3: Navigate to edit (different route data)
        edit_view = MasterMaterialEditView(routeData=route_data)
        edit_view.onInit()
        self.assertEqual(edit_view.ui.lineEditMaterialID.text(), "MAT001")
        
        # Step 4: Calculate
        edit_view.on_calculate_clicked()
        self.assertIn("calculate", edit_view.lifecycle_events)
        
        # Step 5: Cleanup
        view.onDestroy()
        edit_view.onDestroy()
        
        self.assertEqual(view.lifecycle_events, ["init", "destroy"])
        self.assertEqual(edit_view.lifecycle_events, ["init", "calculate", "destroy"])


if __name__ == '__main__':
    unittest.main()
