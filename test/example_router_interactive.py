"""
Example: Interactive Router Navigation with UI

This demonstrates working router navigation with user interactions.
Button clicks now properly trigger navigation because dialogs use show()
instead of exec() to avoid blocking the event loop.

How to use:
  python3 example_router_interactive.py
  
Then:
  1. Click "View Master Material" → opens view dialog
  2. Click "Edit" in view → closes view, opens edit dialog
  3. Click "Save" in edit → closes edit, reopens view
  4. Click "Back" in view → closes view, returns to main window
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication
from nays import NaysModule, Provider, ModuleFactory
from nays.core.route import Route, RouteType
from nays.core.router import Router
from nays.core.logger import setupLogger

# Import your views
from test.ui_master_material_views import (
    MasterMaterialView,
    MasterMaterialEditView,
    EntryWindowView
)

# ==================== Logger Service ====================
from abc import ABC, abstractmethod


class LoggerService(ABC):
    @abstractmethod
    def log(self, message: str):
        pass


class LoggerServiceImpl(LoggerService):
    def __init__(self):
        self.logger = setupLogger(self.__class__.__name__)

    def log(self, message: str):
        self.logger.info(message)


# ==================== Routes ====================
entry_route = Route(
    path="/entry",
    component=EntryWindowView,
    routeType=RouteType.WINDOW
)

view_route = Route(
    path="/material-view",
    component=MasterMaterialView,
    routeType=RouteType.DIALOG
)

edit_route = Route(
    path="/material-edit",
    component=MasterMaterialEditView,
    routeType=RouteType.DIALOG
)

# ==================== Module Definition ====================
logger_provider = Provider(
    provide=LoggerService,
    useClass=LoggerServiceImpl
)


@NaysModule(
    providers=[logger_provider],
    routes=[entry_route, view_route, edit_route],
)
class MaterialManagementModule:
    """Module for material management with interactive navigation"""
    pass


# ==================== Main Entry Point ====================
def main():
    # Create QApplication
    app = QApplication(sys.argv)
    
    # 1. Create factory and register module
    factory = ModuleFactory()
    factory.register(MaterialManagementModule)
    factory.initialize()
    
    # 2. Create router with the factory's injector
    router = Router(factory.injector)
    router.registerRoutes(factory.getRoutes())
    
    # 3. Register router in DI container so views can receive it
    factory.injector.binder.bind(Router, to=router)
    
    # 4. Navigate to entry point
    router.navigate("/entry", {})
    
    print("=" * 70)
    print("✅ Interactive Router Navigation Started!")
    print("=" * 70)
    print("\n📋 UI Navigation Instructions:")
    print("  1. Click 'View Master Material' → opens MasterMaterialView")
    print("  2. Click 'Edit' → navigates to MasterMaterialEditView")
    print("  3. Click 'Save' → navigates back to MasterMaterialView")
    print("  4. Click 'Back' → navigates to EntryWindowView")
    print("\nKey changes from previous approach:")
    print("  • Dialogs now use show() instead of exec()")
    print("  • Button clicks work because event loop isn't blocked")
    print("  • Each navigation closes previous dialog and shows new one")
    print("=" * 70)
    print("\nClose the main window to exit.\n")
    
    # Run the application event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
