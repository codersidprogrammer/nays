"""
example_tree_view_handler.py
============================
Demonstrates TreeViewHandler with real-world DB data that uses:
    - 'moduleName'  as the display name key
    - 'iconPath'    as a Qt resource icon path
    - 'sequence'    as the ordering key
    - 'children'    for nesting (unchanged)

Run:
    python3 test/example_tree_view_handler.py
"""
from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))   # so main_icons is importable

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeView, QGroupBox, QLabel, QPushButton, QStatusBar, QSplitter,
    QMessageBox, QInputDialog,
)
from PySide6.QtCore import Qt

from nays.ui.handler.tree_view_handler import TreeViewHandler
import nays.ui.helper.main_icons as main_icons  # registers :/16/fugue-icons/... Qt resources  # noqa: F401


# ─── Data as it comes from the database ──────────────────────────────────────
# Keys used:
#   sequence   — order within parent
#   moduleName — display label
#   iconPath   — Qt resource path (e.g. ':/16/fugue-icons/icons/water.png')
#   children   — nested list (same structure)

DB_DATA = [
    {
        "sequence": 1,
        "moduleName": "Hydrodynamic",
        "iconPath": ":/16/fugue-icons/icons/water.png",
        "children": [
            {"sequence": 1, "moduleName": "Compiler Settings", "iconPath": ":/16/fugue-icons/icons/gear.png",             "children": []},
            {"sequence": 2, "moduleName": "Hull",              "iconPath": ":/16/fugue-icons/icons/building.png",         "children": []},
            {"sequence": 3, "moduleName": "Single Body",       "iconPath": ":/16/fugue-icons/icons/application.png",      "children": []},
            {"sequence": 4, "moduleName": "Multi Body",        "iconPath": ":/16/fugue-icons/icons/applications-blue.png","children": []},
        ],
    },
    {
        "sequence": 2,
        "moduleName": "Line",
        "iconPath": ":/16/fugue-icons/icons/layer-vector.png",
        "children": [
            {"sequence": 1, "moduleName": "List Materials", "iconPath": ":/16/fugue-icons/icons/database.png",       "children": []},
            {"sequence": 2, "moduleName": "Project",        "iconPath": ":/16/fugue-icons/icons/application-wave.png","children": []},
        ],
    },
    {
        "sequence": 3,
        "moduleName": "Charm 3D",
        "iconPath": ":/16/fugue-icons/icons/block.png",
        "children": [
            {"sequence": 1, "moduleName": "Compiler Settings", "iconPath": ":/16/fugue-icons/icons/gear.png",             "children": []},
            {"sequence": 2, "moduleName": "Single Body",       "iconPath": ":/16/fugue-icons/icons/application.png",      "children": []},
            {"sequence": 3, "moduleName": "Multi Body",        "iconPath": ":/16/fugue-icons/icons/applications-blue.png","children": []},
        ],
    },
]


# ─── Main Window ─────────────────────────────────────────────────────────────

class DemoWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("TreeViewHandler — DB Schema Demo")
        self.resize(1060, 620)

        central = QWidget()
        self.setCentralWidget(central)
        root_vl = QVBoxLayout(central)
        root_vl.setContentsMargins(8, 8, 8, 6)
        root_vl.setSpacing(6)

        title = QLabel("TreeViewHandler  —  moduleName / iconPath / sequence keys")
        title.setStyleSheet("font-weight: 700; font-size: 13px; padding: 2px 0;")
        root_vl.addWidget(title)

        # ── Toolbar ─────────────────────────────────────────
        tb_grp = QGroupBox("Actions")
        tb_hl = QHBoxLayout(tb_grp)
        tb_hl.setContentsMargins(8, 4, 8, 4); tb_hl.setSpacing(6)
        btn_reload   = QPushButton("⟳ Reload")
        btn_expand   = QPushButton("⊞ Expand All")
        btn_collapse = QPushButton("⊟ Collapse All")
        btn_dark     = QPushButton("◑ Dark")
        btn_light    = QPushButton("○ Light")
        btn_all      = QPushButton("⊙ All Nodes")
        for b in (btn_reload, btn_expand, btn_collapse, btn_dark, btn_light, btn_all):
            tb_hl.addWidget(b)
        tb_hl.addStretch()
        root_vl.addWidget(tb_grp)

        # ── Splitter ─────────────────────────────────────────
        splitter = QSplitter(Qt.Horizontal)

        tree_grp = QGroupBox("Module Tree")
        tree_vl  = QVBoxLayout(tree_grp)
        tree_vl.setContentsMargins(4, 4, 4, 4)
        self._tree = QTreeView()           # plain, unmodified QTreeView
        tree_vl.addWidget(self._tree)
        splitter.addWidget(tree_grp)

        info_grp = QGroupBox("Selection Details")
        info_vl  = QVBoxLayout(info_grp)
        info_vl.setContentsMargins(8, 8, 8, 8)
        self._info = QLabel("Select a node.")
        self._info.setWordWrap(True)
        self._info.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._info.setStyleSheet("font-size: 12px; font-family: monospace;")
        info_vl.addWidget(self._info)
        info_vl.addStretch()
        splitter.addWidget(info_grp)

        splitter.setSizes([680, 350])
        root_vl.addWidget(splitter, stretch=1)

        self._sb = QStatusBar()
        self.setStatusBar(self._sb)
        self._sb.showMessage("Ready.")

        # ── TreeViewHandler ───────────────────────────────────
        # Map the DB keys to handler parameters:
        #   nameKey  = "moduleName"   (DB column name)
        #   iconKey  = "iconPath"     (DB column holding Qt resource path)
        self._handler = TreeViewHandler(
            treeView=self._tree,
            childrenKey="children",    # unchanged
            nameKey="moduleName",      # ← DB key for display label
            statusKey="status",        # not in DB data; fallback only
            iconKey="iconPath",        # ← DB key for QIcon resource path
            applyDefaultStyle=True,
        )

        # ── Columns ───────────────────────────────────────────
        # iconPath is used as the node icon — not shown as a column
        self._handler.setColumns([
            {"key": "moduleName", "label": "Module",   "width": 260},
            {"key": "sequence",   "label": "Seq",      "width": 50},
        ])

        # ── Context menu ──────────────────────────────────────
        self._handler.setContextMenuActions([
            {"label": "Properties",    "action": "properties", "icon": "properties"},
            {"separator": True},
            {"label": "Open / Expand", "action": "open",       "icon": "expand",   "nodeFilter": "parent"},
            {"label": "Collapse",      "action": "collapse",   "icon": "collapse", "nodeFilter": "parent"},
            {"separator": True},
            {"label": "Edit Name",     "action": "edit",       "icon": "edit",     "nodeFilter": "leaf"},
            {"label": "Delete",        "action": "delete",     "icon": "delete",   "nodeFilter": "leaf"},
        ])

        # ── Double-click ──────────────────────────────────────
        self._handler.setDoubleClickAction("toggle_expand", nodeFilter="parent")
        self._handler.setDoubleClickAction("edit",          nodeFilter="leaf")

        # ── Callbacks ─────────────────────────────────────────
        self._handler.onSelectionChanged(self._onSelected)
        self._handler.onActionTriggered("edit",       self._onEdit)
        self._handler.onActionTriggered("delete",     self._onDelete)
        self._handler.onActionTriggered("properties", self._onProperties)
        self._handler.onActionTriggered("open",       lambda d: self._handler.expandNode(d))
        self._handler.onActionTriggered("collapse",   lambda d: self._handler.collapseNode(d))
        self._handler.onDataLoaded(lambda n: self._sb.showMessage(f"Loaded {n} nodes."))

        # ── Toolbar wiring ────────────────────────────────────
        btn_reload.clicked.connect(lambda: self._handler.loadData(DB_DATA))
        btn_expand.clicked.connect(self._handler.expandAll)
        btn_collapse.clicked.connect(self._handler.collapseAll)
        btn_dark.clicked.connect(self._handler.applyDarkStyle)
        btn_light.clicked.connect(lambda: self._handler.applyStyle())
        btn_all.clicked.connect(self._showAll)

        # ── Load ─────────────────────────────────────────────
        self._handler.loadData(DB_DATA)

    # ─── Callbacks ─────────────────────────────────────────

    def _onSelected(self, data: dict):
        if not data:
            self._info.setText("(nothing selected)")
            return
        lines = [f"<b>{data.get('moduleName', '?')}</b>", ""]
        for k, v in data.items():
            if k == "children":
                lines.append(f"  children  : {len(v)} item(s)")
            else:
                lines.append(f"  {k:<12}: {v}")
        self._info.setText("<br>".join(lines))

    def _onEdit(self, data: dict):
        text, ok = QInputDialog.getText(
            self, "Edit Module Name", "Module name:",
            text=data.get("moduleName", ""),
        )
        if ok and text.strip():
            data["moduleName"] = text.strip()
            self._handler.loadData(DB_DATA)
            self._sb.showMessage(f"Renamed to '{text.strip()}'.")

    def _onDelete(self, data: dict):
        reply = QMessageBox.question(
            self, "Delete",
            f"Delete '{data.get('moduleName')}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._sb.showMessage(f"Deleted '{data.get('moduleName')}' (demo).")

    def _onProperties(self, data: dict):
        lines = "\n".join(
            f"{k}: {v}" for k, v in data.items() if k != "children"
        )
        QMessageBox.information(self, f"Properties — {data.get('moduleName')}", lines)

    def _showAll(self):
        nodes = self._handler.getAllNodes()
        lines = [
            f"{'  ' * n['_depth']}{n.get('moduleName')}  "
            f"(seq={n.get('sequence')}, children={n['_has_children']})"
            for n in nodes
        ]
        QMessageBox.information(self, "All Nodes", "\n".join(lines))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DemoWindow()
    win.show()
    sys.exit(app.exec())
