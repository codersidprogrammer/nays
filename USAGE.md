# Using Nays Framework in Your Project

## Installation

### From GitHub (Development)
```bash
git clone https://github.com/dimaseditiya/nays.git
cd nays
pip install -e .
```

### From PyPI (When Published)
```bash
pip install nays
```

## Basic Usage

### 1. Define Services

```python
from abc import ABC, abstractmethod

class MyService(ABC):
    @abstractmethod
    def do_something(self):
        pass

class MyServiceImpl(MyService):
    def do_something(self):
        return "Done!"
```

### 2. Create Views

```python
from nays import BaseDialogView, Router

class MyView(BaseDialogView):
    def __init__(self, routeData: dict = {}, router: 'Router' = None):
        super().__init__(routeData=routeData)
        self.router = router
        self.setWindowTitle("My View")
```

### 3. Define Routes

```python
from nays import Route, RouteType

routes = [
    Route(path="/home", component=HomeView, routeType=RouteType.WINDOW),
    Route(path="/dialog", component=MyView, routeType=RouteType.DIALOG),
]
```

### 4. Create Module

```python
from nays import NaysModule, Provider

@NaysModule(
    providers=[
        Provider(MyService, useClass=MyServiceImpl),
    ],
    routes=routes,
)
class MyModule:
    pass
```

### 5. Bootstrap Application

```python
from PySide6.QtWidgets import QApplication
from nays import ModuleFactory, Router

app = QApplication([])
factory = ModuleFactory()
factory.register(MyModule)
factory.initialize()

router = Router(factory.injector)
router.registerRoutes(factory.getRoutes())

# Navigate to initial route
router.navigate('/home')

app.exec()
```

## Advanced Features

### Dependency Injection

Services are automatically injected into components:

```python
@NaysModule(
    providers=[
        Provider(DatabaseService, useClass=DatabaseServiceImpl),
        Provider(UserService, useClass=UserServiceImpl),
    ],
)
class DataModule:
    pass
```

### Lifecycle Hooks

Components can implement lifecycle methods:

```python
from nays import OnInit, OnDestroy

class MyComponent(OnInit, OnDestroy):
    def onInit(self):
        print("Component initialized")
    
    def onDestroy(self):
        print("Component destroyed")
```

### Router Navigation with Parameters

```python
class MyView(BaseDialogView):
    def navigate_to_next(self):
        self.router.navigate('/next-page', {
            'userId': 123,
            'userName': 'John'
        })
```

## Project Structure

```
my_project/
├── services/
│   ├── user_service.py
│   └── data_service.py
├── views/
│   ├── home_view.py
│   ├── user_view.py
│   └── settings_view.py
├── modules/
│   ├── user_module.py
│   └── data_module.py
├── main.py
└── requirements.txt
```

## Examples

See the `test/` directory in the Nays repository for complete working examples:
- `test_nays_module.py` - Module system
- `test_router_navigation_with_params.py` - Router navigation
- `test_lifecycle_routes.py` - Lifecycle management
- `test_ui_dialog_usage.py` - UI components
- `test_ui_master_material_usage.py` - Material views example

## Testing

```python
import unittest
from nays import NaysModule, Provider, ModuleFactory, Router

class TestMyModule(unittest.TestCase):
    def setUp(self):
        self.factory = ModuleFactory()
        self.factory.register(MyModule)
        self.factory.initialize()
        self.router = Router(self.factory.injector)
        self.router.registerRoutes(self.factory.getRoutes())
    
    def test_navigation(self):
        self.router.navigate('/home')
        # Assert view created
```

## Documentation

- [Module System](docs/modules.md)
- [Router & Navigation](docs/router.md)
- [Dependency Injection](docs/di.md)
- [Lifecycle Management](docs/lifecycle.md)
- [UI Components](docs/ui.md)
