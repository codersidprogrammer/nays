import os


def createBatFile(filename: str, commands: list[str], working_dir: str = None):
    """
    Create a .bat file with the given filename and list of command strings.

    Args:
        filename (str): The name (or full path) of the .bat file to create.
        commands (list[str]): List of command lines to include in the .bat file.
        working_dir (str, optional): Directory to place the .bat file in. Defaults to current dir.
    """
    if not filename.endswith(".bat"):
        filename += ".bat"

    path = os.path.join(working_dir, filename) if working_dir else filename

    with open(path, "w") as f:
        for cmd in commands:
            f.write(f"{cmd}\n")

    print(f".bat file created at: {path}")


import subprocess


def executeBatFile(bat_file_path):
    try:
        subprocess.run([bat_file_path], check=True, shell=True)
        print(f"Successfully executed: {bat_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while executing {bat_file_path}: {e}")
