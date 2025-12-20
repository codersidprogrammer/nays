# Nays Framework

A NestJS-like Python modular framework with PySide6 UI support, dependency injection, and router-based navigation.

## Features

- **Modular Architecture**: Build applications with `@NaysModule` decorator
- **Dependency Injection**: Built-in service providers and automatic dependency resolution
- **Router**: Navigate between views with lifecycle management
- **Lifecycle Hooks**: `OnInit` and `OnDestroy` for component lifecycle management
- **PySide6 Integration**: Ready-to-use UI components and dialogs
- **Type-safe**: Full type annotations support

## Installation

```bash
pip install nays
```

Or for development:

```bash
git clone https://github.com/dimaseditiya/nays.git
cd nays
pip install -e .
```

## Quick Start

### Creating a Module

```python
from nays import NaysModule, Provider

@NaysModule(
    providers=[
        Provider(MyService, useClass=MyServiceImpl),
    ],
    routes=[...],
)
class MyModule:
    pass
```

### Using Router Navigation

```python
from nays import BaseDialogView, Router

class MyView(BaseDialogView):
    def __init__(self, routeData: dict = {}, router: 'Router' = None):
        super().__init__(routeData=routeData)
        self.router = router
    
    def navigate_to_next(self):
        if self.router:
            self.router.navigate('/next-route', {'data': 'value'})
```

### Lifecycle Management

```python
from nays import OnInit, OnDestroy

class MyComponent(OnInit, OnDestroy):
    def onInit(self):
        print("Component initialized")
    
    def onDestroy(self):
        print("Component destroyed")
```

## Documentation

- [Module System](docs/modules.md)
- [Router & Navigation](docs/router.md)
- [Dependency Injection](docs/di.md)
- [UI Components](docs/ui.md)

## Examples

See the [test/](test/) directory for comprehensive examples.

## Testing

Run the test suite:

```bash
python -m pytest test/
```

Or using unittest:

```bash
python test/test_nays_module.py
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
