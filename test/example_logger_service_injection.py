"""
Example: LoggerService Dependency Injection

This demonstrates how to:
1. Define a LoggerService in the root module
2. Make it available to all views and components via dependency injection
3. Access the LoggerService in MasterMaterialView and other components
4. Log lifecycle events and user actions

IMPORTANT CONCEPTS:
- LoggerService is provided by the root module
- All imported modules and their components can access it
- The injector automatically provides dependencies to components
- Views receive LoggerService through constructor parameters
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

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
from nays.core.route import Route, RouteType
from nays.core.router import Router

# ==================== Logger Service Implementation ====================


class LoggerServiceImpl(LoggerService):
    """Logger implementation that logs to console and file"""

    def __init__(self):
        self.logs = []
        self.log("LoggerService initialized")

    def log(self, message: str):
        """Log a message to console and storage"""
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        # Print to console with color
        print(f"📝 {log_entry}")

    def get_all_logs(self):
        """Get all logs"""
        return self.logs.copy()


# ==================== Routes ====================

entry_route = Route(path="/entry", component=EntryWindowView, routeType=RouteType.WINDOW)

view_route = Route(path="/material-view", component=MasterMaterialView, routeType=RouteType.DIALOG)

edit_route = Route(
    path="/material-edit", component=MasterMaterialEditView, routeType=RouteType.DIALOG
)

# ==================== Root Module Definition ====================

logger_provider = Provider(provide=LoggerService, useClass=LoggerServiceImpl)


@NaysModule(
    providers=[logger_provider],
    routes=[entry_route, view_route, edit_route],
)
class MaterialManagementModule:
    """Root module for material management with LoggerService"""

    pass


# ==================== Main Entry Point ====================


def main():
    # Create QApplication
    app = QApplication(sys.argv)

    print("=" * 70)
    print("🚀 Starting Logger Service Dependency Injection Example")
    print("=" * 70)

    # 1. Create factory and register module
    print("\n📌 Step 1: Creating ModuleFactory and registering MaterialManagementModule...")
    factory = ModuleFactory()
    factory.register(MaterialManagementModule)
    factory.initialize()

    print("✅ Module registered with providers:")
    print("   - LoggerService (implemented by LoggerServiceImpl)")
    print("   - 3 Routes: /entry, /material-view, /material-edit")

    # 2. Create router with the factory's injector
    print("\n📌 Step 2: Creating Router and registering routes...")
    router = Router(factory.injector)
    router.registerRoutes(factory.getRoutes())

    # 3. Register router in DI container for injection into views
    factory.injector.binder.bind(Router, to=router)

    print("✅ Router created and routes registered:")
    router.logAllRoutes("All Registered Routes")

    # 4. Navigate to entry point
    print("📌 Step 3: Navigating to entry point (/entry)...")
    router.navigate("/entry", {})

    print("\n" + "=" * 70)
    print("✨ Application Started with Logger Service Injection!")
    print("=" * 70)
    print("\n📋 How Dependency Injection Works:")
    print("  1. LoggerService is defined in root module providers")
    print("  2. When navigating to routes, the injector creates components")
    print("  3. Constructor parameters are automatically resolved:")
    print("     - routeData: current route data")
    print("     - router: Router instance for navigation")
    print("     - logger: LoggerService instance (from root module)")
    print("")
    print("  4. Views can now use self.logger to log events:")
    print("     - self.logger.log('MasterMaterialView initialized')")
    print("")
    print("\n🎯 Test the DI System:")
    print("  1. Click 'View Master Material' button")
    print("     → Check console for: 'MasterMaterialView initialized...'")
    print("")
    print("  2. Click 'Edit' button")
    print("     → Check console for: 'MasterMaterialView destroyed'")
    print("     → Check console for: 'MasterMaterialEditView initialized...'")
    print("")
    print("  3. Click 'Save' button")
    print("     → Check console for lifecycle and navigation logs")
    print("")
    print("\n💡 Key Points:")
    print("  • All views receive LoggerService from root module")
    print("  • Service is shared across all components")
    print("  • Injector handles automatic dependency resolution")
    print("  • Views log their lifecycle and user actions")
    print("=" * 70)
    print("\nClose the main window to exit.\n")

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
