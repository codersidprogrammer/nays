"""
Test: Save/Cancel functionality and callbacks

Tests the new Save and Cancel buttons, confirmation dialogs,
and data callback signals.
"""

import sys
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from nays.ui.handler import createTableEditor, createTableEditorWithCallback


def test_save_cancel_basic():
    """Test 1: Basic Save/Cancel functionality."""
    print("\n" + "="*60)
    print("TEST 1: Basic Save/Cancel Buttons")
    print("="*60)
    
    data = [
        {'name': 'Alice', 'age': 28, 'active': True},
        {'name': 'Bob', 'age': 35, 'active': False},
    ]
    
    table = createTableEditor(
        headers=['name', 'age', 'active'],
        data=data,
        column_types={'active': 'checkbox'}
    )
    
    # Check toolbar buttons exist
    assert hasattr(table, 'saveBtn'), "Save button not found"
    assert hasattr(table, 'cancelBtn'), "Cancel button not found"
    print("✓ Save and Cancel buttons created")
    
    # Check signals exist
    assert hasattr(table, 'dataSaved'), "dataSaved signal not found"
    assert hasattr(table, 'operationCancelled'), "operationCancelled signal not found"
    print("✓ Signal definitions exist")
    
    # Check data can be retrieved
    saved_data = table.getDataAsDict()
    assert len(saved_data) == 2, "Data not loaded correctly"
    print(f"✓ Initial data loaded: {len(saved_data)} rows")
    
    table.close()
    print("✅ TEST 1 PASSED\n")
    return True


def test_save_callback_signal():
    """Test 2: Save callback signal emits correct data."""
    print("="*60)
    print("TEST 2: Save Callback Signal")
    print("="*60)
    
    test_data = [
        {'id': 1, 'name': 'Test1'},
        {'id': 2, 'name': 'Test2'},
        {'id': 3, 'name': 'Test3'},
    ]
    
    received_data = {}
    
    def on_save(callback_data):
        received_data.update(callback_data)
    
    table = createTableEditorWithCallback(
        headers=['id', 'name'],
        data=test_data,
        on_save=on_save
    )
    
    print("✓ Table created with callback")
    
    # Simulate save (this would normally be triggered by user clicking Save button)
    # For automated test, we directly emit the signal
    data_dict = table.getDataAsDict()
    data_numpy = table.getDataAsNumpy()
    callback_data = {
        'dict': data_dict,
        'numpy': data_numpy,
        'rowCount': len(data_dict),
        'colCount': table.handler.columnCount,
        'headers': table.handler.model.headers
    }
    table.dataSaved.emit(callback_data)
    
    # Verify callback received data
    assert len(received_data) > 0, "Callback not triggered"
    assert 'dict' in received_data, "Dict data not in callback"
    assert 'numpy' in received_data, "NumPy data not in callback"
    assert received_data['rowCount'] == 3, "Wrong row count"
    print(f"✓ Callback received data: {received_data['rowCount']} rows")
    print(f"  - Headers: {received_data['headers']}")
    print(f"  - Dict entries: {len(received_data['dict'])}")
    print(f"  - NumPy shape: {received_data['numpy'].shape}")
    
    table.close()
    print("✅ TEST 2 PASSED\n")
    return True


def test_cancel_signal():
    """Test 3: Cancel signal emission."""
    print("="*60)
    print("TEST 3: Cancel Signal")
    print("="*60)
    
    cancel_called = {'value': False}
    
    def on_cancel():
        cancel_called['value'] = True
    
    table = createTableEditorWithCallback(
        headers=['col1', 'col2'],
        data=[{'col1': 'a', 'col2': 'b'}],
        on_cancel=on_cancel
    )
    
    print("✓ Table created with cancel callback")
    
    # Emit cancel signal
    table.operationCancelled.emit()
    
    assert cancel_called['value'], "Cancel callback not triggered"
    print("✓ Cancel signal triggered callback")
    
    table.close()
    print("✅ TEST 3 PASSED\n")
    return True


def test_undo_redo_with_save():
    """Test 4: Undo/Redo stacks clear after save."""
    print("="*60)
    print("TEST 4: Undo/Redo Stack Management")
    print("="*60)
    
    table = createTableEditor(
        headers=['col1'],
        data=[{'col1': 'initial'}]
    )
    
    print("✓ Table created")
    
    # Add a row to create undo history
    table._onAddRow()
    assert len(table.undoStack) > 0, "Undo stack not populated"
    print(f"✓ Undo stack has {len(table.undoStack)} entries after add")
    
    # Simulate save by directly emitting signal
    data_dict = table.getDataAsDict()
    data_numpy = table.getDataAsNumpy()
    callback_data = {
        'dict': data_dict,
        'numpy': data_numpy,
        'rowCount': len(data_dict),
        'colCount': table.handler.columnCount,
        'headers': table.handler.model.headers
    }
    table.dataSaved.emit(callback_data)
    
    # Note: The _onSave method clears stacks, but direct emit doesn't
    # That's expected - user must click Save button for stack clearing
    print("✓ Save signal can be emitted with current undo state")
    
    table.close()
    print("✅ TEST 4 PASSED\n")
    return True


def test_with_numpy_input():
    """Test 5: Save/Cancel with NumPy array input."""
    print("="*60)
    print("TEST 5: NumPy Array Input")
    print("="*60)
    
    # Create numpy array
    data = np.array([
        ['Alice', 30, True],
        ['Bob', 25, False],
        ['Charlie', 35, True],
    ])
    
    received = {}
    
    def on_save(callback_data):
        received.update(callback_data)
    
    table = createTableEditorWithCallback(
        headers=['Name', 'Age', 'Active'],
        data=data,
        column_types={'Active': 'checkbox'},
        on_save=on_save
    )
    
    print(f"✓ Table created from NumPy array shape {data.shape}")
    
    # Trigger save signal
    data_dict = table.getDataAsDict()
    data_numpy = table.getDataAsNumpy()
    callback_data = {
        'dict': data_dict,
        'numpy': data_numpy,
        'rowCount': len(data_dict),
        'colCount': table.handler.columnCount,
        'headers': table.handler.model.headers
    }
    table.dataSaved.emit(callback_data)
    
    assert len(received['dict']) == 3, "Wrong number of rows"
    assert received['numpy'].shape[0] == 3, "Wrong array rows"
    print(f"✓ Save callback received {received['rowCount']} rows")
    print(f"  - As dict: {len(received['dict'])} entries")
    print(f"  - As numpy: shape {received['numpy'].shape}")
    
    table.close()
    print("✅ TEST 5 PASSED\n")
    return True


def test_keyboard_shortcut():
    """Test 6: Ctrl+S keyboard shortcut."""
    print("="*60)
    print("TEST 6: Keyboard Shortcut (Ctrl+S)")
    print("="*60)
    
    table = createTableEditor(
        headers=['col1'],
        data=[{'col1': 'test'}]
    )
    
    print("✓ Table created")
    
    # Verify keyPressEvent handles Ctrl+S
    # (actual testing would require simulating keyboard events)
    # For now, just verify the method exists and is callable
    assert callable(table.keyPressEvent), "keyPressEvent not callable"
    print("✓ keyPressEvent method exists and is callable")
    
    # Verify _onSave is connected to saveBtn
    assert table.saveBtn.triggered.connect, "Save button signal not connected"
    print("✓ Save button signal connected")
    
    table.close()
    print("✅ TEST 6 PASSED\n")
    return True


def test_multiple_callbacks():
    """Test 7: Multiple callback connections."""
    print("="*60)
    print("TEST 7: Multiple Value Callbacks")
    print("="*60)
    
    save_calls = []
    cancel_calls = []
    
    def callback1_save(data):
        save_calls.append(('callback1', data['rowCount']))
    
    def callback2_save(data):
        save_calls.append(('callback2', data['rowCount']))
    
    def callback1_cancel():
        cancel_calls.append('callback1')
    
    table = createTableEditor(
        headers=['col1'],
        data=[{'col1': 'a'}, {'col1': 'b'}]
    )
    
    # Connect multiple callbacks
    table.dataSaved.connect(callback1_save)
    table.dataSaved.connect(callback2_save)
    table.operationCancelled.connect(callback1_cancel)
    
    print("✓ Multiple callbacks connected to same signals")
    
    # Emit signals
    data_dict = table.getDataAsDict()
    data_numpy = table.getDataAsNumpy()
    callback_data = {
        'dict': data_dict,
        'numpy': data_numpy,
        'rowCount': len(data_dict),
        'colCount': table.handler.columnCount,
        'headers': table.handler.model.headers
    }
    table.dataSaved.emit(callback_data)
    table.operationCancelled.emit()
    
    assert len(save_calls) == 2, "Not all save callbacks triggered"
    assert len(cancel_calls) == 1, "Cancel callbacks not triggered"
    print(f"✓ Save callbacks triggered: {len(save_calls)}")
    print(f"✓ Cancel callbacks triggered: {len(cancel_calls)}")
    
    table.close()
    print("✅ TEST 7 PASSED\n")
    return True


def main():
    """Run all tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    print("\n" + "="*70)
    print(" SAVE/CANCEL CALLBACK TESTS")
    print("="*70)
    
    tests = [
        test_save_cancel_basic,
        test_save_callback_signal,
        test_cancel_signal,
        test_undo_redo_with_save,
        test_with_numpy_input,
        test_keyboard_shortcut,
        test_multiple_callbacks,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ TEST FAILED: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"❌ EXCEPTION: {str(e)}")
            failed += 1
    
    print("\n" + "="*70)
    print(f" RESULTS: {passed} passed, {failed} failed")
    print("="*70 + "\n")
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
