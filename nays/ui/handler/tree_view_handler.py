"""
tree_view_handler.py
====================
Reusable PySide6 TreeViewHandler that wraps an existing QTreeView widget.

Features
--------
- Attach to any existing QTreeView — no subclassing required
- N-level deep tree (unlimited nesting via a configurable children key)
- Configurable display columns (which data keys to show)
- Re-configurable context menu per node type (parent / child / root / any)
- Double-click action configurable per node type
- Per-status icon coloring painted with QPainter (no image files needed)
- Signals + callback registration API (mirrors TableViewHandler)
- Built-in Default and Dark stylesheets
- Load data from any Python data source (list of dicts)

Quick-start
-----------
    handler = TreeViewHandler(treeView=myTreeWidget)

    handler.setColumns([
        {"key": "name",   "label": "Name",   "width": 220},
        {"key": "status", "label": "Status", "width": 80},
    ])

    handler.setContextMenuActions([
        {"label": "Edit",       "action": "edit",      "icon": "edit",   "nodeFilter": "child"},
        {"label": "Add Child",  "action": "add_child", "icon": "add",    "nodeFilter": "parent"},
        {"separator": True},
        {"label": "Delete",     "action": "delete",    "icon": "delete"},
    ])

    handler.loadData([
        {"id": 1, "name": "Category", "status": "active",
         "children": [{"id": 11, "name": "Item", "status": "active"}]}
    ])

    handler.onActionTriggered("edit",   lambda data: ...)
    handler.onSelectionChanged(lambda data: ...)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from PySide6.QtCore import (
    Qt, Signal, QObject, QModelIndex, QAbstractItemModel, QSize, QPoint
)
from PySide6.QtGui import (
    QColor, QPainter, QPixmap, QIcon,
    QPen, QBrush, QFont, QPainterPath, QAction
)
from PySide6.QtWidgets import (
    QTreeView, QMenu, QAbstractItemView, QHeaderView, QApplication
)

from nays.ui.helper import main_icons  # noqa: F401 — registers Qt resources
from nays.ui.helper.icon_helper import getIconFromResource


# ═══════════════════════════════════════════════════════════
# CONTEXT MENU ICON MAPPING
# ═══════════════════════════════════════════════════════════

# Map icon name strings → Qt resource paths for context menu actions
_CONTEXT_MENU_ICON_MAP = {
    "edit":       ":/16/fugue-icons/icons/pencil.png",
    "delete":     ":/16/fugue-icons/icons/bin.png",
    "add":        ":/16/fugue-icons/icons/plus.png",
    "remove":     ":/16/fugue-icons/icons/minus.png",
    "properties": ":/16/fugue-icons/icons/property.png",
    "expand":     ":/16/fugue-icons/icons/folder-open.png",
    "collapse":   ":/16/fugue-icons/icons/folder.png",
    "refresh":    ":/16/fugue-icons/icons/arrow-circle.png",
    "info":       ":/16/fugue-icons/icons/information.png",
    "search":     ":/16/fugue-icons/icons/magnifier.png",
    "loading":    ":/16/fugue-icons/icons/arrow-circle.png",
}


# ═══════════════════════════════════════════════════════════
# INTERNAL: Icon Factory
# ═══════════════════════════════════════════════════════════

class _IconFactory:
    """Paints QIcon objects on-the-fly — no external image files needed."""

    _cache: Dict[str, QIcon] = {}

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
        p  = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        dispatch = {
            "folder":        cls._folder,
            "folder_open":   cls._folder_open,
            "item":          cls._item,
            "item_warning":  cls._item_warning,
            "item_error":    cls._item_error,
            "item_disabled": cls._item_disabled,
            "loading":       cls._loading,
            "add":           cls._add,
            "delete":        cls._delete,
            "edit":          cls._edit,
            "refresh":       cls._refresh,
            "expand":        cls._expand,
            "collapse":      cls._collapse,
            "info":          cls._info,
            "properties":    cls._properties,
        }
        dispatch.get(name, cls._unknown)(p, size)
        p.end()
        return QIcon(px)

    @staticmethod
    def _folder(p, s):
        p.setBrush(QColor("#f0ad4e")); p.setPen(QPen(QColor("#c87f0a"), 1))
        path = QPainterPath()
        path.moveTo(1, s*0.45); path.lineTo(1, s*0.9); path.lineTo(s-1, s*0.9)
        path.lineTo(s-1, s*0.35); path.lineTo(s*0.55, s*0.35)
        path.lineTo(s*0.45, s*0.2); path.lineTo(s*0.1, s*0.2)
        path.lineTo(s*0.1, s*0.45); path.closeSubpath(); p.drawPath(path)

    @staticmethod
    def _folder_open(p, s):
        p.setBrush(QColor("#ffd080")); p.setPen(QPen(QColor("#c87f0a"), 1))
        path = QPainterPath()
        path.moveTo(1, s*0.9); path.lineTo(s*0.15, s*0.45); path.lineTo(s-1, s*0.45)
        path.lineTo(s-1, s*0.35); path.lineTo(s*0.55, s*0.35)
        path.lineTo(s*0.45, s*0.2); path.lineTo(s*0.1, s*0.2)
        path.lineTo(s*0.1, s*0.45); path.lineTo(1, s*0.45)
        path.closeSubpath(); p.drawPath(path)

    @staticmethod
    def _item(p, s):
        p.setBrush(QColor("#5b9bd5")); p.setPen(QPen(QColor("#2e6da4"), 1))
        p.drawRoundedRect(2, 2, s-4, s-4, 2, 2)
        p.setPen(QPen(QColor("#ffffff"), 1.2))
        m = s // 4; p.drawLine(m, s//2, s-m, s//2); p.drawLine(s//2, m, s//2, s-m)

    @staticmethod
    def _item_warning(p, s):
        p.setBrush(QColor("#f0ad4e")); p.setPen(QPen(QColor("#c87f0a"), 1))
        from PySide6.QtCore import QPoint
        p.drawPolygon([QPoint(s//2, 1), QPoint(s-1, s-2), QPoint(1, s-2)])
        p.setPen(QPen(QColor("#7a4800"), 1.5))
        p.drawLine(s//2, s//3, s//2, s*2//3); p.drawPoint(s//2, s*3//4)

    @staticmethod
    def _item_error(p, s):
        p.setBrush(QColor("#d9534f")); p.setPen(QPen(QColor("#8b1a18"), 1))
        p.drawEllipse(1, 1, s-2, s-2)
        p.setPen(QPen(QColor("#ffffff"), 1.8))
        m = s // 3; p.drawLine(m, m, s-m, s-m); p.drawLine(s-m, m, m, s-m)

    @staticmethod
    def _item_disabled(p, s):
        p.setBrush(QColor("#aaaaaa")); p.setPen(QPen(QColor("#777777"), 1))
        p.drawRoundedRect(2, 2, s-4, s-4, 2, 2)

    @staticmethod
    def _loading(p, s):
        p.setBrush(Qt.NoBrush)
        for i in range(8):
            angle = i * 45; rad = math.radians(angle); alpha = 40 + int(215 * i / 7)
            p.setPen(QPen(QColor(80, 80, 200, alpha), 1.5))
            cx, cy, r = s/2, s/2, s/2 - 2
            p.drawLine(
                int(cx + r*0.5*math.cos(rad)), int(cy + r*0.5*math.sin(rad)),
                int(cx + r*math.cos(rad)),     int(cy + r*math.sin(rad)),
            )

    @staticmethod
    def _add(p, s):
        p.setBrush(QColor("#5cb85c")); p.setPen(QPen(QColor("#3d8b3d"), 1))
        p.drawEllipse(1, 1, s-2, s-2)
        p.setPen(QPen(QColor("#ffffff"), 2))
        m = s // 4; p.drawLine(s//2, m, s//2, s-m); p.drawLine(m, s//2, s-m, s//2)

    @staticmethod
    def _delete(p, s):
        p.setBrush(QColor("#d9534f")); p.setPen(QPen(QColor("#8b1a18"), 1))
        p.drawRoundedRect(1, 1, s-2, s-2, 2, 2)
        p.setPen(QPen(QColor("#ffffff"), 2))
        m = s // 4; p.drawLine(m, m, s-m, s-m); p.drawLine(s-m, m, m, s-m)

    @staticmethod
    def _edit(p, s):
        p.setBrush(QColor("#5b9bd5")); p.setPen(QPen(QColor("#2e6da4"), 1))
        path = QPainterPath()
        path.moveTo(s*0.7, s*0.1); path.lineTo(s*0.9, s*0.3)
        path.lineTo(s*0.3, s*0.9); path.lineTo(s*0.1, s*0.9)
        path.lineTo(s*0.1, s*0.7); path.closeSubpath(); p.drawPath(path)

    @staticmethod
    def _refresh(p, s):
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor("#0078d7"), 2))
        p.drawArc(2, 2, s-4, s-4, 30*16, 300*16)
        p.setBrush(QColor("#0078d7")); p.setPen(Qt.NoPen)
        angle = math.radians(30); cx, cy, r = s/2, s/2, s/2-2
        ax = cx + r*math.cos(angle); ay = cy - r*math.sin(angle)
        from PySide6.QtCore import QPoint
        p.drawPolygon([QPoint(int(ax), int(ay)-3), QPoint(int(ax)+4, int(ay)+2), QPoint(int(ax)-2, int(ay)+3)])

    @staticmethod
    def _expand(p, s):
        p.setBrush(QColor("#e1e1e1")); p.setPen(QPen(QColor("#adadad"), 1))
        p.drawRect(1, 1, s-2, s-2); p.setPen(QPen(QColor("#000"), 1.5))
        m = s // 4; p.drawLine(m, s//2, s-m, s//2); p.drawLine(s//2, m, s//2, s-m)

    @staticmethod
    def _collapse(p, s):
        p.setBrush(QColor("#e1e1e1")); p.setPen(QPen(QColor("#adadad"), 1))
        p.drawRect(1, 1, s-2, s-2); p.setPen(QPen(QColor("#000"), 1.5))
        m = s // 4; p.drawLine(m, s//2, s-m, s//2)

    @staticmethod
    def _info(p, s):
        p.setBrush(QColor("#5b9bd5")); p.setPen(QPen(QColor("#2e6da4"), 1))
        p.drawEllipse(1, 1, s-2, s-2)
        p.setPen(QPen(Qt.white, 1.8)); p.drawText(0, 0, s, s, Qt.AlignCenter, "i")

    @staticmethod
    def _properties(p, s):
        p.setBrush(Qt.NoBrush); p.setPen(QPen(QColor("#555"), 1.5))
        for y in [s//4, s//2, s*3//4]: p.drawLine(3, y, s-3, y)

    @staticmethod
    def _unknown(p, s):
        p.setBrush(QColor("#cccccc")); p.setPen(QPen(QColor("#999"), 1))
        p.drawRect(1, 1, s-2, s-2)


# ═══════════════════════════════════════════════════════════
# INTERNAL: Tree Node
# ═══════════════════════════════════════════════════════════

@dataclass
class _TreeNode:
    """
    Internal tree node wrapping the raw user data dict.
    Supports unlimited nesting depth.
    """
    raw:      Dict[str, Any]                  # original dict from caller
    depth:    int                             # 0 = root
    parent:   Optional["_TreeNode"] = field(default=None, repr=False, compare=False)
    children: List["_TreeNode"]     = field(default_factory=list)

    # ── helpers ────────────────────────────────────────────
    def child_count(self) -> int:
        return len(self.children)

    def child_at(self, row: int) -> Optional["_TreeNode"]:
        return self.children[row] if 0 <= row < len(self.children) else None

    def row_in_parent(self) -> int:
        if self.parent:
            return self.parent.children.index(self)
        return 0

    @property
    def is_parent(self) -> bool:
        """True if this node has or can have children (depth == 0 or has children)."""
        return bool(self.children)

    @property
    def is_root(self) -> bool:
        return self.depth == 0


# ═══════════════════════════════════════════════════════════
# INTERNAL: Qt Item Model
# ═══════════════════════════════════════════════════════════

class _TreeItemModel(QAbstractItemModel):
    """
    Bridges a flat list of _TreeNode roots ↔ QTreeView.
    Internal pointer of each QModelIndex = _TreeNode object.
    """

    def __init__(
        self,
        roots: List[_TreeNode],
        columns: List[Dict[str, Any]],
        name_key: str = "name",
        status_key: str = "status",
        icon_key: Optional[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._roots      = roots
        self._columns    = columns   # [{"key": ..., "label": ..., ...}]
        self._name_key   = name_key
        self._status_key = status_key
        self._icon_key   = icon_key          # data key that holds a QIcon path/resource
        self._icon_path_cache: Dict[str, QIcon] = {}  # path -> QIcon cache

    # ── reset ──────────────────────────────────────────────
    def resetData(self, roots: List[_TreeNode]):
        self.beginResetModel()
        self._roots = roots
        self.endResetModel()

    def updateColumns(self, columns: List[Dict[str, Any]]):
        self.beginResetModel()
        self._columns = columns
        self.endResetModel()

    def updateIconKey(self, icon_key: Optional[str]):
        self._icon_key = icon_key
        self._icon_path_cache.clear()
        self.beginResetModel()
        self.endResetModel()

    # ── required overrides ─────────────────────────────────
    def index(self, row: int, col: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, col, parent):
            return QModelIndex()
        if not parent.isValid():
            node = self._roots[row] if row < len(self._roots) else None
        else:
            p_node: _TreeNode = parent.internalPointer()
            node = p_node.child_at(row)
        if node is None:
            return QModelIndex()
        return self.createIndex(row, col, node)

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        node: _TreeNode = index.internalPointer()
        if node.parent is None:
            return QModelIndex()
        p = node.parent
        row = p.parent.children.index(p) if p.parent else self._roots.index(p)
        return self.createIndex(row, 0, p)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            return len(self._roots)
        node: _TreeNode = parent.internalPointer()
        return node.child_count()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return max(len(self._columns), 1)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid():
            return None
        node: _TreeNode = index.internalPointer()
        col = index.column()
        col_cfg = self._columns[col] if col < len(self._columns) else {}
        key = col_cfg.get("key", self._name_key)
        value = node.raw.get(key, "")
        status = node.raw.get(self._status_key, "active")

        if role == Qt.DisplayRole:
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value) if value is not None else ""

        if role == Qt.DecorationRole and col == 0:
            return self._icon_for(node)

        if role == Qt.ForegroundRole:
            return self._fg_color(status)

        if role == Qt.FontRole and col == 0 and node.is_root:
            f = QFont(); f.setBold(True); return f

        if role == Qt.ToolTipRole:
            parts = [f"<b>{node.raw.get(self._name_key, '')}</b>"]
            for c in self._columns[1:]:
                v = node.raw.get(c["key"], "")
                if isinstance(v, list):
                    v = ", ".join(str(x) for x in v)
                parts.append(f"{c.get('label', c['key'])}: <i>{v}</i>")
            return "<br>".join(parts)

        if role == Qt.UserRole:
            return node  # give raw node to context menu handler

        return None

    def headerData(self, section: int, orientation: Qt.Orientation,
                   role: int = Qt.DisplayRole) -> Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section < len(self._columns):
                return self._columns[section].get("label", self._columns[section].get("key", ""))
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    # ── helpers ────────────────────────────────────────────
    def _icon_for(self, node: _TreeNode) -> QIcon:
        # 1. Prefer an explicit icon path/resource stored in the data
        if self._icon_key:
            path = node.raw.get(self._icon_key)
            if path:
                if path not in self._icon_path_cache:
                    self._icon_path_cache[path] = QIcon(path)
                return self._icon_path_cache[path]

        # 2. Fall back to painted icons driven by status
        status = node.raw.get(self._status_key, "active")
        if node.children:
            return _IconFactory.get("folder")
        icon_map = {
            "active":   "item",
            "warning":  "item_warning",
            "error":    "item_error",
            "disabled": "item_disabled",
        }
        return _IconFactory.get(icon_map.get(status, "item"))

    def _fg_color(self, status: str) -> QColor:
        return {
            "active":   QColor("#000000"),
            "warning":  QColor("#8a6000"),
            "error":    QColor("#a31515"),
            "disabled": QColor("#909090"),
        }.get(status, QColor("#000000"))

    # ── node lookup ────────────────────────────────────────
    def indexForNode(self, node: _TreeNode) -> QModelIndex:
        """Return a QModelIndex pointing to node (column 0)."""
        row = node.parent.children.index(node) if node.parent else self._roots.index(node)
        return self.createIndex(row, 0, node)


# ═══════════════════════════════════════════════════════════
# PUBLIC: TreeViewHandler
# ═══════════════════════════════════════════════════════════

class TreeViewHandler(QObject):
    """
    Reusable handler that adds MVVM tree capabilities to any existing QTreeView.

    Signals
    -------
    selectionChanged(dict)          Node data dict of the selected node (or {} if none)
    actionTriggered(str, dict)      (action_name, node_data_dict)
    doubleClicked(dict)             Node data dict on double-click
    dataLoaded(int)                 Total node count after loadData()

    Context menu configuration
    --------------------------
    Each entry in setContextMenuActions() is a dict:

        {"label": "Edit",   "action": "edit",   "icon": "edit",   "nodeFilter": "child"}
        {"separator": True}                         ← inserts a separator line

    nodeFilter values (optional — omit to show for ALL nodes):
        "root"      depth == 0 (top-level nodes)
        "non-root"  depth  > 0
        "parent"    node has children
        "child"     node has no children
        "leaf"      alias for "child"
        callable    fn(node_data: dict, depth: int) -> bool

    Double-click configuration
    --------------------------
    setDoubleClickAction(action, nodeFilter=None)
        action  : str action name emitted on doubleClicked / actionTriggered, or
                  "toggle_expand" (default for parent nodes) to expand/collapse
        nodeFilter: same filter rules as context menu

    Column configuration
    --------------------
    setColumns([
        {"key": "name",   "label": "Name",   "width": 220},
        {"key": "status", "label": "Status", "width": 80},
        {"key": "tags",   "label": "Tags"},          # auto-stretch
    ])

    Data format
    -----------
    loadData([
        {"id": 1, "name": "Category", "status": "active",
         "children": [
             {"id": 11, "name": "Item", "status": "warning"},
         ]},
    ])
    Children key is configurable via childrenKey= constructor argument.
    """

    # Public signals
    selectionChanged = Signal(dict)        # node raw data
    actionTriggered  = Signal(str, dict)  # action_name, node raw data
    doubleClicked    = Signal(dict)        # node raw data
    dataLoaded       = Signal(int)         # total node count

    # ── Built-in stylesheets ───────────────────────────────
    DEFAULT_STYLE = """
        QTreeView {
            border: 1px solid #d0d7de;
            border-radius: 4px;
            background-color: #ffffff;
            alternate-background-color: #f6f8fa;
            gridline-color: #e8ebee;
            selection-background-color: #0969da;
            selection-color: #ffffff;
            font-size: 13px;
            show-decoration-selected: 1;
        }
        QTreeView::item          { padding: 3px 4px; min-height: 22px; }
        QTreeView::item:selected { background: #ddf4ff; color: #1f2328; }
        QTreeView::item:hover    { background: #f6f8fa; }
        QHeaderView::section {
            background-color: #f6f8fa; color: #1f2328;
            padding: 6px 6px; font-weight: 600;
            border: none; border-bottom: 2px solid #d0d7de;
            border-right: 1px solid #e8ebee;
        }
        QHeaderView::section:hover { background-color: #eaeef2; }
        QScrollBar:vertical   { background:#f6f8fa; width:10px; border-radius:5px; }
        QScrollBar::handle:vertical { background:#c9d1d9; border-radius:5px; min-height:20px; }
        QScrollBar::handle:vertical:hover { background:#8b949e; }
        QScrollBar:horizontal { background:#f6f8fa; height:10px; border-radius:5px; }
        QScrollBar::handle:horizontal { background:#c9d1d9; border-radius:5px; min-width:20px; }
        QScrollBar::handle:horizontal:hover { background:#8b949e; }
        QScrollBar::add-line, QScrollBar::sub-line { border:none; background:none; }
        QMenu { background:#fff; border:1px solid #adadad; }
        QMenu::item { padding:4px 24px; min-height:20px; }
        QMenu::item:selected { background:#ddf4ff; }
        QMenu::separator { height:1px; background:#d0d0d0; margin:2px 0; }
    """

    DARK_STYLE = """
        QTreeView {
            border: 1px solid #30363d;
            border-radius: 4px;
            background-color: #0d1117;
            alternate-background-color: #161b22;
            gridline-color: #21262d;
            selection-background-color: #388bfd;
            selection-color: #ffffff;
            font-size: 13px;
            color: #c9d1d9;
            show-decoration-selected: 1;
        }
        QTreeView::item          { padding: 3px 4px; min-height: 22px; }
        QTreeView::item:selected { background: #1f6feb; color: #ffffff; }
        QTreeView::item:hover    { background: #161b22; }
        QHeaderView::section {
            background-color: #161b22; color: #c9d1d9;
            padding: 6px 6px; font-weight: 600;
            border: none; border-bottom: 2px solid #30363d;
            border-right: 1px solid #21262d;
        }
        QHeaderView::section:hover { background-color: #21262d; }
        QScrollBar:vertical   { background:#161b22; width:10px; border-radius:5px; }
        QScrollBar::handle:vertical { background:#30363d; border-radius:5px; min-height:20px; }
        QScrollBar::handle:vertical:hover { background:#484f58; }
        QScrollBar:horizontal { background:#161b22; height:10px; border-radius:5px; }
        QScrollBar::handle:horizontal { background:#30363d; border-radius:5px; min-width:20px; }
        QScrollBar::handle:horizontal:hover { background:#484f58; }
        QScrollBar::add-line, QScrollBar::sub-line { border:none; background:none; }
        QMenu { background:#161b22; border:1px solid #30363d; color:#c9d1d9; }
        QMenu::item { padding:4px 24px; min-height:20px; }
        QMenu::item:selected { background:#1f6feb; }
        QMenu::separator { height:1px; background:#30363d; margin:2px 0; }
    """

    # ── Constructor ────────────────────────────────────────
    def __init__(
        self,
        treeView: QTreeView,
        childrenKey: str = "children",
        nameKey:     str = "name",
        statusKey:   str = "status",
        iconKey:     Optional[str] = None,
        applyDefaultStyle: bool = False,
    ):
        """
        Parameters
        ----------
        treeView          : The existing QTreeView widget to attach to.
        childrenKey       : Key used in data dicts to hold child node lists.
        nameKey           : Key used as display name / label in the first column.
        statusKey         : Key used for status-based icon/colour (fallback only).
        iconKey           : Key in each data dict whose value is a QIcon path or
                            Qt resource string (e.g. ``":/icons/gear.png"``).  When
                            set, this takes priority over the painted status icons.
                            Pass ``None`` to use the built-in painted icons.
        applyDefaultStyle : Apply DEFAULT_STYLE automatically on construction.
        """
        super().__init__(treeView)

        self._treeView    = treeView
        self._childrenKey = childrenKey
        self._nameKey     = nameKey
        self._statusKey   = statusKey
        self._iconKey     = iconKey

        # Internal state
        self._roots:          List[_TreeNode]          = []
        self._columns:        List[Dict[str, Any]]     = [{"key": nameKey, "label": "Name"}]
        self._contextActions: List[Dict[str, Any]]     = []
        self._dblClickRules:  List[Dict[str, Any]]     = []   # [{"action":"...", "nodeFilter":...}]
        self._actionCallbacks: Dict[str, List[Callable]] = {}

        # Build model and wire up view
        self._model = _TreeItemModel(
            roots=self._roots,
            columns=self._columns,
            name_key=self._nameKey,
            status_key=self._statusKey,
            icon_key=self._iconKey,
        )
        self._treeView.setModel(self._model)
        self._treeView.setIconSize(QSize(16, 16))
        self._treeView.setAnimated(True)
        self._treeView.setUniformRowHeights(False)
        self._treeView.setAlternatingRowColors(True)
        self._treeView.setSelectionMode(QAbstractItemView.SingleSelection)
        self._treeView.setContextMenuPolicy(Qt.CustomContextMenu)

        # Wire signals
        self._treeView.customContextMenuRequested.connect(self._onContextMenuRequested)
        self._treeView.doubleClicked.connect(self._onDoubleClicked)
        self._treeView.selectionModel().currentChanged.connect(self._onSelectionChanged)

        if applyDefaultStyle:
            self.applyStyle()

    # ═══════════════════════════════════════════════════════
    # STYLING
    # ═══════════════════════════════════════════════════════

    def applyStyle(self, style: Optional[str] = None):
        """
        Apply a stylesheet.  Pass None to apply DEFAULT_STYLE.
        Use TreeViewHandler.DARK_STYLE for the dark theme.
        """
        self._treeView.setStyleSheet(style if style is not None else self.DEFAULT_STYLE)
        self._treeView.header().setStretchLastSection(True)
        self._treeView.setIndentation(20)

    def applyDarkStyle(self):
        """Apply the built-in dark theme stylesheet."""
        self.applyStyle(self.DARK_STYLE)

    def setCustomStyle(self, stylesheet: str):
        """Apply a fully custom QSS stylesheet."""
        self._treeView.setStyleSheet(stylesheet)

    # ═══════════════════════════════════════════════════════
    # ICON KEY
    # ═══════════════════════════════════════════════════════

    def setIconKey(self, iconKey: Optional[str]):
        """
        Set (or clear) the data key used to load node icons from a path.

        Parameters
        ----------
        iconKey : str or None
            Key in each node's data dict whose value is a file path or Qt
            resource string (e.g. ``":/16/icons/gear.png"``).
            Pass ``None`` to revert to the built-in painted status icons.
        """
        self._iconKey = iconKey
        self._model.updateIconKey(iconKey)

    # ═══════════════════════════════════════════════════════
    # COLUMN CONFIGURATION
    # ═══════════════════════════════════════════════════════

    def setColumns(self, columns: List[Dict[str, Any]]):
        """
        Define which data keys map to tree columns.

        Each column dict supports:
            key   : str  (required) — key into the node raw data dict
            label : str  (optional) — column header text; defaults to key
            width : int  (optional) — fixed column pixel width
            stretch: bool (optional) — if True, column stretches to fill remaining space

        Example::

            handler.setColumns([
                {"key": "name",   "label": "Name",   "width": 220},
                {"key": "status", "label": "Status", "width": 80},
                {"key": "tags",   "label": "Tags",   "stretch": True},
            ])
        """
        self._columns = columns
        self._model.updateColumns(columns)
        self._applyColumnWidths()

    def _applyColumnWidths(self):
        hh = self._treeView.header()
        hh.setStretchLastSection(False)
        for i, col in enumerate(self._columns):
            if col.get("stretch"):
                hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            elif "width" in col:
                hh.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                hh.resizeSection(i, col["width"])
            else:
                hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        # If no column requested stretch, let the last one stretch
        if not any(c.get("stretch") for c in self._columns):
            hh.setStretchLastSection(True)

    # ═══════════════════════════════════════════════════════
    # CONTEXT MENU CONFIGURATION
    # ═══════════════════════════════════════════════════════

    def setContextMenuActions(self, actions: List[Dict[str, Any]]):
        """
        Configure the right-click context menu.

        Each entry is a dict:
            {"label": "Edit",  "action": "edit",  "icon": "edit",  "nodeFilter": "child"}
            {"separator": True}

        Keys
        ----
        label       : str           Menu item text.
        action      : str           Name emitted in actionTriggered signal.
        icon        : str           Icon name from Qt resources (available: "edit", 
                                    "delete", "add", "remove", "properties", "expand", 
                                    "collapse", "refresh", "info", "search", "loading").
        nodeFilter  : str|callable  Visibility condition (see class docstring).
        enabled     : bool|callable If False / callable returning False, item is greyed out.

        Built-in actions with default behaviour (can be overridden via onActionTriggered):
            "expand_all"   — expands all nodes under the selected node
            "collapse_all" — collapses all nodes under the selected node
            "expand_node"  — expands selected node one level
        """
        self._contextActions = actions

    def addContextMenuAction(self, action: Dict[str, Any]):
        """Append a single action entry to the context menu configuration."""
        self._contextActions.append(action)

    def clearContextMenuActions(self):
        """Remove all context menu entries."""
        self._contextActions.clear()

    # ═══════════════════════════════════════════════════════
    # DOUBLE-CLICK CONFIGURATION
    # ═══════════════════════════════════════════════════════

    def setDoubleClickAction(self, action: str, nodeFilter=None):
        """
        Define what happens on double-click.

        Parameters
        ----------
        action      : str action name, or "toggle_expand" to expand/collapse.
        nodeFilter  : same rules as context menu nodeFilter (optional).

        Multiple rules can be added; first matching rule wins.
        """
        self._dblClickRules.append({"action": action, "nodeFilter": nodeFilter})

    def clearDoubleClickActions(self):
        """Remove all double-click rules."""
        self._dblClickRules.clear()

    # ═══════════════════════════════════════════════════════
    # DATA LOADING
    # ═══════════════════════════════════════════════════════

    def loadData(self, data: List[Dict[str, Any]]):
        """
        Load tree data from a list of dicts.

        The dicts are nested arbitrarily deep via the key specified by childrenKey
        (default: ``"children"``).

        Parameters
        ----------
        data : list of dicts, each representing a root node.

        Example::

            handler.loadData([
                {"id": 1, "name": "Engineering", "status": "active",
                 "children": [
                     {"id": 11, "name": "Hydraulic", "status": "active"},
                     {"id": 12, "name": "Control",   "status": "warning"},
                 ]},
            ])
        """
        self._roots = self._buildTree(data, parent=None, depth=0)
        self._model.resetData(self._roots)
        count = self._countNodes(self._roots)
        self.dataLoaded.emit(count)

    def clearData(self):
        """Remove all nodes from the tree."""
        self._roots = []
        self._model.resetData(self._roots)
        self.dataLoaded.emit(0)

    # ═══════════════════════════════════════════════════════
    # DATA ACCESS
    # ═══════════════════════════════════════════════════════

    def getData(self) -> List[Dict[str, Any]]:
        """Return raw data dicts for all root nodes (shallow, no children stripped)."""
        return [n.raw for n in self._roots]

    def getSelectedNode(self) -> Optional[Dict[str, Any]]:
        """Return the raw data dict of the currently selected node, or None."""
        node = self._currentNode()
        return node.raw if node else None

    def getSelectedDepth(self) -> int:
        """Return the depth of the currently selected node (-1 if nothing selected)."""
        node = self._currentNode()
        return node.depth if node else -1

    def getAllNodes(self, includeRaw: bool = True) -> List[Dict[str, Any]]:
        """
        Return a flat list of all node data dicts in depth-first order.

        Each dict is extended with ``_depth`` and ``_has_children`` keys for
        convenience (these are not part of the original data).
        """
        result: List[Dict[str, Any]] = []
        self._collectNodes(self._roots, result)
        return result

    # ═══════════════════════════════════════════════════════
    # VIEW OPERATIONS
    # ═══════════════════════════════════════════════════════

    def expandAll(self):
        """Expand all nodes."""
        self._treeView.expandAll()

    def collapseAll(self):
        """Collapse all nodes."""
        self._treeView.collapseAll()

    def expandNode(self, nodeData: Dict[str, Any]):
        """Expand a specific node identified by its raw data dict."""
        node = self._findNodeByRaw(nodeData)
        if node:
            idx = self._model.indexForNode(node)
            self._treeView.expand(idx)

    def collapseNode(self, nodeData: Dict[str, Any]):
        """Collapse a specific node identified by its raw data dict."""
        node = self._findNodeByRaw(nodeData)
        if node:
            idx = self._model.indexForNode(node)
            self._treeView.collapse(idx)

    def selectNode(self, nodeData: Dict[str, Any]):
        """Programmatically select a node by its raw data dict."""
        node = self._findNodeByRaw(nodeData)
        if node:
            idx = self._model.indexForNode(node)
            self._treeView.setCurrentIndex(idx)
            self._treeView.scrollTo(idx)

    def setIconSize(self, size: int):
        """Set the size (pixels) of node icons."""
        self._treeView.setIconSize(QSize(size, size))

    def setIndentation(self, pixels: int):
        """Set the indentation width per tree level."""
        self._treeView.setIndentation(pixels)

    # ═══════════════════════════════════════════════════════
    # CALLBACKS  (mirrors TableViewHandler API)
    # ═══════════════════════════════════════════════════════

    def onSelectionChanged(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback invoked when the selected node changes.

        Parameters
        ----------
        callback : fn(node_data: dict) -> None
            Receives the raw data dict of the newly selected node (empty dict if none).
        """
        self.selectionChanged.connect(callback)

    def onActionTriggered(self, action: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback for a named action (from context menu or double-click).

        Parameters
        ----------
        action   : str — the action name (e.g. "edit", "delete", "add_child").
        callback : fn(node_data: dict) -> None

        Multiple callbacks per action are supported.
        """
        self._actionCallbacks.setdefault(action, []).append(callback)

    def onDoubleClicked(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register a callback for any double-click event.

        Parameters
        ----------
        callback : fn(node_data: dict) -> None
        """
        self.doubleClicked.connect(callback)

    def onDataLoaded(self, callback: Callable[[int], None]):
        """
        Register a callback fired after loadData() completes.

        Parameters
        ----------
        callback : fn(total_node_count: int) -> None
        """
        self.dataLoaded.connect(callback)

    # ═══════════════════════════════════════════════════════
    # INTERNAL: slots
    # ═══════════════════════════════════════════════════════

    def _onSelectionChanged(self, current: QModelIndex, _prev: QModelIndex):
        if current.isValid():
            node: _TreeNode = current.internalPointer()
            self.selectionChanged.emit(node.raw)
        else:
            self.selectionChanged.emit({})

    def _onDoubleClicked(self, index: QModelIndex):
        if not index.isValid():
            return
        node: _TreeNode = index.internalPointer()

        # Find first matching double-click rule
        matched_action = None
        for rule in self._dblClickRules:
            if self._nodeMatchesFilter(node, rule.get("nodeFilter")):
                matched_action = rule["action"]
                break

        # Default behaviour when no rule matches
        if matched_action is None:
            if node.children:
                matched_action = "toggle_expand"
            else:
                matched_action = None

        if matched_action == "toggle_expand":
            idx = self._model.indexForNode(node)
            if self._treeView.isExpanded(idx):
                self._treeView.collapse(idx)
            else:
                self._treeView.expand(idx)
        elif matched_action:
            self._dispatchAction(matched_action, node)

        self.doubleClicked.emit(node.raw)

    def _onContextMenuRequested(self, pos: QPoint):
        index = self._treeView.indexAt(pos)
        if not index.isValid():
            return

        node: _TreeNode = index.internalPointer()

        # Build visible actions for this node
        visible = []
        for entry in self._contextActions:
            if entry.get("separator"):
                visible.append(entry)
                continue
            nf = entry.get("nodeFilter")
            if self._nodeMatchesFilter(node, nf):
                visible.append(entry)

        # Strip leading / trailing separators and double separators
        visible = self._cleanSeparators(visible)
        if not visible:
            return

        menu = QMenu(self._treeView)
        for entry in visible:
            if entry.get("separator"):
                menu.addSeparator()
                continue
            icon_name = entry.get("icon", "")
            # Load icon from Qt resources if icon name is recognized
            if icon_name and icon_name in _CONTEXT_MENU_ICON_MAP:
                icon = getIconFromResource(_CONTEXT_MENU_ICON_MAP[icon_name])
            else:
                icon = QIcon()
            act = QAction(
                icon,
                entry.get("label", entry.get("action", "?")),
                menu,
            )
            # Optional enabled state
            enabled_cfg = entry.get("enabled", True)
            if callable(enabled_cfg):
                act.setEnabled(bool(enabled_cfg(node.raw, node.depth)))
            else:
                act.setEnabled(bool(enabled_cfg))

            action_name = entry.get("action", "")
            act.triggered.connect(lambda checked=False, a=action_name, n=node: self._dispatchAction(a, n))
            menu.addAction(act)

        menu.exec(self._treeView.viewport().mapToGlobal(pos))

    # ═══════════════════════════════════════════════════════
    # INTERNAL: dispatch + built-in actions
    # ═══════════════════════════════════════════════════════

    def _dispatchAction(self, action: str, node: _TreeNode):
        # Built-in structural actions
        if action == "expand_all":
            idx = self._model.indexForNode(node)
            self._treeView.expandRecursively(idx)
        elif action == "collapse_all":
            idx = self._model.indexForNode(node)
            self._treeView.collapse(idx)
        elif action == "expand_node":
            idx = self._model.indexForNode(node)
            self._treeView.expand(idx)
        elif action == "toggle_expand":
            idx = self._model.indexForNode(node)
            if self._treeView.isExpanded(idx):
                self._treeView.collapse(idx)
            else:
                self._treeView.expand(idx)

        # Emit public signals
        self.actionTriggered.emit(action, node.raw)

        # Fire registered callbacks
        for cb in self._actionCallbacks.get(action, []):
            cb(node.raw)

    # ═══════════════════════════════════════════════════════
    # INTERNAL: helpers
    # ═══════════════════════════════════════════════════════

    def _buildTree(
        self,
        data: List[Dict[str, Any]],
        parent: Optional[_TreeNode],
        depth: int,
    ) -> List[_TreeNode]:
        nodes = []
        for raw in data:
            node = _TreeNode(raw=raw, depth=depth, parent=parent)
            children_raw = raw.get(self._childrenKey, [])
            node.children = self._buildTree(children_raw, parent=node, depth=depth + 1)
            nodes.append(node)
        return nodes

    def _countNodes(self, nodes: List[_TreeNode]) -> int:
        total = len(nodes)
        for n in nodes:
            total += self._countNodes(n.children)
        return total

    def _collectNodes(self, nodes: List[_TreeNode], result: List):
        for n in nodes:
            enriched = dict(n.raw)
            enriched["_depth"] = n.depth
            enriched["_has_children"] = bool(n.children)
            result.append(enriched)
            self._collectNodes(n.children, result)

    def _currentNode(self) -> Optional[_TreeNode]:
        idx = self._treeView.currentIndex()
        if idx.isValid():
            return idx.internalPointer()
        return None

    def _findNodeByRaw(self, raw: Dict[str, Any]) -> Optional[_TreeNode]:
        """Find a _TreeNode by identity of its raw dict."""
        return self._searchNodes(self._roots, raw)

    def _searchNodes(self, nodes: List[_TreeNode], raw: Dict) -> Optional[_TreeNode]:
        for n in nodes:
            if n.raw is raw:
                return n
            found = self._searchNodes(n.children, raw)
            if found:
                return found
        return None

    def _nodeMatchesFilter(self, node: _TreeNode, nodeFilter) -> bool:
        """Return True if the node passes the given filter."""
        if nodeFilter is None:
            return True
        if callable(nodeFilter):
            return bool(nodeFilter(node.raw, node.depth))
        if nodeFilter == "root":
            return node.depth == 0
        if nodeFilter == "non-root":
            return node.depth > 0
        if nodeFilter in ("parent",):
            return bool(node.children)
        if nodeFilter in ("child", "leaf"):
            return not node.children
        return True  # unknown filter string → show for all

    @staticmethod
    def _cleanSeparators(entries: List[Dict]) -> List[Dict]:
        """Remove leading, trailing, and consecutive separators."""
        result = []
        for e in entries:
            if e.get("separator"):
                if result and not result[-1].get("separator"):
                    result.append(e)
            else:
                result.append(e)
        while result and result[-1].get("separator"):
            result.pop()
        return result
