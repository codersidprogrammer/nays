"""
Custom dialog views for testing UI integration with modules and lifecycle hooks.
These views extend BaseDialogView and implement lifecycle interfaces.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QMessageBox, QWidget
from PySide6.QtCore import Qt

from nays.ui.base_dialog import BaseDialogView


class HydroDashboardDialog(BaseDialogView):
    """Dialog for Hydro Dashboard with lifecycle support"""
    
    def __init__(self, routeData: dict = {}):
        BaseDialogView.__init__(self, routeData=routeData)
        self.init_called = False
        self.destroy_called = False
        self.lifecycle_events = []
        
        # Setup UI
        self.setWindowTitle("Hydro Dashboard")
        self.setGeometry(100, 100, 500, 300)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Hydro Monitoring Dashboard")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        btn_to_line = QPushButton("Go to Line Monitor")
        btn_to_line.clicked.connect(self.go_to_line_monitor)
        layout.addWidget(btn_to_line)
        
        self.setLayout(layout)
    
    def onInit(self):
        """Lifecycle hook: called when route is navigated to"""
        self.init_called = True
        self.lifecycle_events.append("init")
        self.status_label.setText("Status: Initialized")
    
    def onDestroy(self):
        """Lifecycle hook: called when route is navigated away"""
        self.destroy_called = True
        self.lifecycle_events.append("destroy")
    
    def go_to_line_monitor(self):
        """Navigate to line monitor route"""
        # In real scenario, this would call router.navigate("/line-monitor")
        pass


class LineMonitorDialog(BaseDialogView):
    """Dialog for Line Monitor with lifecycle support"""
    
    def __init__(self, routeData: dict = {}):
        BaseDialogView.__init__(self, routeData=routeData)
        self.init_called = False
        self.destroy_called = False
        self.lifecycle_events = []
        
        # Setup UI
        self.setWindowTitle("Line Monitor")
        self.setGeometry(150, 150, 500, 300)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Line Monitoring Dashboard")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        btn_to_hydro = QPushButton("Go to Hydro Dashboard")
        btn_to_hydro.clicked.connect(self.go_to_hydro_dashboard)
        layout.addWidget(btn_to_hydro)
        
        btn_to_main = QPushButton("Go to Main Dashboard")
        btn_to_main.clicked.connect(self.go_to_main_dashboard)
        layout.addWidget(btn_to_main)
        
        self.setLayout(layout)
    
    def onInit(self):
        """Lifecycle hook: called when route is navigated to"""
        self.init_called = True
        self.lifecycle_events.append("init")
        self.status_label.setText("Status: Initialized")
    
    def onDestroy(self):
        """Lifecycle hook: called when route is navigated away"""
        self.destroy_called = True
        self.lifecycle_events.append("destroy")
    
    def go_to_hydro_dashboard(self):
        """Navigate to hydro dashboard route"""
        pass
    
    def go_to_main_dashboard(self):
        """Navigate to main dashboard route"""
        pass


class MainDashboardDialog(BaseDialogView):
    """Main dashboard dialog with lifecycle support"""
    
    def __init__(self, routeData: dict = {}):
        BaseDialogView.__init__(self, routeData=routeData)
        self.init_called = False
        self.destroy_called = False
        self.lifecycle_events = []
        
        # Setup UI
        self.setWindowTitle("Main Dashboard")
        self.setGeometry(50, 50, 600, 400)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Main Control Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0066cc;")
        layout.addWidget(title)
        
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)
        
        info_label = QLabel("Welcome to the Main Dashboard. Use buttons to navigate to monitoring systems.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        btn_to_hydro = QPushButton("View Hydro System")
        btn_to_hydro.clicked.connect(self.go_to_hydro)
        layout.addWidget(btn_to_hydro)
        
        btn_to_line = QPushButton("View Line System")
        btn_to_line.clicked.connect(self.go_to_line)
        layout.addWidget(btn_to_line)
        
        self.setLayout(layout)
    
    def onInit(self):
        """Lifecycle hook: called when route is navigated to"""
        self.init_called = True
        self.lifecycle_events.append("init")
        self.status_label.setText("Status: Initialized")
    
    def onDestroy(self):
        """Lifecycle hook: called when route is navigated away"""
        self.destroy_called = True
        self.lifecycle_events.append("destroy")
    
    def go_to_hydro(self):
        """Navigate to hydro dashboard"""
        pass
    
    def go_to_line(self):
        """Navigate to line dashboard"""
        pass
