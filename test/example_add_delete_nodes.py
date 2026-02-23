#!/usr/bin/env python3
"""
example_add_delete_nodes.py
============================
Demonstrates the addNode() and deleteNode() methods for adding/deleting nodes
dynamically from a TreeViewHandler.
"""

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

from nays.ui.handler import TreeViewHandler
from PySide6.QtWidgets import QTreeView

# Sample initial data
INITIAL_DATA = [
    {
        "id": 1,
        "name": "Engineering",
        "status": "active",
        "children": [
            {"id": 11, "name": "Hardware", "status": "active"},
            {"id": 12, "name": "Software", "status": "warning"},
        ],
    },
    {"id": 2, "name": "Sales", "status": "active", "children": []},
]


class AddDeleteDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TreeViewHandler - Add/Delete Demo")
        self.setGeometry(100, 100, 600, 500)

        central = QWidget()
        layout = QVBoxLayout(central)
        self.setCentralWidget(central)

        # Create tree view
        tree = QTreeView()
        layout.addWidget(tree)

        # Setup handler
        self.handler = TreeViewHandler(tree, applyDefaultStyle=True)
        self.handler.setColumns([
            {"key": "name", "label": "Name", "width": 200},
            {"key": "status", "label": "Status", "width": 80},
        ])

        self.handler.setContextMenuActions([
            {"label": "Add Child", "action": "add_child", "icon": "add", "nodeFilter": "root"},
            {"separator": True},
            {"label": "Delete", "action": "delete", "icon": "delete"},
        ])

        # Load initial data
        self.handler.loadData(INITIAL_DATA)

        # Callbacks
        self.handler.onActionTriggered("add_child", self.on_add_child)
        self.handler.onActionTriggered("delete", self.on_delete)
        self.handler.onDataLoaded(
            lambda count: print(f"✓ Tree loaded with {count} nodes total")
        )

        # Button controls
        btn_layout = QVBoxLayout()
        layout.addLayout(btn_layout)

        # Add root button
        add_root_btn = QPushButton("Add Root Item")
        add_root_btn.clicked.connect(self.on_add_root)
        btn_layout.addWidget(add_root_btn)

        # Add child button
        add_child_btn = QPushButton("Add Child to Selected")
        add_child_btn.clicked.connect(self.on_add_child_button)
        btn_layout.addWidget(add_child_btn)

        # Delete button
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.on_delete_button)
        btn_layout.addWidget(delete_btn)

    def on_add_root(self):
        """Add a new root item via button."""
        new_root = {"id": 999, "name": "New Root", "status": "active", "children": []}
        success = self.handler.addNode(new_root)
        if success:
            print(f"✓ Added root: {new_root['name']}")
        else:
            print("✗ Failed to add root")

    def on_add_child(self, node_data):
        """Context menu callback: add child to selected node."""
        new_child = {"id": 888, "name": "New Child", "status": "active"}
        success = self.handler.addNode(new_child, parentData=node_data)
        if success:
            print(f"✓ Added child '{new_child['name']}' to '{node_data.get('name')}'")
            # Auto-expand parent
            self.handler.expandNode(node_data)
        else:
            print("✗ Failed to add child")

    def on_add_child_button(self):
        """Button callback: add child to selected node."""
        selected = self.handler.getSelectedNode()
        if selected:
            self.on_add_child(selected)
        else:
            print("⚠ No node selected")

    def on_delete(self, node_data):
        """Context menu callback: delete selected node."""
        name = node_data.get("name", "?")
        success = self.handler.deleteNode(node_data)
        if success:
            print(f"✓ Deleted: {name}")
        else:
            print(f"✗ Failed to delete: {name}")

    def on_delete_button(self):
        """Button callback: delete selected node."""
        selected = self.handler.getSelectedNode()
        if selected:
            self.on_delete(selected)
        else:
            print("⚠ No node selected")


if __name__ == "__main__":
    app = QApplication([])
    window = AddDeleteDemo()
    window.show()
    app.exec()
