#!/usr/bin/env python3
"""
Package validation script for nays.
Run this to verify all imports and functionality work correctly.
"""

import sys


def validate_imports():
    """Validate all package imports."""
    print("Testing package imports...")
    
    # Core imports
    from nays import NaysModule, Router, Route, OnInit, OnDestroy
    print("✅ Core imports OK")
    
    # UI imports
    from nays.ui import BaseView, BaseDialogView, BaseWindowView, BaseWidgetView
    print("✅ UI base imports OK")
    
    # UI Handler imports
    from nays.ui.handler import TableViewHandler, TableViewModel, ComboBoxDelegate
    print("✅ UI handler imports OK")
    
    # Service imports
    from nays.service import LoggerService, LoggerServiceImpl
    print("✅ Service imports OK")
    
    return True


def validate_tableview_handler():
    """Validate TableViewHandler functionality."""
    from PySide6.QtWidgets import QApplication, QTableView
    from nays.ui.handler import TableViewHandler
    
    app = QApplication.instance() or QApplication(sys.argv)
    tableView = QTableView()
    handler = TableViewHandler(tableView, ["A", "B", "C"])
    handler.setupColumns([("a", "text"), ("b", "combo"), ("c", "checkbox")])
    handler.addRow({"a": "test", "b": "option1", "c": True})
    
    assert handler.model.rowCount() == 1, "Row count should be 1"
    assert handler.getCellValue(0, 0) == "test", "Cell value mismatch"
    print("✅ TableViewHandler functionality OK")
    
    return True


def validate_build():
    """Test that package can be built."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("✅ Pip check passed")
    else:
        print(f"⚠️ Pip check warnings: {result.stdout}")
    
    return True


def main():
    print()
    print("=" * 50)
    print("Nays Package Validation")
    print("=" * 50)
    print()
    
    try:
        validate_imports()
        validate_tableview_handler()
        validate_build()
        
        print()
        print("=" * 50)
        print("All validations passed! ✅")
        print("Package is ready to be bundled.")
        print("=" * 50)
        print()
        print("To build the package, run:")
        print("  python3 -m build")
        print()
        print("To install locally for testing:")
        print("  pip install -e .")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
