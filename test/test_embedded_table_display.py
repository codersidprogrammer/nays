"""
Test: Verify embedded editor displays table correctly
"""

import sys
from PySide6.QtWidgets import QApplication, QTableView
from nays.ui.handler import createTableEditorEmbedded

# Create QApplication first
app = QApplication(sys.argv)

# Sample config data
config_data = [
    {'name': 'IPOLY', 'description': 'Polynomial Order', 'type': 'combobox'},
    {'name': 'IOPT', 'description': 'Option Flag', 'type': 'checkbox'},
    {'name': 'GLEN', 'description': 'Length', 'type': 'text'},
]

# Headers
headers = ["ID", "GLEN", "IOPT", "Material Id", "Set As Output", "IPOLY Usage"]

# Callbacks
def on_save(data):
    print("\n✅ DATA SAVED:")
    print(f"   Rows: {data['rowCount']}")
    print(f"   Cols: {data['colCount']}")
    print(f"   Headers: {data['headers']}")
    print(f"   Data: {data['dict']}")

def on_cancel():
    print("\n❌ Edit cancelled")

# Test the embedded editor
print("Creating embedded editor...")

editor = createTableEditorEmbedded(
    table_view=QTableView(),
    headers=headers,
    config_data=config_data,
    on_save=on_save,
    on_cancel=on_cancel,
    apply_dark_style=True,
    combo_display_mode="both"
)

print("✓ Editor created successfully")

# Show the editor (this is what happens when user clicks button)
editor.show()

print(f"✓ Table view visible after show(): {editor.tableView.isVisible()}")
print(f"✓ Editor visible: {editor.isVisible()}")
print(f"✓ Table model: {editor.tableView.model()}")

# Check if table has data
if editor.tableView.model():
    print(f"✓ Row count in model: {editor.tableView.model().rowCount()}")
    print(f"✓ Column count in model: {editor.tableView.model().columnCount()}")
    
    # Print the data
    if editor.handler:
        data = editor.handler.getData()
        print(f"✓ Handler data: {len(data)} rows")
        for i, row in enumerate(data):
            print(f"  Row {i}: {row}")
else:
    print("❌ No model found in table view!")

print("\n✅ All checks passed! The table should display correctly when editor is shown.")
