import json
import os
from PySide6.QtCore import QTemporaryDir, QTemporaryFile

class TemporaryHandler:
    _instance = None  # This will hold the singleton instance

    def __new__(cls, base_dir="temp"):
        # Implementing Singleton behavior
        if cls._instance is None:
            # Only create the instance if it doesn't exist
            cls._instance = super(TemporaryHandler, cls).__new__(cls)
            cls._instance._initialized = False  # Ensure base_dir is set only once
            cls._instance.baseDir = base_dir
        return cls._instance

    def __init__(self, base_dir="temp"):
        """Initialize the TemporaryHandler"""
        if not self._initialized:
            # Set up base_dir only once during the first run
            self.setBaseDir(base_dir)
            self._initialized = True

    def setBaseDir(self, base_dir):
        """Set the base directory for temporary files."""
        self.baseDir = os.path.join(os.getcwd(), base_dir)
        if not os.path.exists(self.baseDir):
            os.makedirs(self.baseDir)

        # Create a QTemporaryDir instance
        self.tempDir = QTemporaryDir(os.path.join(self.baseDir, "XXXXXX"))

        if self.tempDir.isValid():
            print(f"Temporary directory created at: {self.tempDir.path()}")
        else:
            raise Exception("Failed to create temporary directory")

    def createTempFile(self, filename="temp_file_", ext="txt", data=b"Some temporary data"):
        """Create a temporary file inside the temporary directory and write data."""
        tempFile = QTemporaryFile(os.path.join(self.tempDir.path(), f"{filename}XXXXXX.{ext}"))
        tempFile.setAutoRemove(False)

        # Open the file and write the given data
        if tempFile.open():
            tempFile.write(data)
            print(f"Temporary file created at: {tempFile.fileName()}")
            tempFile.close()
            return tempFile.fileName()
        else:
            raise Exception("Failed to create temporary file")
        
    def createTempJsonFile(self,filename="temp_file_", data=None):
        """Create a temporary file inside the temporary directory and write JSON data."""
        # If data is not passed, use default empty dictionary
        if data is None:
            data = {"message": "Some temporary data"}

        # Serialize the data to JSON
        json_data = json.dumps(data)

        # Create the temporary file
        tempFile = QTemporaryFile(os.path.join(self.tempDir.path(), f"{filename}XXXXXX.json"))
        tempFile.setAutoRemove(False)

        # Open the file and write the serialized JSON data
        if tempFile.open():
            tempFile.write(json_data.encode('utf-8'))  # Write the encoded JSON data (as bytes)
            print(f"Temporary JSON file created at: {tempFile.fileName()}")
            tempFile.close()
            return tempFile.fileName()
        else:
            raise Exception("Failed to create temporary file")

    def getTempDirectory(self):
        """Returns the path of the temporary directory."""
        return self.tempDir.path()

    def readFileContent(self, filePath):
        """Read the content of the file and return it."""
        try:
            with open(filePath, 'rb') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def cleanup(self):
        """Cleans up by deleting the temporary directory and its contents."""
        # QTemporaryDir automatically deletes the temp directory when it goes out of scope
        self.tempDir.remove()