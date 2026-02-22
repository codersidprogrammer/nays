"""
Example: How to use Router with View Navigation

This demonstrates how to:
1. Create a module with routes
2. Register the router with the module
3. Views can then navigate themselves using self.router.navigate()

IMPORTANT: Button clicks will trigger navigation!
- Each navigation closes the previous dialog and shows the new one
- The event loop continues unblocked, allowing interactions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ==================== Logger Service ====================
from abc import ABC, abstractmethod

# Import your views
from test.ui_master_material_views import (
    EntryWindowView,
    LoggerService,
    MasterMaterialEditView,
    MasterMaterialView,
)

from PySide6.QtWidgets import QApplication

from nays import ModuleFactory, NaysModule, Provider
from nays.core.logger import setupLogger
from nays.core.route import Route, RouteType
from nays.core.router import Router


class LoggerServiceImpl(LoggerService):
    """Logger implementation"""

    def __init__(self):
        self.logs = []
        self.log("LoggerService initialized")

    def log(self, message: str):
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs.append(message)
        print(f"[{timestamp}] {message}")


# ==================== Routes ====================
entry_route = Route(path="/entry", component=EntryWindowView, routeType=RouteType.WINDOW)

view_route = Route(path="/material-view", component=MasterMaterialView, routeType=RouteType.DIALOG)

edit_route = Route(
    path="/material-edit", component=MasterMaterialEditView, routeType=RouteType.DIALOG
)

# ==================== Module Definition ====================
logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)


@NaysModule(
    providers=[logger_provider],
    routes=[entry_route, view_route, edit_route],
)
class MaterialManagementModule:
    """Module for material management with navigation"""

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

    # 3. Register router in DI container for injection into views
    factory.injector.binder.bind(Router, to=router)

    # 4. Navigate to entry point
    router.navigate("/entry", {})

    print("=" * 70)
    print("✅ Interactive Router Navigation Started!")
    print("=" * 70)
    print("\n📋 How to Test Navigation:")
    print("  1. Click 'View Master Material' button")
    print("     → Opens MasterMaterialView dialog")
    print("")
    print("  2. Click 'Edit' button in view dialog")
    print("     → Closes view, opens MasterMaterialEditView dialog")
    print("")
    print("  3. Click 'Save' button in edit dialog")
    print("     → Closes edit, reopens MasterMaterialView dialog")
    print("")
    print("  4. Click 'Back' button in view dialog")
    print("     → Closes view, returns to main window")
    print("")
    print("  5. Click 'View Master Material' again to restart")
    print("\n🔧 Key Changes from Previous Approach:")
    print("  • Dialogs now use show() instead of exec()")
    print("  • Previous dialogs are properly hidden on navigation")
    print("  • Event loop is never blocked")
    print("  • Button clicks work immediately")
    print("=" * 70)
    print("\nClose the main window to exit.\n")

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
