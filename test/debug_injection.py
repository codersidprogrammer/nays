#!/usr/bin/env python3
"""Debug router injection"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from injector import Injector
from nays.core.router import Router
from nays import ModuleFactory

class TestClass:
    def __init__(self, router: Router = None):
        self.router = router

# Create an injector
injector = Injector()

# Create a mock router
mock_router = object()

# Try to bind Router
from injector import Binder
def configure(binder):
    binder.bind(Router, to=mock_router)

injector = Injector([configure])

# Try to create object
try:
    obj = injector.create_object(TestClass)
    print(f"Router injected: {obj.router is not None}")
    print(f"Is it mock_router: {obj.router is mock_router}")
except Exception as e:
    print(f"Error: {e}")
