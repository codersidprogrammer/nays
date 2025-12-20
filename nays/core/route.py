
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Type

from nays.ui.base_view import BaseView

class RouteType(Enum):
    WINDOW = 'window'
    DIALOG = 'dialog'
    WIDGET = 'widget'


@dataclass
class Route:
    """
    Represents a route that links to a component (view).
    Routes are defined at the module level.
    """
    name: str = ''
    path: str = ''
    component: Type[BaseView] = None
    routeType: RouteType = field(default=RouteType.WINDOW)