"""
Example: Using Nays Framework in External Project

This demonstrates how to use nays as an installed package
in a separate project.
"""

# After installing nays with: pip install nays
# or pip install -e /path/to/nays

from nays import (
    NaysModule,
    Provider,
    ModuleFactory,
    Route,
    RouteType,
    Router,
    OnInit,
    OnDestroy,
    BaseDialogView,
    BaseWindowView,
)
from PySide6.QtWidgets import QApplication, QVBoxLayout, QLabel, QPushButton


# ==================== Services ====================
class GreetingService:
    """Example service"""
    def __init__(self):
        self.message = "Hello from Nays Framework!"
    
    def greet(self, name: str):
        return f"{self.message} Welcome, {name}!"


# ==================== Views ====================
class MainWindow(BaseWindowView):
    """Main application window"""
    
    def __init__(self, routeData: dict = {}, router: 'Router' = None):
        super().__init__(routeData=routeData)
        self.router = router
        
        self.setWindowTitle("Nays External Project Example")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Welcome to Nays Framework!"))
        
        btn = QPushButton("Open Dialog")
        btn.clicked.connect(self.open_dialog)
        layout.addWidget(btn)
        
        self.setCentralWidget(self)
    
    def open_dialog(self):
        if self.router:
            self.router.navigate('/dialog', {'name': 'User'})


class DialogWindow(BaseDialogView):
    """Example dialog"""
    
    def __init__(self, routeData: dict = {}, router: 'Router' = None):
        super().__init__(routeData=routeData)
        self.router = router
        
        self.setWindowTitle("Dialog Window")
        self.setGeometry(150, 150, 300, 200)
        
        layout = QVBoxLayout(self)
        name = routeData.get('name', 'Guest')
        layout.addWidget(QLabel(f"Hello, {name}!"))
        
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)
        
        self.setLayout(layout)
    
    def onInit(self):
        print("Dialog initialized")
    
    def onDestroy(self):
        print("Dialog destroyed")


# ==================== Modules ====================
@NaysModule(
    providers=[
        Provider(GreetingService, useClass=GreetingService),
    ],
    routes=[
        Route(path="/", component=MainWindow, routeType=RouteType.WINDOW),
        Route(path="/dialog", component=DialogWindow, routeType=RouteType.DIALOG),
    ],
)
class AppModule:
    """Main application module"""
    pass


# ==================== Main ====================
if __name__ == '__main__':
    import sys
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create factory and register module
    factory = ModuleFactory()
    factory.register(AppModule)
    factory.initialize()
    
    # Create router
    router = Router(factory.injector)
    router.registerRoutes(factory.getRoutes())
    
    # Navigate to main window
    router.navigate('/')
    
    # Start application
    sys.exit(app.exec())
