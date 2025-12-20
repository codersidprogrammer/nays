# Nays Framework - Package Structure

## Directory Layout

```
nays/                                 # Root directory
├── nays/                            # Main package directory
│   ├── __init__.py                  # Public API exports
│   ├── core/                        # Core framework
│   │   ├── __init__.py
│   │   ├── module.py                # @NaysModule decorator
│   │   ├── route.py                 # Route definitions
│   │   ├── router.py                # Application router
│   │   ├── lifecycle.py             # OnInit, OnDestroy
│   │   ├── logger.py                # Logger utilities
│   │   └── initializer.py           # YAML initializer
│   ├── ui/                          # UI components
│   │   ├── __init__.py
│   │   ├── base_view.py             # Base view
│   │   ├── base_dialog.py           # Dialog view
│   │   ├── base_window.py           # Window view
│   │   ├── base_widget.py           # Widget view
│   │   ├── based_tabular_model.py   # Table model
│   │   ├── handler/                 # UI handlers
│   │   │   ├── data_table_handler.py
│   │   │   ├── component_handler.py
│   │   │   ├── tab_handler.py
│   │   │   └── ...
│   │   ├── decorator/               # UI decorators
│   │   │   ├── onsignal_decorator.py
│   │   │   ├── file_dialog.py
│   │   │   └── ...
│   │   └── helper/                  # UI helpers
│   │       ├── icon_helper.py
│   │       ├── message_box_helper.py
│   │       └── ...
│   └── service/                     # Services
│       ├── __init__.py
│       └── logger_service.py
│
├── core/                            # Legacy - for backward compatibility
│   ├── __init__.py (auto-generated)
│   ├── module.py
│   ├── route.py
│   ├── router.py
│   ├── lifecycle.py
│   ├── logger.py
│   └── initializer.py
│
├── ui/                              # Legacy - for backward compatibility
│   ├── __init__.py (auto-generated)
│   ├── base_view.py
│   ├── base_dialog.py
│   ├── base_window.py
│   ├── base_widget.py
│   ├── based_tabular_model.py
│   ├── handler/
│   ├── decorator/
│   └── helper/
│
├── service/                         # Legacy - for backward compatibility
│   ├── __init__.py (auto-generated)
│   └── logger_service.py
│
├── test/                            # Test suite (161 tests)
│   ├── test_nays_module.py          # 13 tests
│   ├── test_nays_module_providers.py # 16 tests
│   ├── test_nays_module_routes.py   # 15 tests
│   ├── test_lifecycle_routes.py     # 12 tests
│   ├── test_logger_injection.py     # 14 tests
│   ├── test_module_scenario.py      # 12 tests
│   ├── test_router_navigation_with_params.py # 26 tests
│   ├── test_ui_dialog_usage.py      # 25 tests
│   ├── test_ui_master_material_usage.py # 28 tests
│   ├── test_button_navigation.py
│   ├── ui_master_material_views.py
│   ├── ui_dialog_views.py
│   └── ...
│
├── setup.py                         # setuptools configuration
├── pyproject.toml                   # PEP 518 build config
├── MANIFEST.in                      # Package manifest
├── requirements.txt                 # Dependencies
├── requirements-dev.txt             # Dev dependencies
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT License
├── README.md                        # Package documentation
├── USAGE.md                         # Usage guide
├── PACKAGING_SUMMARY.md             # This setup summary
└── PACKAGE_STRUCTURE.md             # This file
```

## Package Files

### Core Package (`nays/`)

The main package that gets installed. Contains:
- `nays/__init__.py` - Exports public API
- `nays/core/` - Core framework modules
- `nays/ui/` - UI components
- `nays/service/` - Service utilities

### Configuration Files

- **setup.py** - setuptools configuration for package installation
- **pyproject.toml** - Modern Python packaging (PEP 518)
- **MANIFEST.in** - Specifies additional files to include in distribution
- **requirements.txt** - Runtime dependencies
- **requirements-dev.txt** - Development and testing dependencies

### Documentation

- **README.md** - Package overview and features
- **USAGE.md** - How to use the package
- **PACKAGING_SUMMARY.md** - Summary of packaging setup
- **PACKAGE_STRUCTURE.md** - This file

### Test Suite

- **test/** - 161 comprehensive tests covering all features
- All tests pass ✓

## Installation

### From Development Source
```bash
cd nays
pip install -e .
```

### From Package Distribution
```bash
pip install nays
```

## Using the Package

### Standard Import Style (Recommended)
```python
from nays import NaysModule, Provider, Router, ModuleFactory
from nays import Route, RouteType
from nays import OnInit, OnDestroy
from nays import BaseDialogView, BaseWindowView
```

### Legacy Import Style (Still Supported)
```python
# Old style still works due to core/, ui/, service/ directories
from core.module import NaysModule
from core.router import Router
from ui.base_dialog import BaseDialogView
```

## Key Exported Classes

### Core Framework
- `NaysModule` - Module decorator
- `Provider` - Service provider
- `ModuleFactory` - Creates and manages modules
- `Router` - Application router for navigation
- `Route` - Route definition
- `RouteType` - Enum: WINDOW, DIALOG, WIDGET
- `OnInit` - Lifecycle init interface
- `OnDestroy` - Lifecycle destroy interface
- `setupLogger` - Logger setup utility

### UI Components
- `BaseView` - Base class for all views
- `BaseDialogView` - Dialog view component
- `BaseWindowView` - Main window component
- `BaseWidgetView` - Widget component

## File Statistics

- **Total Python Files**: 50+
- **Total Tests**: 161
- **Test Files**: 9
- **Lines of Code**: ~5000+
- **Test Coverage**: Comprehensive

## Dependencies

### Runtime
- `injector` - Dependency injection
- `pyside6` - UI framework
- `python-dotenv` - Environment management
- `colorama` - Colored output

### Optional
- `numpy` - Scientific computing
- `pyyaml` - YAML support
- `pyinstaller` - Executable bundling

### Development
- `pytest` - Testing framework
- `coverage` - Code coverage
- `black` - Code formatting
- `flake8` - Linting
- `mypy` - Type checking

## Next Steps

1. **Install the package**: `pip install -e .`
2. **Review examples**: Check `test/` directory
3. **Read documentation**: See `USAGE.md`
4. **Build distribution**: `python -m build`
5. **Publish**: `twine upload dist/*` (when ready)

## Support

For issues, questions, or contributions:
- Check the test suite for examples
- Review USAGE.md for common patterns
- See PACKAGING_SUMMARY.md for setup details
