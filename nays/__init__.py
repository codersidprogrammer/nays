"""
Nays Framework - A NestJS-like Python modular framework with PySide6 UI support.

Provides:
- Module system with dependency injection
- Router for view navigation
- Lifecycle management (OnInit, OnDestroy)
- Service providers
- PySide6 UI components and views
"""

__version__ = "1.0.0"
__author__ = "Nays Contributors"

from nays.core.module import NaysModule, NaysModuleBase, ModuleMetadata, Provider, ModuleFactory
from nays.core.route import Route, RouteType
from nays.core.router import Router
from nays.core.lifecycle import OnInit, OnDestroy
from nays.core.logger import setupLogger
from nays.service.logger_service import LoggerService, LoggerServiceImpl
from nays.ui.base_view import BaseView
from nays.ui.base_dialog import BaseDialogView
from nays.ui.base_window import BaseWindowView
from nays.ui.base_widget import BaseWidgetView

__all__ = [
    # Core
    'NaysModule',
    'NaysModuleBase',
    'ModuleMetadata',
    'Provider',
    'ModuleFactory',
    'Route',
    'RouteType',
    'Router',
    'OnInit',
    'OnDestroy',
    'setupLogger',
    # Services
    'LoggerService',
    'LoggerServiceImpl',
    # UI
    'BaseView',
    'BaseDialogView',
    'BaseWindowView',
    'BaseWidgetView',
]
