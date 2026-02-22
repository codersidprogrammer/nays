"""
mvvm_treeview.py
================
PySide6 MVVM QTreeView with:
  • Simulated async DB load (QTimer, 600 ms delay)
  • Two-level tree: Category (parent) → Item (child)
  • Different context menus for parent vs child nodes
  • Per-node icons drawn with QPainter (no external files needed)
  • Double-click default action (open/expand for parent, edit for child)
  • All double-click actions also available via right-click context menu
  • Full two-way MVVM binding (ViewModel ↔ View, infinite-loop-safe)

Install:  pip install PySide6
Run:      python mvvm_treeview.py
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from PySide6.QtCore import (
    Q_ARG,
    QAbstractItemModel,
    QMetaObject,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    QRunnable,
    QSize,
    Qt,
    QThread,
    QThreadPool,
    QTimer,
    Signal,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QFont,
    QIcon,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStatusBar,
    QTextEdit,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

# ═══════════════════════════════════════════════════════════
# 1. DATA NODES  (pure Python, no Qt)
# ═══════════════════════════════════════════════════════════


class NodeKind(Enum):
    CATEGORY = auto()  # parent-level
    ITEM = auto()  # child-level


@dataclass
class TreeNode:
    """One node in the tree. Children only allowed on CATEGORY nodes."""

    id: int
    kind: NodeKind
    name: str
    description: str = ""
    status: str = "active"  # active | warning | error | disabled
    tags: list[str] = field(default_factory=list)
    children: list["TreeNode"] = field(default_factory=list)
    parent: "TreeNode | None" = field(default=None, repr=False, compare=False)

    # runtime state
    is_loading: bool = False

    def child_count(self) -> int:
        return len(self.children)

    def child_at(self, row: int) -> "TreeNode | None":
        if 0 <= row < len(self.children):
            return self.children[row]
        return None

    def row_in_parent(self) -> int:
        if self.parent:
            return self.parent.children.index(self)
        return 0


# ═══════════════════════════════════════════════════════════
# 2. ICON FACTORY  (all icons painted with QPainter)
# ═══════════════════════════════════════════════════════════


class IconFactory:
    """Creates QIcon objects painted on-the-fly — no image files needed."""

    _cache: dict[str, QIcon] = {}

    @classmethod
    def get(cls, name: str, size: int = 16) -> QIcon:
        key = f"{name}@{size}"
        if key not in cls._cache:
            cls._cache[key] = cls._make(name, size)
        return cls._cache[key]

    @classmethod
    def _make(cls, name: str, size: int) -> QIcon:
        px = QPixmap(size, size)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        dispatch = {
            "folder": cls._folder,
            "folder_open": cls._folder_open,
            "item": cls._item,
            "item_warning": cls._item_warning,
            "item_error": cls._item_error,
            "item_disabled": cls._item_disabled,
            "loading": cls._loading,
            "add": cls._add,
            "delete": cls._delete,
            "edit": cls._edit,
            "refresh": cls._refresh,
            "expand": cls._expand,
            "collapse": cls._collapse,
            "info": cls._info,
            "properties": cls._properties,
        }
        draw = dispatch.get(name, cls._unknown)
        draw(p, size)
        p.end()
        return QIcon(px)

    # ── drawers ───────────────────────────────────────────
    @staticmethod
    def _folder(p, s):
        p.setBrush(QColor("#f0ad4e"))
        p.setPen(QPen(QColor("#c87f0a"), 1))
        # tab
        path = QPainterPath()
        path.moveTo(1, s * 0.45)
        path.lineTo(1, s * 0.9)
        path.lineTo(s - 1, s * 0.9)
        path.lineTo(s - 1, s * 0.35)
        path.lineTo(s * 0.55, s * 0.35)
        path.lineTo(s * 0.45, s * 0.2)
        path.lineTo(s * 0.1, s * 0.2)
        path.lineTo(s * 0.1, s * 0.45)
        path.closeSubpath()
        p.drawPath(path)

    @staticmethod
    def _folder_open(p, s):
        p.setBrush(QColor("#ffd080"))
        p.setPen(QPen(QColor("#c87f0a"), 1))
        path = QPainterPath()
        path.moveTo(1, s * 0.9)
        path.lineTo(s * 0.15, s * 0.45)
        path.lineTo(s - 1, s * 0.45)
        path.lineTo(s - 1, s * 0.35)
        path.lineTo(s * 0.55, s * 0.35)
        path.lineTo(s * 0.45, s * 0.2)
        path.lineTo(s * 0.1, s * 0.2)
        path.lineTo(s * 0.1, s * 0.45)
        path.lineTo(1, s * 0.45)
        path.closeSubpath()
        p.drawPath(path)

    @staticmethod
    def _item(p, s):
        p.setBrush(QColor("#5b9bd5"))
        p.setPen(QPen(QColor("#2e6da4"), 1))
        p.drawRoundedRect(2, 2, s - 4, s - 4, 2, 2)
        p.setPen(QPen(QColor("#ffffff"), 1.2))
        m = s // 4
        p.drawLine(m, s // 2, s - m, s // 2)
        p.drawLine(s // 2, m, s // 2, s - m)

    @staticmethod
    def _item_warning(p, s):
        p.setBrush(QColor("#f0ad4e"))
        p.setPen(QPen(QColor("#c87f0a"), 1))
        pts = [s // 2, 1, s - 1, s - 2, 1, s - 2]
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QPolygon

        poly = [QPoint(s // 2, 1), QPoint(s - 1, s - 2), QPoint(1, s - 2)]
        p.drawPolygon(poly)
        p.setPen(QPen(QColor("#7a4800"), 1.5))
        p.drawLine(s // 2, s // 3, s // 2, s * 2 // 3)
        p.drawPoint(s // 2, s * 3 // 4)

    @staticmethod
    def _item_error(p, s):
        p.setBrush(QColor("#d9534f"))
        p.setPen(QPen(QColor("#8b1a18"), 1))
        p.drawEllipse(1, 1, s - 2, s - 2)
        p.setPen(QPen(QColor("#ffffff"), 1.8))
        m = s // 3
        p.drawLine(m, m, s - m, s - m)
        p.drawLine(s - m, m, m, s - m)

    @staticmethod
    def _item_disabled(p, s):
        p.setBrush(QColor("#aaaaaa"))
        p.setPen(QPen(QColor("#777777"), 1))
        p.drawRoundedRect(2, 2, s - 4, s - 4, 2, 2)

    @staticmethod
    def _loading(p, s):
        p.setBrush(Qt.NoBrush)
        for i in range(8):
            import math

            angle = i * 45
            rad = math.radians(angle)
            alpha = 40 + int(215 * i / 7)
            p.setPen(QPen(QColor(80, 80, 200, alpha), 1.5))
            cx, cy, r = s / 2, s / 2, s / 2 - 2
            x1 = cx + r * 0.5 * math.cos(rad)
            y1 = cy + r * 0.5 * math.sin(rad)
            x2 = cx + r * math.cos(rad)
            y2 = cy + r * math.sin(rad)
            p.drawLine(int(x1), int(y1), int(x2), int(y2))

    @staticmethod
    def _add(p, s):
        p.setBrush(QColor("#5cb85c"))
        p.setPen(QPen(QColor("#3d8b3d"), 1))
        p.drawEllipse(1, 1, s - 2, s - 2)
        p.setPen(QPen(QColor("#ffffff"), 2))
        m = s // 4
        p.drawLine(s // 2, m, s // 2, s - m)
        p.drawLine(m, s // 2, s - m, s // 2)

    @staticmethod
    def _delete(p, s):
        p.setBrush(QColor("#d9534f"))
        p.setPen(QPen(QColor("#8b1a18"), 1))
        p.drawRoundedRect(1, 1, s - 2, s - 2, 2, 2)
        p.setPen(QPen(QColor("#ffffff"), 2))
        m = s // 4
        p.drawLine(m, m, s - m, s - m)
        p.drawLine(s - m, m, m, s - m)

    @staticmethod
    def _edit(p, s):
        p.setBrush(QColor("#5b9bd5"))
        p.setPen(QPen(QColor("#2e6da4"), 1))
        # pencil shape
        path = QPainterPath()
        path.moveTo(s * 0.7, s * 0.1)
        path.lineTo(s * 0.9, s * 0.3)
        path.lineTo(s * 0.3, s * 0.9)
        path.lineTo(s * 0.1, s * 0.9)
        path.lineTo(s * 0.1, s * 0.7)
        path.closeSubpath()
        p.drawPath(path)

    @staticmethod
    def _refresh(p, s):
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#0078d7"), 2))
        import math

        p.drawArc(2, 2, s - 4, s - 4, 30 * 16, 300 * 16)
        # arrowhead
        p.setBrush(QColor("#0078d7"))
        p.setPen(Qt.NoPen)
        angle = math.radians(30)
        cx, cy, r = s / 2, s / 2, s / 2 - 2
        ax = cx + r * math.cos(angle)
        ay = cy - r * math.sin(angle)
        from PySide6.QtCore import QPoint

        p.drawPolygon(
            [
                QPoint(int(ax), int(ay) - 3),
                QPoint(int(ax) + 4, int(ay) + 2),
                QPoint(int(ax) - 2, int(ay) + 3),
            ]
        )

    @staticmethod
    def _expand(p, s):
        p.setBrush(QColor("#e1e1e1"))
        p.setPen(QPen(QColor("#adadad"), 1))
        p.drawRect(1, 1, s - 2, s - 2)
        p.setPen(QPen(QColor("#000"), 1.5))
        m = s // 4
        p.drawLine(m, s // 2, s - m, s // 2)
        p.drawLine(s // 2, m, s // 2, s - m)

    @staticmethod
    def _collapse(p, s):
        p.setBrush(QColor("#e1e1e1"))
        p.setPen(QPen(QColor("#adadad"), 1))
        p.drawRect(1, 1, s - 2, s - 2)
        p.setPen(QPen(QColor("#000"), 1.5))
        m = s // 4
        p.drawLine(m, s // 2, s - m, s // 2)

    @staticmethod
    def _info(p, s):
        p.setBrush(QColor("#5b9bd5"))
        p.setPen(QPen(QColor("#2e6da4"), 1))
        p.drawEllipse(1, 1, s - 2, s - 2)
        p.setPen(QPen(Qt.white, 1.8))
        p.drawText(0, 0, s, s, Qt.AlignCenter, "i")

    @staticmethod
    def _properties(p, s):
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(QColor("#555"), 1.5))
        m = 3
        for y in [s // 4, s // 2, s * 3 // 4]:
            p.drawLine(m, y, s - m, y)

    @staticmethod
    def _unknown(p, s):
        p.setBrush(QColor("#cccccc"))
        p.setPen(QPen(QColor("#999"), 1))
        p.drawRect(1, 1, s - 2, s - 2)


# ═══════════════════════════════════════════════════════════
# 3. VIEW-MODEL  (all state lives here)
# ═══════════════════════════════════════════════════════════


class TreeViewModel(QObject):
    """
    MVVM ViewModel for a two-level tree.

    Signals
    -------
    load_started()              DB fetch begins
    load_finished()             DB fetch complete, roots rebuilt
    node_updated(node_id)       A node's data changed
    node_added(parent_id, row)  New child inserted
    node_removed(node_id)       Node deleted
    action_triggered(action, node)   UI should react (open dialog, etc.)
    status_message(str)
    """

    load_started = Signal()
    load_finished = Signal()
    node_updated = Signal(int)  # node id
    node_added = Signal(int, int)  # parent_id, child_row
    node_removed = Signal(int)  # node id
    action_triggered = Signal(str, object)  # action_name, TreeNode
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self._roots: list[TreeNode] = []
        self._id_map: dict[int, TreeNode] = {}
        self._suppress = False
        self._next_id = 1000

    # ── roots ─────────────────────────────────────────────
    @property
    def roots(self) -> list[TreeNode]:
        return self._roots

    def node_by_id(self, nid: int) -> TreeNode | None:
        return self._id_map.get(nid)

    # ── DB simulation ──────────────────────────────────────
    def load_from_db(self):
        """
        Simulate an async database fetch.
        Uses QTimer to mimic network/IO delay without blocking UI.
        """
        self.load_started.emit()
        self.status_message.emit("Loading data from database…")
        QTimer.singleShot(650, self._do_load)

    def _do_load(self):
        """Simulated DB result — in production replace with real query."""
        raw_data = [
            {
                "id": 1,
                "name": "Engineering",
                "description": "Core engineering projects",
                "status": "active",
                "tags": ["tech", "core"],
                "children": [
                    {
                        "id": 11,
                        "name": "Hydraulic System",
                        "description": "Main hydraulic circuit design",
                        "status": "active",
                        "tags": ["hydraulic"],
                    },
                    {
                        "id": 12,
                        "name": "Control Module v2",
                        "description": "Digital control unit firmware",
                        "status": "warning",
                        "tags": ["firmware", "control"],
                    },
                    {
                        "id": 13,
                        "name": "Structural Frame",
                        "description": "Primary load-bearing structure",
                        "status": "active",
                        "tags": ["structural"],
                    },
                    {
                        "id": 14,
                        "name": "Legacy Wiring",
                        "description": "Deprecated wiring harness",
                        "status": "disabled",
                        "tags": ["legacy"],
                    },
                ],
            },
            {
                "id": 2,
                "name": "Research & Development",
                "description": "Experimental and prototype work",
                "status": "active",
                "tags": ["research"],
                "children": [
                    {
                        "id": 21,
                        "name": "AI Sensor Fusion",
                        "description": "ML-based sensor data fusion",
                        "status": "active",
                        "tags": ["ai", "sensor"],
                    },
                    {
                        "id": 22,
                        "name": "Carbon Composite",
                        "description": "New material testing batch",
                        "status": "error",
                        "tags": ["materials"],
                    },
                    {
                        "id": 23,
                        "name": "Prototype XR-9",
                        "description": "Next-gen propulsion prototype",
                        "status": "active",
                        "tags": ["propulsion"],
                    },
                ],
            },
            {
                "id": 3,
                "name": "Quality Assurance",
                "description": "Testing and certification workflows",
                "status": "warning",
                "tags": ["qa", "testing"],
                "children": [
                    {
                        "id": 31,
                        "name": "Fatigue Test Rig",
                        "description": "Cyclic load testing apparatus",
                        "status": "active",
                        "tags": ["testing"],
                    },
                    {
                        "id": 32,
                        "name": "Cert Package Rev3",
                        "description": "Regulatory certification docs",
                        "status": "warning",
                        "tags": ["cert", "docs"],
                    },
                ],
            },
            {
                "id": 4,
                "name": "Documentation",
                "description": "Technical documentation and manuals",
                "status": "active",
                "tags": ["docs"],
                "children": [
                    {
                        "id": 41,
                        "name": "Installation Guide",
                        "description": "Step-by-step installation manual",
                        "status": "active",
                        "tags": ["manual"],
                    },
                    {
                        "id": 42,
                        "name": "API Reference",
                        "description": "Developer API documentation",
                        "status": "active",
                        "tags": ["api", "dev"],
                    },
                    {
                        "id": 43,
                        "name": "Release Notes v4.1",
                        "description": "Version 4.1 change log",
                        "status": "active",
                        "tags": ["release"],
                    },
                ],
            },
        ]
        self._build_tree(raw_data)
        self.load_finished.emit()
        self.status_message.emit(
            f"Loaded {len(self._roots)} categories, "
            f"{sum(n.child_count() for n in self._roots)} items."
        )

    def _build_tree(self, raw: list[dict]):
        self._roots.clear()
        self._id_map.clear()
        for rd in raw:
            parent = TreeNode(
                id=rd["id"],
                kind=NodeKind.CATEGORY,
                name=rd["name"],
                description=rd["description"],
                status=rd.get("status", "active"),
                tags=rd.get("tags", []),
            )
            self._id_map[parent.id] = parent
            for cd in rd.get("children", []):
                child = TreeNode(
                    id=cd["id"],
                    kind=NodeKind.ITEM,
                    name=cd["name"],
                    description=cd["description"],
                    status=cd.get("status", "active"),
                    tags=cd.get("tags", []),
                    parent=parent,
                )
                self._id_map[child.id] = child
                parent.children.append(child)
            self._roots.append(parent)

    # ── mutations ──────────────────────────────────────────
    def update_node(
        self, node: TreeNode, name: str = None, description: str = None, status: str = None
    ):
        if name is not None:
            node.name = name
        if description is not None:
            node.description = description
        if status is not None:
            node.status = status
        self.node_updated.emit(node.id)
        self.status_message.emit(f"Updated '{node.name}'.")

    def add_child(self, parent: TreeNode, name: str, description: str = "") -> TreeNode:
        self._next_id += 1
        child = TreeNode(
            id=self._next_id,
            kind=NodeKind.ITEM,
            name=name,
            description=description,
            status="active",
            parent=parent,
        )
        parent.children.append(child)
        self._id_map[child.id] = child
        self.node_added.emit(parent.id, len(parent.children) - 1)
        self.status_message.emit(f"Added '{name}' to '{parent.name}'.")
        return child

    def remove_node(self, node: TreeNode):
        name = node.name
        if node.parent:
            node.parent.children.remove(node)
        else:
            self._roots.remove(node)
        self._id_map.pop(node.id, None)
        self.node_removed.emit(node.id)
        self.status_message.emit(f"Removed '{name}'.")

    # ── actions (ViewModel → View via signal) ─────────────
    def trigger_action(self, action: str, node: TreeNode):
        """
        Named actions dispatched to the View.
        action: "open" | "edit" | "properties" | "add_child"
                | "delete" | "refresh" | "expand_all" | "collapse_all"
        """
        self.action_triggered.emit(action, node)


# ═══════════════════════════════════════════════════════════
# 4. Qt ITEM MODEL  (adapter over TreeViewModel)
# ═══════════════════════════════════════════════════════════


class TreeItemModel(QAbstractItemModel):
    """
    Bridges TreeViewModel ↔ QTreeView.
    Internal pointer of each QModelIndex = TreeNode object.
    """

    COL_NAME = 0
    COL_STATUS = 1
    COL_TAGS = 2

    HEADERS = ["Name", "Status", "Tags"]

    def __init__(self, vm: TreeViewModel):
        super().__init__()
        self._vm = vm
        # ViewModel → Qt signals
        vm.load_finished.connect(self._on_load_finished)
        vm.node_updated.connect(self._on_node_updated)
        vm.node_added.connect(self._on_node_added)
        vm.node_removed.connect(self._on_node_removed)

    # ── QAbstractItemModel required ────────────────────────
    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, col, parent):
            return QModelIndex()
        if not parent.isValid():
            node = self._vm.roots[row]
        else:
            parent_node: TreeNode = parent.internalPointer()
            node = parent_node.child_at(row)
        if node is None:
            return QModelIndex()
        return self.createIndex(row, col, node)

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        node: TreeNode = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        p = node.parent
        if p.parent is None:
            row = self._vm.roots.index(p)
        else:
            row = p.parent.children.index(p)
        return self.createIndex(row, 0, p)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self._vm.roots)
        node: TreeNode = parent.internalPointer()
        return node.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.HEADERS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        node: TreeNode = index.internalPointer()
        col = index.column()

        if role == Qt.DisplayRole:
            if col == self.COL_NAME:
                return node.name
            if col == self.COL_STATUS:
                return node.status.capitalize()
            if col == self.COL_TAGS:
                return ", ".join(node.tags)

        if role == Qt.DecorationRole and col == self.COL_NAME:
            return self._icon_for(node)

        if role == Qt.ForegroundRole:
            return self._fg_color(node)

        if role == Qt.ToolTipRole:
            return (
                f"<b>{node.name}</b><br>"
                f"{node.description}<br>"
                f"Status: <i>{node.status}</i><br>"
                f"Tags: {', '.join(node.tags) or '—'}"
            )

        if role == Qt.UserRole:
            return node  # pass the raw node for context menus

        if role == Qt.FontRole:
            if node.kind == NodeKind.CATEGORY:
                f = QFont()
                f.setBold(True)
                return f

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.HEADERS[section]
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # ── icon / color helpers ───────────────────────────────
    def _icon_for(self, node: TreeNode) -> QIcon:
        if node.is_loading:
            return IconFactory.get("loading")
        if node.kind == NodeKind.CATEGORY:
            return IconFactory.get("folder")
        # child icon depends on status
        mapping = {
            "active": "item",
            "warning": "item_warning",
            "error": "item_error",
            "disabled": "item_disabled",
        }
        return IconFactory.get(mapping.get(node.status, "item"))

    def _fg_color(self, node: TreeNode) -> QColor:
        colors = {
            "active": QColor("#000000"),
            "warning": QColor("#8a6000"),
            "error": QColor("#a31515"),
            "disabled": QColor("#909090"),
        }
        return colors.get(node.status, QColor("#000000"))

    # ── ViewModel → Qt model signals ──────────────────────
    def _on_load_finished(self):
        self.beginResetModel()
        self.endResetModel()

    def _on_node_updated(self, node_id: int):
        node = self._vm.node_by_id(node_id)
        if node is None:
            return
        row = node.row_in_parent()
        parent_idx = self._parent_index(node)
        tl = self.index(row, 0, parent_idx)
        br = self.index(row, self.columnCount() - 1, parent_idx)
        self.dataChanged.emit(tl, br)

    def _on_node_added(self, parent_id: int, child_row: int):
        parent_node = self._vm.node_by_id(parent_id)
        if parent_node is None:
            return
        parent_idx = self._node_index(parent_node)
        self.beginInsertRows(parent_idx, child_row, child_row)
        self.endInsertRows()

    def _on_node_removed(self, node_id: int):
        # Node already removed from VM — just reset
        self.beginResetModel()
        self.endResetModel()

    def _parent_index(self, node: TreeNode) -> QModelIndex:
        if node.parent is None:
            return QModelIndex()
        return self._node_index(node.parent)

    def _node_index(self, node: TreeNode) -> QModelIndex:
        if node.parent is None:
            row = self._vm.roots.index(node)
        else:
            row = node.parent.children.index(node)
        return self.createIndex(row, 0, node)


# ═══════════════════════════════════════════════════════════
# 5. DIALOGS
# ═══════════════════════════════════════════════════════════


class EditDialog(QDialog):
    """Edit a node's name, description and status."""

    STATUSES = ["active", "warning", "error", "disabled"]

    def __init__(self, node: TreeNode, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit — {node.name}")
        self.setMinimumWidth(400)
        self._node = node

        from PySide6.QtWidgets import QComboBox

        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 10)

        self._name = QLineEdit(node.name)
        self._desc = QTextEdit(node.description)
        self._desc.setFixedHeight(80)
        self._status = QComboBox()
        self._status.addItems(self.STATUSES)
        self._status.setCurrentText(node.status)

        layout.addRow("Name:", self._name)
        layout.addRow("Description:", self._desc)
        layout.addRow("Status:", self._status)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def values(self) -> dict:
        return {
            "name": self._name.text().strip(),
            "description": self._desc.toPlainText().strip(),
            "status": self._status.currentText(),
        }


class PropertiesDialog(QDialog):
    """Read-only property sheet for a node."""

    def __init__(self, node: TreeNode, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Properties — {node.name}")
        self.setMinimumWidth(420)

        layout = QFormLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(14, 14, 14, 10)

        def ro(text):
            l = QLineEdit(text)
            l.setReadOnly(True)
            l.setStyleSheet("background:#f0f0f0;border:1px solid #c0c0c0;")
            return l

        layout.addRow("ID:", ro(str(node.id)))
        layout.addRow("Kind:", ro(node.kind.name.capitalize()))
        layout.addRow("Name:", ro(node.name))
        layout.addRow("Status:", ro(node.status))
        layout.addRow("Tags:", ro(", ".join(node.tags) or "—"))

        desc = QTextEdit(node.description)
        desc.setReadOnly(True)
        desc.setFixedHeight(70)
        desc.setStyleSheet("background:#f0f0f0;border:1px solid #c0c0c0;")
        layout.addRow("Description:", desc)

        child_count = node.child_count() if node.kind == NodeKind.CATEGORY else "—"
        layout.addRow("Children:", ro(str(child_count)))

        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(self.reject)
        btns.accepted.connect(self.accept)
        layout.addRow(btns)


class AddChildDialog(QDialog):
    """Add a new child item under a category."""

    def __init__(self, parent_node: TreeNode, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Add Item to '{parent_node.name}'")
        self.setMinimumWidth(360)

        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 10)

        self._name = QLineEdit()
        self._name.setPlaceholderText("Enter item name…")
        self._desc = QLineEdit()
        self._desc.setPlaceholderText("Short description…")

        layout.addRow("Name:", self._name)
        layout.addRow("Description:", self._desc)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addRow(btns)

    def values(self) -> dict:
        return {
            "name": self._name.text().strip(),
            "description": self._desc.text().strip(),
        }


# ═══════════════════════════════════════════════════════════
# 6. DETAIL PANEL  (right side)
# ═══════════════════════════════════════════════════════════


class DetailPanel(QWidget):
    """Displays the selected node's full details."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        vl = QVBoxLayout(self)
        vl.setContentsMargins(6, 4, 6, 4)
        vl.setSpacing(4)

        title = QLabel("Node Details")
        title.setStyleSheet("font-weight:700;font-size:12px;")
        vl.addWidget(title)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#c0c0c0;")
        vl.addWidget(sep)

        def row(label: str):
            hl = QHBoxLayout()
            lbl = QLabel(label)
            lbl.setFixedWidth(80)
            lbl.setStyleSheet("font-weight:600;font-size:11px;color:#555;")
            val = QLabel("—")
            val.setStyleSheet("font-size:11px;")
            val.setWordWrap(True)
            hl.addWidget(lbl)
            hl.addWidget(val, stretch=1)
            return hl, val

        r1, self._lbl_name = row("Name:")
        r2, self._lbl_kind = row("Kind:")
        r3, self._lbl_status = row("Status:")
        r4, self._lbl_tags = row("Tags:")
        r5, self._lbl_id = row("ID:")

        for r in (r1, r2, r3, r4, r5):
            vl.addLayout(r)

        desc_lbl = QLabel("Description:")
        desc_lbl.setStyleSheet("font-weight:600;font-size:11px;color:#555;")
        vl.addWidget(desc_lbl)

        self._desc = QPlainTextEdit()
        self._desc.setReadOnly(True)
        self._desc.setStyleSheet(
            "QPlainTextEdit{background:#fafafa;border:1px solid #d0d0d0;"
            "font-size:11px;font-family:Segoe UI,sans-serif;}"
        )
        self._desc.setFixedHeight(90)
        vl.addWidget(self._desc)

        # Status indicator badge
        self._badge = QLabel("")
        self._badge.setAlignment(Qt.AlignCenter)
        self._badge.setFixedHeight(22)
        self._badge.setStyleSheet("font-size:11px;border-radius:3px;padding:1px 8px;")
        vl.addWidget(self._badge)

        vl.addStretch()

    def show_node(self, node: TreeNode | None):
        if node is None:
            for lbl in (
                self._lbl_name,
                self._lbl_kind,
                self._lbl_status,
                self._lbl_tags,
                self._lbl_id,
            ):
                lbl.setText("—")
            self._desc.setPlainText("")
            self._badge.setText("")
            return

        self._lbl_name.setText(node.name)
        self._lbl_kind.setText(node.kind.name.capitalize())
        self._lbl_status.setText(node.status.capitalize())
        self._lbl_tags.setText(", ".join(node.tags) or "—")
        self._lbl_id.setText(str(node.id))
        self._desc.setPlainText(node.description)

        badge_styles = {
            "active": ("Active", "#d4edda", "#155724", "#c3e6cb"),
            "warning": ("Warning", "#fff3cd", "#856404", "#ffeeba"),
            "error": ("Error", "#f8d7da", "#721c24", "#f5c6cb"),
            "disabled": ("Disabled", "#e2e3e5", "#383d41", "#d6d8db"),
        }
        label, bg, fg, border = badge_styles.get(
            node.status, ("Unknown", "#e2e3e5", "#000", "#ccc")
        )
        self._badge.setText(f"● {label}")
        self._badge.setStyleSheet(
            f"font-size:11px;border-radius:3px;padding:1px 8px;"
            f"background:{bg};color:{fg};border:1px solid {border};"
        )


# ═══════════════════════════════════════════════════════════
# 7. MAIN WINDOW
# ═══════════════════════════════════════════════════════════

COMPACT_QSS = """
* { font-family: "Segoe UI", Tahoma, sans-serif; font-size: 11px; color: #000; }
QWidget    { background: #f0f0f0; }
QMainWindow { background: #f0f0f0; }

QGroupBox {
    border: 1px solid #adadad; border-radius: 0; margin-top: 14px;
    padding: 4px; background: #f0f0f0;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 6px; top: 1px; padding: 0 2px; font-weight: 700; background: #f0f0f0;
}

QTreeView {
    background: #fff; alternate-background-color: #f7f7f7;
    gridline-color: #e0e0e0; border: 1px solid #adadad;
    selection-background-color: #cce4ff; selection-color: #000;
    show-decoration-selected: 1;
}
QTreeView::item            { padding: 2px 4px; min-height: 20px; }
QTreeView::item:selected   { background: #cce4ff; }
QTreeView::item:hover      { background: #e8f0fe; }
QTreeView::branch:has-siblings:!adjoins-item { border-image: none; }
QTreeView::branch:has-children:!has-siblings:closed,
QTreeView::branch:closed:has-children:has-siblings {
    image: none; border: none;
}

QHeaderView::section {
    background: #e1e1e1; border: none;
    border-right: 1px solid #c0c0c0; border-bottom: 1px solid #c0c0c0;
    padding: 2px 6px; font-weight: 700; font-size: 11px;
}

QPushButton {
    background: #e1e1e1; border: 1px solid #adadad; border-radius: 0;
    padding: 2px 10px; min-height: 20px; font-size: 11px;
}
QPushButton:hover   { background: #e8f0fe; border-color: #0078d7; }
QPushButton:pressed { background: #cce4ff; border-color: #0078d7; }
QPushButton#loadBtn   { background: #d0e8ff; border-color: #0078d7; font-weight:700; }
QPushButton#addBtn    { background: #d4edda; border-color: #5cb85c; }
QPushButton#deleteBtn { background: #f8d7da; border-color: #dc3545; }
QPushButton#expandBtn { background: #fff3cd; border-color: #f0ad4e; }

QMenu { background: #fff; border: 1px solid #adadad; }
QMenu::item { padding: 4px 24px 4px 24px; min-height: 20px; }
QMenu::item:selected { background: #cce4ff; }
QMenu::separator { height: 1px; background: #d0d0d0; margin: 2px 0; }

QStatusBar { background: #f0f0f0; border-top: 1px solid #c0c0c0; }
QSplitter::handle { background: #c0c0c0; width: 3px; }
QDialog { background: #f0f0f0; }
QLineEdit {
    background: #fff; border: 1px solid #adadad; border-radius: 0;
    padding: 1px 3px; min-height: 18px; max-height: 20px;
}
QLineEdit:focus { border-color: #0078d7; }
QTextEdit, QPlainTextEdit {
    background: #fff; border: 1px solid #adadad; border-radius: 0;
}
QComboBox {
    background: #fff; border: 1px solid #adadad; border-radius: 0;
    padding: 1px 16px 1px 3px; min-height: 18px; max-height: 20px;
}
QComboBox::drop-down { width: 14px; border-left: 1px solid #adadad; background: #e1e1e1; }
QComboBox QAbstractItemView { background: #fff; selection-background-color: #cce4ff; }
QLabel { background: transparent; }
"""


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MVVM TreeView  —  DB Simulation, Context Menus, Icons")
        self.resize(1060, 640)
        self.setStyleSheet(COMPACT_QSS)

        # ── ViewModel ──────────────────────────────────────
        self._vm = TreeViewModel()
        self._vm.load_started.connect(self._on_load_started)
        self._vm.load_finished.connect(self._on_load_finished)
        self._vm.action_triggered.connect(self._on_action)
        self._vm.status_message.connect(self._on_status)

        # ── Qt item model ──────────────────────────────────
        self._model = TreeItemModel(self._vm)

        self._build_ui()

        # ── Kick off DB load after window shows ────────────
        QTimer.singleShot(200, self._vm.load_from_db)

    # ─── UI construction ──────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_vl = QVBoxLayout(central)
        root_vl.setContentsMargins(6, 6, 6, 4)
        root_vl.setSpacing(4)

        # Title
        title = QLabel("Project Browser  —  MVVM QTreeView")
        title.setStyleSheet("font-weight:700;font-size:13px;padding:2px 0;")
        root_vl.addWidget(title)

        # Splitter: tree (left) + detail panel (right)
        splitter = QSplitter(Qt.Horizontal)

        # Tree group — created BEFORE toolbar so _tree exists when signals connect
        tree_grp = QGroupBox("Project Tree")
        tree_vl = QVBoxLayout(tree_grp)
        tree_vl.setContentsMargins(3, 3, 3, 3)

        self._tree = QTreeView()
        self._tree.setModel(self._model)
        self._tree.setAlternatingRowColors(True)
        self._tree.setAnimated(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.setIconSize(QSize(16, 16))
        self._tree.setIndentation(20)

        # Column widths
        hh = self._tree.header()
        hh.setStretchLastSection(False)
        hh.resizeSection(0, 240)
        hh.resizeSection(1, 80)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        # Signals
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.doubleClicked.connect(self._on_double_click)
        self._tree.selectionModel().currentChanged.connect(self._on_selection)

        tree_vl.addWidget(self._tree)
        splitter.addWidget(tree_grp)

        # Toolbar built AFTER _tree exists
        tb = self._build_toolbar()
        root_vl.addWidget(tb)

        # Detail panel group
        detail_grp = QGroupBox("Details")
        detail_vl = QVBoxLayout(detail_grp)
        detail_vl.setContentsMargins(3, 3, 3, 3)
        self._detail = DetailPanel()
        detail_vl.addWidget(self._detail)
        splitter.addWidget(detail_grp)

        splitter.setSizes([680, 340])
        root_vl.addWidget(splitter, stretch=1)

        # Status bar
        self._sb = QStatusBar()
        self.setStatusBar(self._sb)
        self._sb.showMessage("Initialising…")

    def _build_toolbar(self) -> QGroupBox:
        grp = QGroupBox("Toolbar")
        hl = QHBoxLayout(grp)
        hl.setContentsMargins(6, 4, 6, 4)
        hl.setSpacing(4)

        def btn(text, icon_name, obj_name=None) -> QPushButton:
            b = QPushButton(text)
            b.setIcon(IconFactory.get(icon_name))
            if obj_name:
                b.setObjectName(obj_name)
            return b

        self._btn_load = btn("Reload from DB", "refresh", "loadBtn")
        self._btn_add = btn("Add Item", "add", "addBtn")
        self._btn_delete = btn("Delete Selected", "delete", "deleteBtn")
        self._btn_expand = btn("Expand All", "expand", "expandBtn")
        self._btn_collapse = btn("Collapse All", "collapse")
        self._btn_edit = btn("Edit Selected", "edit")

        self._btn_load.clicked.connect(lambda: self._vm.load_from_db())
        self._btn_add.clicked.connect(self._toolbar_add)
        self._btn_delete.clicked.connect(self._toolbar_delete)
        self._btn_expand.clicked.connect(lambda: self._tree.expandAll())
        self._btn_collapse.clicked.connect(lambda: self._tree.collapseAll())
        self._btn_edit.clicked.connect(self._toolbar_edit)

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("color:#adadad;")

        for w in (
            self._btn_load,
            sep,
            self._btn_add,
            self._btn_delete,
            self._btn_edit,
            self._btn_expand,
            self._btn_collapse,
        ):
            hl.addWidget(w)
        hl.addStretch()
        return grp

    # ─── selection ────────────────────────────────────────
    def _current_node(self) -> TreeNode | None:
        idx = self._tree.currentIndex()
        if not idx.isValid():
            return None
        return idx.data(Qt.UserRole)

    def _on_selection(self, current: QModelIndex, _prev: QModelIndex):
        node = current.data(Qt.UserRole) if current.isValid() else None
        self._detail.show_node(node)

    # ─── double-click (default action) ────────────────────
    def _on_double_click(self, index: QModelIndex):
        node: TreeNode = index.data(Qt.UserRole)
        if node is None:
            return
        if node.kind == NodeKind.CATEGORY:
            # Default: toggle expand/collapse
            if self._tree.isExpanded(index):
                self._tree.collapse(index)
            else:
                self._tree.expand(index)
            self._vm.trigger_action("expand", node)
        else:
            # Default: open edit dialog
            self._vm.trigger_action("edit", node)

    # ─── context menu ─────────────────────────────────────
    def _on_context_menu(self, pos):
        index = self._tree.indexAt(pos)
        if not index.isValid():
            return
        node: TreeNode = index.data(Qt.UserRole)
        if node is None:
            return
        global_pos = self._tree.viewport().mapToGlobal(pos)

        if node.kind == NodeKind.CATEGORY:
            self._show_category_menu(node, global_pos)
        else:
            self._show_item_menu(node, global_pos)

    def _show_category_menu(self, node: TreeNode, pos):
        """Context menu for CATEGORY (parent) nodes."""
        menu = QMenu(self)

        # Header label (non-clickable)
        header = QAction(f"📁  {node.name}", self)
        header.setEnabled(False)
        menu.addAction(header)
        menu.addSeparator()

        a_expand = QAction(IconFactory.get("expand"), "Expand", self)
        a_collapse = QAction(IconFactory.get("collapse"), "Collapse", self)
        a_add = QAction(IconFactory.get("add"), "Add Item…", self)
        a_edit = QAction(IconFactory.get("edit"), "Edit Category…", self)
        a_props = QAction(IconFactory.get("properties"), "Properties…", self)
        menu.addSeparator()
        a_delete = QAction(IconFactory.get("delete"), "Delete Category", self)

        a_expand.triggered.connect(lambda: self._tree.expand(self._index_for(node)))
        a_collapse.triggered.connect(lambda: self._tree.collapse(self._index_for(node)))
        a_add.triggered.connect(lambda: self._vm.trigger_action("add_child", node))
        a_edit.triggered.connect(lambda: self._vm.trigger_action("edit", node))
        a_props.triggered.connect(lambda: self._vm.trigger_action("properties", node))
        a_delete.triggered.connect(lambda: self._vm.trigger_action("delete", node))

        for action in (a_expand, a_collapse, a_add, a_edit, a_props, menu.addSeparator(), a_delete):
            if isinstance(action, QAction):
                menu.addAction(action)

        menu.exec(pos)

    def _show_item_menu(self, node: TreeNode, pos):
        """Context menu for ITEM (child) nodes."""
        menu = QMenu(self)

        # Header label
        icon_map = {
            "active": "item",
            "warning": "item_warning",
            "error": "item_error",
            "disabled": "item_disabled",
        }
        header = QAction(IconFactory.get(icon_map.get(node.status, "item")), f"  {node.name}", self)
        header.setEnabled(False)
        menu.addAction(header)
        menu.addSeparator()

        # Default action (same as double-click) — visually marked
        a_edit = QAction(IconFactory.get("edit"), "✎  Edit…  (default)", self)
        a_props = QAction(IconFactory.get("properties"), "Properties…", self)
        a_info = QAction(IconFactory.get("info"), "View Description…", self)
        menu.addSeparator()

        # Status change submenu
        status_menu = menu.addMenu("Set Status")
        for s in ("active", "warning", "error", "disabled"):
            sa = QAction(s.capitalize(), self)
            sa.setCheckable(True)
            sa.setChecked(node.status == s)
            _s = s  # capture
            sa.triggered.connect(
                lambda checked, status=_s: self._vm.update_node(node, status=status)
            )
            status_menu.addAction(sa)

        menu.addSeparator()
        a_delete = QAction(IconFactory.get("delete"), "Delete Item", self)

        a_edit.triggered.connect(lambda: self._vm.trigger_action("edit", node))
        a_props.triggered.connect(lambda: self._vm.trigger_action("properties", node))
        a_info.triggered.connect(lambda: self._vm.trigger_action("open", node))
        a_delete.triggered.connect(lambda: self._vm.trigger_action("delete", node))

        for action in (a_edit, a_props, a_info, a_delete):
            menu.addAction(action)

        menu.exec(pos)

    # ─── action handler (ViewModel → View) ───────────────
    def _on_action(self, action: str, node: TreeNode):
        """
        Central dispatcher for all named actions.
        ViewModel emits action_triggered → this method handles UI.
        """
        if action == "edit":
            dlg = EditDialog(node, self)
            if dlg.exec() == QDialog.Accepted:
                v = dlg.values()
                if v["name"]:
                    self._vm.update_node(node, **v)

        elif action == "properties":
            PropertiesDialog(node, self).exec()

        elif action == "open":
            QMessageBox.information(
                self,
                f"Description — {node.name}",
                f"<b>{node.name}</b><br><br>{node.description or '(no description)'}",
            )

        elif action == "add_child":
            if node.kind != NodeKind.CATEGORY:
                return
            dlg = AddChildDialog(node, self)
            if dlg.exec() == QDialog.Accepted:
                v = dlg.values()
                if v["name"]:
                    new_child = self._vm.add_child(node, v["name"], v["description"])
                    # Expand parent so new child is visible
                    parent_idx = self._index_for(node)
                    self._tree.expand(parent_idx)

        elif action == "delete":
            kind_word = "category and all its items" if node.kind == NodeKind.CATEGORY else "item"
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Delete {kind_word} '{node.name}'?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self._vm.remove_node(node)

        elif action in ("expand", "collapse_all", "expand_all"):
            pass  # handled directly in toolbar / double-click

    # ─── toolbar actions ──────────────────────────────────
    def _toolbar_add(self):
        node = self._current_node()
        if node is None:
            QMessageBox.information(self, "No Selection", "Select a category to add an item to.")
            return
        target = node if node.kind == NodeKind.CATEGORY else node.parent
        if target is None:
            return
        self._vm.trigger_action("add_child", target)

    def _toolbar_delete(self):
        node = self._current_node()
        if node is None:
            QMessageBox.information(self, "No Selection", "Select a node to delete.")
            return
        self._vm.trigger_action("delete", node)

    def _toolbar_edit(self):
        node = self._current_node()
        if node is None:
            QMessageBox.information(self, "No Selection", "Select a node to edit.")
            return
        self._vm.trigger_action("edit", node)

    # ─── load state ───────────────────────────────────────
    def _on_load_started(self):
        self._btn_load.setEnabled(False)
        self._btn_load.setText("Loading…")
        self._sb.showMessage("Fetching data from database…")

    def _on_load_finished(self):
        self._btn_load.setEnabled(True)
        self._btn_load.setText("Reload from DB")
        self._tree.expandToDepth(0)  # expand categories only

    def _on_status(self, msg: str):
        self._sb.showMessage(msg)

    # ─── helper: get QModelIndex for a node ───────────────
    def _index_for(self, node: TreeNode) -> QModelIndex:
        if node.parent is None:
            row = self._vm.roots.index(node)
            return self._model.index(row, 0, QModelIndex())
        p_idx = self._index_for(node.parent)
        return self._model.index(node.row_in_parent(), 0, p_idx)


# ═══════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
