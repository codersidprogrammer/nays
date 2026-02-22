import os
import shutil


def createFolderIfNotExist(base_path: str, folder_name: str):
    path = os.path.join(base_path, folder_name)
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Folder created at: {path}")
    else:
        print(f"ℹ️ Folder already exists at: {path}")


def copyFile(src_path: str, dest_path: str) -> None:
    """
    Copy a file from src_path to dest_path.

    Args:
        src_path (str): The source file path.
        dest_path (str): The destination file path or directory.

    Raises:
        FileNotFoundError: If the source file doesn't exist.
        IOError: If the copy operation fails.
    """
    if not os.path.isfile(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")

    try:
        shutil.copy(src_path, dest_path)
        print(f"File copied from {src_path} to {dest_path}")
    except IOError as e:
        raise IOError(f"Failed to copy file: {e}")


# def scanFilesWithExtensions(directory, extensions):
#     matched_files = []

#     # Walk through all files in the directory and subdirectories
#     for root, _, files in os.walk(directory):
#         for file in files:
#             # Check if the file has one of the specified extensions
#             if any(file.endswith(ext) for ext in extensions):
#                 matched_files.append(file)  # Only append the file name, not the full path

#     return matched_files


def scanFilesWithExtensions(directory, extensions):
    matched_files = []

    # List only files in the specific directory (no subdirectories)
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)

        # Ensure the path is a file and check if it has one of the specified extensions
        if os.path.isfile(file_path) and any(file.endswith(ext) for ext in extensions):
            matched_files.append(file)  # Only append the file name, not the full path

    return matched_files
