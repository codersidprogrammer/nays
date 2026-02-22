"""
View wrappers for the generated UI files.
These views wrap the auto-generated UI code and add lifecycle support.
"""

from abc import ABC, abstractmethod

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTreeWidget,
    QVBoxLayout,
    QWidget,
)

from nays.core.router import Router
from nays.ui.base_dialog import BaseDialogView
from nays.ui.base_window import BaseWindowView


# ==================== Logger Service Definition ====================
class LoggerService(ABC):
    """Logger service interface"""

    @abstractmethod
    def log(self, message: str):
        pass


# Note: Generated UI classes are no longer imported since we create UI dynamically
# from ui_dialog_line_master_material import Ui_MasterMaterial
# from ui_dialog_line_master_material_edit import Ui_MasterMaterialEdit


class MasterMaterialView(BaseDialogView):
    """
    View for viewing Line Master Material with generated UI.
    Wraps Ui_MasterMaterial and adds logic/lifecycle support.
    """

    def __init__(self, routeData: dict = {}, router: "Router" = None, logger: LoggerService = None):
        BaseDialogView.__init__(self, routeData=routeData)
        self.route_data = routeData
        self.router = router  # Injected router for navigation
        self.logger = logger  # Injected logger service from root module
        self.init_called = False
        self.destroy_called = False
        self.lifecycle_events = []

        # Setup generated UI (create stub ui object for backward compatibility)
        self.ui = type("UI", (), {})()  # Mock ui object

        # Setup UI layout
        self.setWindowTitle("Master Material - View")
        self.setGeometry(100, 100, 500, 300)

        # Create main layout
        main_layout = QVBoxLayout(self)

        # Material ID label and display
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Material ID:"))
        self.id_label = QLabel(self.route_data.get("material_id", ""))
        self.ui.id_label = self.id_label  # Add to ui for compatibility
        id_layout.addWidget(self.id_label)
        main_layout.addLayout(id_layout)

        # Material Name label and display
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Material Name:"))
        self.name_label = QLabel(self.route_data.get("material_name", ""))
        self.ui.name_label = self.name_label  # Add to ui for compatibility
        name_layout.addWidget(self.name_label)
        main_layout.addLayout(name_layout)

        # Add spacing
        main_layout.addSpacing(10)

        # Tree Material (placeholder for tree view)
        main_layout.addWidget(QLabel("Materials:"))
        self.treeMaterial = QTreeWidget()
        self.ui.treeMaterial = self.treeMaterial  # Add to ui for compatibility
        main_layout.addWidget(self.treeMaterial)

        # Table Detail (placeholder for detail table)
        main_layout.addWidget(QLabel("Details:"))
        self.tableDetail = QTableWidget()
        self.ui.tableDetail = self.tableDetail  # Add to ui for compatibility
        main_layout.addWidget(self.tableDetail)

        # Button layout
        btn_layout = QHBoxLayout()

        # Edit button
        self.pbEdit = QPushButton("Edit")
        self.pbEdit.clicked.connect(self.on_edit_clicked)
        self.ui.pbEdit = self.pbEdit  # Add to ui for compatibility
        btn_layout.addWidget(self.pbEdit)

        # Back button
        self.pbBack = QPushButton("Back")
        self.pbBack.clicked.connect(self.on_back_clicked)
        self.ui.pbBack = self.pbBack  # Add to ui for compatibility
        btn_layout.addWidget(self.pbBack)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)
        self.populate_material_data()
        self.setup_handlers()

    def populate_material_data(self):
        """Populate material data from route params if available"""
        if self.route_data and "material_id" in self.route_data:
            material_id = self.route_data["material_id"]
            # In real scenario, this would fetch from database
            # For now, just mark as populated
            pass

    def setup_handlers(self):
        """Setup event handlers"""
        # Handlers are already connected in __init__
        pass

    def on_edit_clicked(self):
        """Navigate to edit view"""
        if self.router:
            self.router.navigate(
                "/material-edit",
                {
                    "material_id": self.route_data.get("material_id", ""),
                    "material_name": self.route_data.get("material_name", ""),
                },
            )

    def on_back_clicked(self):
        """Navigate back to entry window"""
        if self.router:
            self.router.navigate("/entry")

    def onInit(self):
        """Lifecycle hook: called when route is navigated to"""
        self.init_called = True
        self.lifecycle_events.append("init")
        if self.logger:
            self.logger.log(
                f"MasterMaterialView initialized with material: {self.route_data.get('material_name', 'Unknown')}"
            )
        if self.route_data:
            title = self.route_data.get("material_name", "Master Material")
            self.setWindowTitle(f"Master Material - {title}")

    def onDestroy(self):
        """Lifecycle hook: called when route is navigated away"""
        self.destroy_called = True
        self.lifecycle_events.append("destroy")
        if self.logger:
            self.logger.log(f"MasterMaterialView destroyed")


class MasterMaterialEditView(BaseDialogView):
    """
    View for editing Line Master Material with generated UI.
    Wraps Ui_MasterMaterialEdit and adds logic/lifecycle support.
    """

    def __init__(self, routeData: dict = {}, router: "Router" = None, logger: LoggerService = None):
        BaseDialogView.__init__(self, routeData=routeData)
        self.route_data = routeData
        self.router = router  # Injected router for navigation
        self.logger = logger  # Injected logger service from root module
        self.init_called = False
        self.destroy_called = False
        self.lifecycle_events = []

        # Setup generated UI (create stub ui object for backward compatibility)
        self.ui = type("UI", (), {})()  # Mock ui object

        # Setup UI layout
        self.setWindowTitle("Master Material - Edit")
        self.setGeometry(100, 100, 500, 400)

        # Create main layout
        main_layout = QVBoxLayout(self)

        # Material ID field
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Material ID:"))
        self.lineEditMaterialID = QLineEdit()
        self.ui.lineEditMaterialID = self.lineEditMaterialID  # Add to ui for compatibility
        id_layout.addWidget(self.lineEditMaterialID)
        main_layout.addLayout(id_layout)

        # Material Name field
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Material Name:"))
        self.lineEditMaterialName = QLineEdit()
        self.ui.lineEditMaterialName = self.lineEditMaterialName  # Add to ui for compatibility
        name_layout.addWidget(self.lineEditMaterialName)
        main_layout.addLayout(name_layout)

        # Input Parameters table
        main_layout.addWidget(QLabel("Input Parameters:"))
        self.tableInputParameters = QTableWidget()
        self.ui.tableInputParameters = self.tableInputParameters  # Add to ui for compatibility
        main_layout.addWidget(self.tableInputParameters)

        # Calculated Parameters table
        main_layout.addWidget(QLabel("Calculated Parameters:"))
        self.tableCalculatedParameters = QTableWidget()
        self.ui.tableCalculatedParameters = (
            self.tableCalculatedParameters
        )  # Add to ui for compatibility
        main_layout.addWidget(self.tableCalculatedParameters)

        # Add spacing
        main_layout.addSpacing(10)

        # Button layout
        btn_layout = QHBoxLayout()

        # Calculate button
        self.pbCalculate = QPushButton("Calculate")
        self.pbCalculate.clicked.connect(self.on_calculate_clicked)
        self.ui.pbCalculate = self.pbCalculate  # Add to ui for compatibility
        btn_layout.addWidget(self.pbCalculate)

        # Save button
        self.pbSave = QPushButton("Save")
        self.pbSave.clicked.connect(self.on_save_clicked)
        self.ui.pbSave = self.pbSave  # Add to ui for compatibility
        btn_layout.addWidget(self.pbSave)

        # Cancel button
        self.pbCancel = QPushButton("Cancel")
        self.pbCancel.clicked.connect(self.on_cancel_clicked)
        self.ui.pbCancel = self.pbCancel  # Add to ui for compatibility
        btn_layout.addWidget(self.pbCancel)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.populate_edit_data()
        self.setup_handlers()

    def populate_edit_data(self):
        """Populate edit data from route params if available"""
        if self.route_data:
            material_id = self.route_data.get("material_id", "")
            material_name = self.route_data.get("material_name", "")

            self.lineEditMaterialID.setText(material_id)
            self.lineEditMaterialName.setText(material_name)

    def setup_handlers(self):
        """Setup event handlers for calculate button"""
        # Handlers are already connected in __init__
        pass

    def on_calculate_clicked(self):
        """Handle calculate button click"""
        # In real scenario, this would perform calculations
        self.lifecycle_events.append("calculate")

    def on_save_clicked(self):
        """Handle save button click - navigate back to view"""
        if self.router:
            self.router.navigate(
                "/material-view",
                {
                    "material_id": self.lineEditMaterialID.text(),
                    "material_name": self.lineEditMaterialName.text(),
                },
            )
            self.lifecycle_events.append("save_and_navigate")

    def on_cancel_clicked(self):
        """Handle cancel button click - navigate back to entry"""
        if self.router:
            self.router.navigate("/entry")
            self.lifecycle_events.append("cancel_and_navigate")

    def onInit(self):
        """Lifecycle hook: called when route is navigated to"""
        self.init_called = True
        self.lifecycle_events.append("init")
        if self.logger:
            self.logger.log(
                f"MasterMaterialEditView initialized with material: {self.route_data.get('material_name', 'Unknown')}"
            )
        if self.route_data:
            title = self.route_data.get("material_name", "Master Material")
            self.setWindowTitle(f"Master Material Edit - {title}")

    def onDestroy(self):
        """Lifecycle hook: called when route is navigated away"""
        self.destroy_called = True
        self.lifecycle_events.append("destroy")
        if self.logger:
            self.logger.log(f"MasterMaterialEditView destroyed")


class EntryWindowView(BaseWindowView):
    """
    Main entry window view.
    Provides navigation to different material management dialogs.
    """

    def __init__(self, routeData: dict = {}, router: "Router" = None, logger: LoggerService = None):
        BaseWindowView.__init__(self, routeData=routeData)
        self.route_data = routeData
        self.router = router  # Injected router for navigation
        self.logger = logger  # Injected logger service from root module
        self.init_called = False
        self.destroy_called = False
        self.lifecycle_events = []

        # Setup window
        self.setWindowTitle("Material Management - Entry Window")
        self.setGeometry(50, 50, 700, 500)

        # Create central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Material Management System")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0066cc;")
        layout.addWidget(title)

        # Instructions
        info = QLabel("Welcome to Material Management. Select an option below:")
        info.setWordWrap(True)
        layout.addWidget(info)

        # Buttons for navigation
        btn_view = QPushButton("View Master Material")
        btn_view.clicked.connect(self.on_view_material)
        layout.addWidget(btn_view)

        btn_edit = QPushButton("Edit Master Material")
        btn_edit.clicked.connect(self.on_edit_material)
        layout.addWidget(btn_edit)

        # Status label
        self.status_label = QLabel("Status: Ready")
        layout.addWidget(self.status_label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def on_view_material(self):
        """Navigate to view material"""
        if self.router:
            self.router.navigate(
                "/material-view", {"material_id": "DIMAT-0012", "material_name": "Steel Material"}
            )
        self.lifecycle_events.append("navigate_to_view")

    def on_edit_material(self):
        """Navigate to edit material"""
        if self.router:
            self.router.navigate(
                "/material-edit", {"material_id": "MAT001", "material_name": "Steel Material"}
            )
        self.lifecycle_events.append("navigate_to_edit")

    def onInit(self):
        """Lifecycle hook: called when route is navigated to"""
        self.init_called = True
        self.lifecycle_events.append("init")
        if self.logger:
            self.logger.log(
                "EntryWindowView initialized - Ready to navigate to material management views"
            )
        self.status_label.setText("Status: Initialized")

    def onDestroy(self):
        """Lifecycle hook: called when route is navigated away"""
        self.destroy_called = True
        self.lifecycle_events.append("destroy")
        if self.logger:
            self.logger.log("EntryWindowView destroyed")
