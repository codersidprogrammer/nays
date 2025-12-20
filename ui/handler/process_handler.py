from collections import deque
from PySide6.QtCore import QObject, QThread, Signal, Slot, QProcess

class ProcessHandler(QObject):
    output_ready = Signal(str)
    error_ready = Signal(str)
    finished = Signal(int)

    def __init__(self, parent=None, workingDir: str = None):
        super().__init__(parent)
        self.thread = QThread()
        self.process = QProcess()
        self.process.moveToThread(self.thread)

        self.process.readyReadStandardOutput.connect(self.handleStdout)
        self.process.readyReadStandardError.connect(self.handleStderr)
        self.process.finished.connect(self.handleFinished)

        self.thread.started.connect(self.startProcess)
        self._commands = deque()  # Command queue
        if workingDir:
            self.process.setWorkingDirectory(workingDir)
            
    def setWorkingDirectory(self, path: str):
        self.process.setWorkingDirectory(path)

    def start(self, command: list[str]):
        self._commands.clear()
        self._commands.append(command)
        self.thread.start()

    def chain(self, command: list[str]):
        """Add a command to be run after the current one finishes."""
        self._commands.append(command)

    @Slot()
    def startProcess(self):
        if not self._commands:
            self.thread.quit()
            return
        current_cmd = self._commands[0]
        self.process.start(current_cmd[0], current_cmd[1:])

    def stop(self):
        if self.process.state() != QProcess.NotRunning:
            self.process.terminate()
            if not self.process.waitForFinished(3000):
                self.process.kill()
        self._commands.clear()
    
    def write_input(self, text: str):
        """Write input to the running process (for interactive processes)"""
        if self.process.state() == QProcess.Running:
            self.process.write(text.encode())
            self.process.waitForBytesWritten()

    @Slot()
    def handleStdout(self):
        text = self.process.readAllStandardOutput().data().decode()
        self.output_ready.emit(text)

    @Slot()
    def handleStderr(self):
        text = self.process.readAllStandardError().data().decode()
        self.error_ready.emit(text)

    @Slot(int, QProcess.ExitStatus)
    def handleFinished(self, exit_code, exit_status):
        self.finished.emit(exit_code)
        self._commands.popleft()  # Remove the finished command

        if self._commands:
            self.startProcess()  # Start next command without restarting thread
        else:
            self.thread.quit()
            self.thread.wait()
