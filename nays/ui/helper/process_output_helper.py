"""
A comprehensive subwindow helper for displaying and monitoring process output in real-time within PySide6 applications.

This module provides three main integration approaches:
1. ProcessOutputCapture: Generic function output capture using stdout/stderr redirection
2. Charm3DProcessOutputCapture: Integration with existing Charm3DLineProcess ProcessHandler signals
3. WamitProcessOutputCapture: Integration with ProcessHandler for WAMIT process execution

The Charm3D integration preserves existing functionality while adding real-time GUI display:
- Maintains original outputHandler, errorHandler, and finishedHandler functionality
- Connects to existing processHandler.output_ready, error_ready, and finished signals  
- Provides seamless real-time output display in dedicated subwindows
- Requires no changes to existing Charm3DLineProcess code

The WAMIT integration connects directly to ProcessHandler signals for clean process execution:
- Connects to processHandler.output_ready, error_ready, and finished signals
- Provides real-time output display in dedicated subwindows
- Allows for clean process lifecycle management
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QMdiSubWindow, 
                             QSizePolicy, QPlainTextEdit, QLabel, QPushButton, QCheckBox,
                            QSplitter)
from PySide6.QtCore import Qt, QTimer, Signal, QThread, QObject, QProcess
from PySide6.QtGui import QAction, QFont, QTextCursor
import time
from datetime import datetime
from typing import Callable, Optional

from nays.core.logger import setupLogger
from nays.ui.helper.message_box_helper import showErrorMessageBox


class ProcessOutputCapture(QObject):
    """Captures process output and emits signals for GUI updates"""
    
    output_received = Signal(str)
    error_received = Signal(str)
    process_finished = Signal(int)  # exit code
    process_started = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setupLogger(self.__class__.__name__)
        self.process = None
        self.is_running = False


class Charm3DProcessOutputCapture(QObject):
    """Integrates with existing Charm3DLineProcess signals"""
    
    output_received = Signal(str)
    error_received = Signal(str)
    process_finished = Signal(int)  # exit code
    process_started = Signal()
    
    def __init__(self, charm3d_process, parent=None):
        super().__init__(parent)
        self.logger = setupLogger(self.__class__.__name__)
        self.charm3d_process = charm3d_process
        self.is_running = False
        self.working_dir = None
        
        # Connect to existing ProcessHandler signals from Charm3DLineProcess
        if hasattr(charm3d_process, 'processHandler') and charm3d_process.processHandler:
            # Replace the existing handlers with our own that emit signals
            self.original_output_handler = charm3d_process.outputHandler
            self.original_error_handler = charm3d_process.errorHandler  
            self.original_finished_handler = charm3d_process.finishedHandler
            
            # Set our handlers
            charm3d_process.outputHandler = self._handle_output
            charm3d_process.errorHandler = self._handle_error
            charm3d_process.finishedHandler = self._handle_finished
            
            # Reconnect the signals to our handlers
            charm3d_process.processHandler.output_ready.disconnect()
            charm3d_process.processHandler.error_ready.disconnect()
            charm3d_process.processHandler.finished.disconnect()
            
            charm3d_process.processHandler.output_ready.connect(self._handle_output)
            charm3d_process.processHandler.error_ready.connect(self._handle_error)
            charm3d_process.processHandler.finished.connect(self._handle_finished)
            
    def _handle_output(self, text: str):
        """Handle output from ProcessHandler and emit signal"""
        # Call original handler to maintain existing functionality
        if hasattr(self, 'original_output_handler') and callable(self.original_output_handler):
            try:
                self.original_output_handler(text)
            except Exception as e:
                self.logger.debug(f"Error in original output handler: {e}")
        
        # Emit our signal for GUI
        self.output_received.emit(text)
        
    def _handle_error(self, text: str):
        """Handle error from ProcessHandler and emit signal"""
        # Call original handler to maintain existing functionality
        if hasattr(self, 'original_error_handler') and callable(self.original_error_handler):
            try:
                self.original_error_handler(text)
            except Exception as e:
                self.logger.debug(f"Error in original error handler: {e}")
        
        # Emit our signal for GUI
        self.error_received.emit(text)
        
    def _handle_finished(self, exit_code: int):
        """Handle process finished and emit signal"""
        # Call original handler to maintain existing functionality
        if hasattr(self, 'original_finished_handler') and callable(self.original_finished_handler):
            try:
                self.original_finished_handler(exit_code)
            except Exception as e:
                self.logger.debug(f"Error in original finished handler: {e}")
        
        self.is_running = False
        # Emit our signal for GUI
        self.process_finished.emit(exit_code)
        
    def run_charm3d_process(self, working_dir: str):
        """Execute the Charm3D process with the given working directory"""
        self.working_dir = working_dir
        self.is_running = True
        self.process_started.emit()
        
        try:
            result = self.charm3d_process.process(working_dir)
            return result
        except Exception as e:
            self.logger.error(f"Error running Charm3D process: {str(e)}")
            self.error_received.emit(f"Error running Charm3D process: {str(e)}")
            self.process_finished.emit(1)  # Error exit code
            raise
        
    def capture_function_output(self, func: Callable, *args, **kwargs):
        """Capture output from a function call by redirecting stdout/stderr"""
        import io
        import contextlib
        
        # Create string buffers to capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            self.process_started.emit()
            self.is_running = True
            
            # Redirect stdout and stderr
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                try:
                    result = func(*args, **kwargs)
                    
                    # Get captured output
                    stdout_content = stdout_buffer.getvalue()
                    stderr_content = stderr_buffer.getvalue()
                    
                    # Emit output if any
                    if stdout_content:
                        self.output_received.emit(stdout_content)
                    if stderr_content:
                        self.error_received.emit(stderr_content)
                    
                    # Emit result if it's a string
                    if isinstance(result, str) and result.strip():
                        self.output_received.emit(f"\nProcess Result:\n{result}")
                    
                    self.process_finished.emit(0)  # Success
                    return result
                    
                except Exception as e:
                    error_msg = f"Function execution error: {str(e)}"
                    self.error_received.emit(error_msg)
                    self.process_finished.emit(1)  # Error
                    raise
                    
        except Exception as e:
            self.logger.error(f"Error capturing function output: {str(e)}")
            self.error_received.emit(f"Capture error: {str(e)}")
            self.process_finished.emit(1)
        finally:
            self.is_running = False



class WamitProcessOutputCapture(QObject):
    """
    Integrates with WamitProcess for WAMIT process execution
    
    This class connects to ProcessHandler signals from WamitProcess.processHandler to provide
    real-time output display in the GUI. It can work with either a WamitProcess instance or
    directly with a ProcessHandler.
    
    Usage:
        # Option 1: With WamitProcess instance
        wamit_process = WamitProcess()
        wamit_capture = WamitProcessOutputCapture(wamit_process=wamit_process)
        
        # Option 2: With ProcessHandler directly
        wamit_capture = WamitProcessOutputCapture(process_handler=process_handler)
    """
    
    output_received = Signal(str)
    error_received = Signal(str)
    process_finished = Signal(int)  # exit code
    process_started = Signal()
    
    def __init__(self, process_handler=None, wamit_process=None, parent=None):
        super().__init__(parent)
        self.logger = setupLogger(self.__class__.__name__)
        
        # Accept either a WamitProcess instance or a ProcessHandler
        if wamit_process is not None:
            self.wamit_process = wamit_process
            self.process_handler = wamit_process.processHandler
        elif process_handler is not None:
            self.wamit_process = None
            self.process_handler = process_handler
        else:
            raise ValueError("Either wamit_process or process_handler must be provided")
            
        self.is_running = False
        self.working_dir = None
        
        # Connect to ProcessHandler signals
        if self.process_handler:
            self.process_handler.output_ready.connect(self._handle_output)
            self.process_handler.error_ready.connect(self._handle_error)
            self.process_handler.finished.connect(self._handle_finished)
            
    def _handle_output(self, text: str):
        """Handle output from ProcessHandler and emit signal"""
        # Emit our signal for GUI
        self.output_received.emit(text)
        
    def _handle_error(self, text: str):
        """Handle error from ProcessHandler and emit signal"""
        # Emit our signal for GUI
        self.error_received.emit(text)
        
    def _handle_finished(self, exit_code: int):
        """Handle process finished and emit signal"""
        self.is_running = False
        # Emit our signal for GUI
        self.process_finished.emit(exit_code)
        
    def run_wamit_process(self, wamit_exe_path: str, working_dir: str):
        """
        Execute the WAMIT process using WamitProcess.executeWamit() if available,
        otherwise start the process directly with ProcessHandler
        
        Args:
            wamit_exe_path: Path to WAMIT executable
            working_dir: Working directory for the process
        """
        self.working_dir = working_dir
        self.is_running = True
        self.process_started.emit()
        
        try:
            if self.wamit_process is not None:
                # Use WamitProcess.executeWamit() method
                self.logger.info(f"Starting WAMIT process using WamitProcess.executeWamit()")
                result = self.wamit_process.executeWamit(
                    wamitExePath=wamit_exe_path,
                    workingDir=working_dir
                )
                # Note: executeWamit() starts the process asynchronously,
                # so we don't need to do anything else here.
                # The signals will be emitted as the process runs.
            else:
                # Fallback: start process directly with ProcessHandler
                self.logger.info(f"Starting WAMIT process using ProcessHandler directly")
                self.process_handler.start([wamit_exe_path])
                
        except Exception as e:
            self.logger.error(f"Error running WAMIT process: {str(e)}")
            self.error_received.emit(f"Error running WAMIT process: {str(e)}")
            self.process_finished.emit(1)  # Error exit code
            raise
        
    def capture_function_output(self, func: Callable, *args, **kwargs):
        """Capture output from a function call by redirecting stdout/stderr"""
        import io
        import contextlib
        
        # Create string buffers to capture output
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        try:
            self.process_started.emit()
            self.is_running = True
            
            # Redirect stdout and stderr
            with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
                try:
                    result = func(*args, **kwargs)
                    
                    # Get captured output
                    stdout_content = stdout_buffer.getvalue()
                    stderr_content = stderr_buffer.getvalue()
                    
                    # Emit output if any
                    if stdout_content:
                        self.output_received.emit(stdout_content)
                    if stderr_content:
                        self.error_received.emit(stderr_content)
                    
                    # Emit result if it's a string
                    if isinstance(result, str) and result.strip():
                        self.output_received.emit(f"\nProcess Result:\n{result}")
                    
                    self.process_finished.emit(0)  # Success
                    return result
                    
                except Exception as e:
                    error_msg = f"Function execution error: {str(e)}"
                    self.error_received.emit(error_msg)
                    self.process_finished.emit(1)  # Error
                    raise
                    
        except Exception as e:
            self.logger.error(f"Error capturing function output: {str(e)}")
            self.error_received.emit(f"Capture error: {str(e)}")
            self.process_finished.emit(1)
        finally:
            self.is_running = False


class ProcessOutputWidget(QWidget):
    """
    A widget that displays process output in real-time with controls
    """
    
    # Signals
    process_started = Signal()
    process_finished = Signal(int)
    
    def __init__(self, title="Process Output", parent=None):
        super().__init__(parent)
        self.logger = setupLogger(self.__class__.__name__)
        
        # Properties
        self.title = title
        self.process_capture = ProcessOutputCapture(self)
        self.is_running = False
        self.start_time = None
        self.auto_scroll = True
        
        # Setup UI
        self.setupUI()
        self.connectSignals()
        
        # Timer for updating runtime
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateRuntime)
        
    def setupUI(self):
        """Setup the user interface"""
        # Main layout
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(5)
        
        # Create toolbar
        self.toolbar = self.createToolbar()
        mainLayout.addWidget(self.toolbar)
        
        # Create splitter for output areas
        splitter = QSplitter(Qt.Vertical)
        
        # Main output area
        self.outputEdit = QPlainTextEdit()
        self.outputEdit.setObjectName("processOutput")
        self.outputEdit.setReadOnly(True)
        self.outputEdit.setFont(QFont("Consolas", 10))
        self.outputEdit.setMaximumBlockCount(10000)  # Limit memory usage
        
        # Set dark theme for output
        self.outputEdit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444444;
                selection-background-color: #264f78;
            }
        """)
        
        splitter.addWidget(self.outputEdit)
        
        # Error output area (smaller)
        self.errorEdit = QPlainTextEdit()
        self.errorEdit.setObjectName("errorOutput")
        self.errorEdit.setReadOnly(True)
        self.errorEdit.setFont(QFont("Consolas", 9))
        self.errorEdit.setMaximumHeight(150)
        self.errorEdit.setPlaceholderText("Error output will appear here...")
        
        # Set red theme for errors
        self.errorEdit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2d1b1b;
                color: #ff6b6b;
                border: 1px solid #664444;
                selection-background-color: #662222;
            }
        """)
        
        splitter.addWidget(self.errorEdit)
        
        # Set splitter proportions (main output gets most space)
        splitter.setSizes([400, 100])
        
        mainLayout.addWidget(splitter)
        
        # Status bar
        statusLayout = QHBoxLayout()
        statusLayout.setContentsMargins(5, 2, 5, 2)
        
        self.statusLabel = QLabel("Ready")
        self.statusLabel.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
        statusLayout.addWidget(self.statusLabel)
        
        statusLayout.addStretch()
        
        # Runtime label
        self.runtimeLabel = QLabel("Runtime: 00:00")
        self.runtimeLabel.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
        statusLayout.addWidget(self.runtimeLabel)
        
        # Line count
        self.lineCountLabel = QLabel("Lines: 0")
        self.lineCountLabel.setStyleSheet("QLabel { color: #666; font-size: 10px; }")
        statusLayout.addWidget(self.lineCountLabel)
        
        mainLayout.addLayout(statusLayout)
        
    def createToolbar(self):
        """Create toolbar with process control actions"""
        toolbar = QToolBar("Process Controls", self)
        toolbar.setMovable(False)
        
        # Clear output
        clearAction = QAction("🗑️ Clear", self)
        clearAction.setToolTip("Clear output")
        clearAction.triggered.connect(self.clearOutput)
        toolbar.addAction(clearAction)
        
        toolbar.addSeparator()
        
        # Auto-scroll toggle
        self.autoScrollAction = QAction("📜 Auto Scroll", self)
        self.autoScrollAction.setToolTip("Toggle auto-scroll to bottom")
        self.autoScrollAction.setCheckable(True)
        self.autoScrollAction.setChecked(True)
        self.autoScrollAction.triggered.connect(self.toggleAutoScroll)
        toolbar.addAction(self.autoScrollAction)
        
        # Word wrap toggle
        wordWrapAction = QAction("📝 Word Wrap", self)
        wordWrapAction.setToolTip("Toggle word wrap")
        wordWrapAction.setCheckable(True)
        wordWrapAction.setChecked(True)
        wordWrapAction.triggered.connect(self.toggleWordWrap)
        toolbar.addAction(wordWrapAction)
        
        toolbar.addSeparator()
        
        # Export output
        exportAction = QAction("💾 Export", self)
        exportAction.setToolTip("Export output to file")
        exportAction.triggered.connect(self.exportOutput)
        toolbar.addAction(exportAction)
        
        # Copy all
        copyAction = QAction("📋 Copy All", self)
        copyAction.setToolTip("Copy all output to clipboard")
        copyAction.triggered.connect(self.copyAllOutput)
        toolbar.addAction(copyAction)
        
        toolbar.addSeparator()
        
        # Status indicator
        self.statusIndicator = QLabel("⚪")
        self.statusIndicator.setToolTip("Process status")
        toolbar.addWidget(self.statusIndicator)
        
        return toolbar
        
    def connectSignals(self):
        """Connect all signals"""
        self.process_capture.output_received.connect(self.appendOutput)
        self.process_capture.error_received.connect(self.appendError)
        self.process_capture.process_started.connect(self.onProcessStarted)
        self.process_capture.process_finished.connect(self.onProcessFinished)
        
        # Connect text change to update line count
        self.outputEdit.textChanged.connect(self.updateLineCount)
        
    def runFunction(self, func: Callable, *args, **kwargs):
        """Run a function and capture its output"""
        if self.is_running:
            self.appendError("Process is already running!")
            return
            
        self.clearOutput()
        self.appendOutput(f"Starting process: {func.__name__}")
        self.appendOutput(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.appendOutput("-" * 50)
        
        # Run in a separate thread to avoid blocking UI
        try:
            self.process_capture.capture_function_output(func, *args, **kwargs)
        except Exception as e:
            self.appendError(f"Failed to start process: {str(e)}")
            
    def runCharm3DProcess(self, charm3d_capture: Charm3DProcessOutputCapture, working_dir: str):
        """Run a Charm3D process using existing ProcessHandler signals"""
        if self.is_running:
            self.appendError("Process is already running!")
            return
            
        self.clearOutput()
        self.appendOutput(f"Starting Charm3D process")
        self.appendOutput(f"Working directory: {working_dir}")
        self.appendOutput(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.appendOutput("-" * 50)
        
        # Connect the capture signals to our display methods
        charm3d_capture.output_received.connect(self.appendOutput)
        charm3d_capture.error_received.connect(self.appendError)
        charm3d_capture.process_started.connect(self.onProcessStarted)
        charm3d_capture.process_finished.connect(self.onProcessFinished)
        
        # Start the process in a separate thread to avoid blocking UI
        from PySide6.QtCore import QThread, QObject
        
        class Charm3DWorker(QObject):
            def __init__(self, capture, working_dir):
                super().__init__()
                self.capture = capture
                self.working_dir = working_dir
                
            def run(self):
                try:
                    self.capture.run_charm3d_process(self.working_dir)
                except Exception as e:
                    self.capture.error_received.emit(str(e))
        
        self.worker_thread = QThread()
        self.worker = Charm3DWorker(charm3d_capture, working_dir)
        # self.worker.moveToThread(self.worker_thread)
        
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()
    
    def runWamitProcess(self, wamit_capture: WamitProcessOutputCapture, wamit_exe_path: str, working_dir: str):
        """Run a WAMIT process using WamitProcess.executeWamit()"""
        if self.is_running:
            self.appendError("Process is already running!")
            return
            
        self.clearOutput()
        self.appendOutput(f"Starting WAMIT process")
        self.appendOutput(f"Working directory: {working_dir}")
        self.appendOutput(f"Executable: {wamit_exe_path}")
        self.appendOutput(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.appendOutput("-" * 50)
        
        # Connect the capture signals to our display methods
        wamit_capture.output_received.connect(self.appendOutput)
        wamit_capture.error_received.connect(self.appendError)
        wamit_capture.process_started.connect(self.onProcessStarted)
        wamit_capture.process_finished.connect(self.onProcessFinished)
        
        # Start the process using WamitProcess.executeWamit()
        try:
            wamit_capture.run_wamit_process(wamit_exe_path, working_dir)
        except Exception as e:
            self.appendError(f"Failed to start WAMIT process: {str(e)}")
            
    def appendOutput(self, text: str):
        """Append text to output area"""
        if not text.strip():
            return
            
        cursor = self.outputEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Add timestamp for new lines
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                timestamp = datetime.now().strftime('%H:%M:%S')
                formatted_lines.append(f"[{timestamp}] {line}")
            else:
                formatted_lines.append(line)
        
        formatted_text = '\n'.join(formatted_lines)
        cursor.insertText(formatted_text + '\n')
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            scrollbar = self.outputEdit.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    def appendError(self, text: str):
        """Append error text to error area"""
        if not text.strip():
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_text = f"[{timestamp}] {text}"
        
        cursor = self.errorEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(formatted_text + '\n')
        
        # Also add to main output with ERROR prefix
        self.outputEdit.appendPlainText(f"ERROR: {formatted_text}")
        
        # Auto-scroll error area
        scrollbar = self.errorEdit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def onProcessStarted(self):
        """Handle process started"""
        self.is_running = True
        self.start_time = time.time()
        self.statusLabel.setText("Running...")
        self.statusIndicator.setText("🟢")
        self.statusIndicator.setToolTip("Process running")
        self.timer.start(1000)  # Update every second
        self.process_started.emit()
        
    def onProcessFinished(self, exit_code: int):
        """Handle process finished"""
        self.is_running = False
        self.timer.stop()
        
        runtime = time.time() - self.start_time if self.start_time else 0
        
        if exit_code == 0:
            self.statusLabel.setText(f"Completed successfully (Runtime: {runtime:.1f}s)")
            self.statusIndicator.setText("🟢")
            self.statusIndicator.setToolTip("Process completed successfully")
            self.appendOutput(f"\nProcess completed successfully in {runtime:.1f} seconds")
        else:
            self.statusLabel.setText(f"Failed with exit code {exit_code} (Runtime: {runtime:.1f}s)")
            self.statusIndicator.setText("🔴")
            self.statusIndicator.setToolTip(f"Process failed with exit code {exit_code}")
            self.appendError(f"Process failed with exit code {exit_code} after {runtime:.1f} seconds")
            
        self.process_finished.emit(exit_code)
        
    def updateRuntime(self):
        """Update runtime display"""
        if self.start_time:
            runtime = time.time() - self.start_time
            minutes = int(runtime // 60)
            seconds = int(runtime % 60)
            self.runtimeLabel.setText(f"Runtime: {minutes:02d}:{seconds:02d}")
            
    def updateLineCount(self):
        """Update line count display"""
        line_count = self.outputEdit.blockCount()
        self.lineCountLabel.setText(f"Lines: {line_count}")
        
    def clearOutput(self):
        """Clear all output"""
        self.outputEdit.clear()
        self.errorEdit.clear()
        self.statusLabel.setText("Ready")
        self.statusIndicator.setText("⚪")
        self.statusIndicator.setToolTip("Process status")
        self.runtimeLabel.setText("Runtime: 00:00")
        self.updateLineCount()
        
    def toggleAutoScroll(self):
        """Toggle auto-scroll feature"""
        self.auto_scroll = self.autoScrollAction.isChecked()
        
    def toggleWordWrap(self):
        """Toggle word wrap"""
        if self.outputEdit.lineWrapMode() == QPlainTextEdit.NoWrap:
            self.outputEdit.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.outputEdit.setLineWrapMode(QPlainTextEdit.NoWrap)
            
    def exportOutput(self):
        """Export output to file"""
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Process Output", 
            f"process_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Process Output Export - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write("MAIN OUTPUT:\n")
                    f.write(self.outputEdit.toPlainText())
                    f.write("\n\nERROR OUTPUT:\n")
                    f.write(self.errorEdit.toPlainText())
                    
                self.statusLabel.setText(f"Output exported to {filename}")
            except Exception as e:
                showErrorMessageBox("Export Error", f"Failed to export output: {str(e)}")
                
    def copyAllOutput(self):
        """Copy all output to clipboard"""
        from PySide6.QtWidgets import QApplication
        
        clipboard = QApplication.clipboard()
        all_text = self.outputEdit.toPlainText()
        if self.errorEdit.toPlainText().strip():
            all_text += "\n\nERRORS:\n" + self.errorEdit.toPlainText()
        clipboard.setText(all_text)
        self.statusLabel.setText("Output copied to clipboard")


def createProcessOutputSubwindow(mdiArea, title: str, process_function: Callable = None, *args, **kwargs):
    """
    Create a process output subwindow
    
    Args:
        mdiArea: QMdiArea to add the subwindow to
        title: Window title
        process_function: Function to execute and monitor (optional)
        *args, **kwargs: Arguments to pass to the process function
    
    Returns:
        tuple: (sub_window, process_output_widget)
    """
    logger = setupLogger("ProcessOutputHelper")
    
    # Create sub-window
    sub_window = QMdiSubWindow()
    sub_window.setWindowTitle(title)
    
    # Create process output widget
    process_widget = ProcessOutputWidget(title)
    
    # Set the widget as the central widget of the subwindow
    sub_window.setWidget(process_widget)
    
    # Add the sub-window to the MDI area
    mdiArea.addSubWindow(sub_window)
    
    # Resize to a decent size
    sub_window.resize(1000, 700)
    
    # Show the sub-window
    sub_window.show()
    
    # If a process function is provided, run it
    if process_function:
        process_widget.runFunction(process_function, *args, **kwargs)
    
    logger.info(f'Process output subwindow created: {title}')
    
    return sub_window, process_widget


def createCharm3DProcessOutputSubwindow(mdiArea, title: str, charm3d_process, working_dir: str) -> tuple[QMdiSubWindow, ProcessOutputWidget]:
    """
    Create a specialized subwindow for Charm3D process output
    
    Args:
        mdiArea: QMdiArea to add the subwindow to
        title: Window title
        charm3d_process: Charm3DLineProcess instance
        working_dir: Working directory for the process
    
    Returns:
        tuple: (sub_window, process_output_widget)
    """
    logger = setupLogger("ProcessOutputHelper")
    
    # Create sub-window
    sub_window = QMdiSubWindow()
    sub_window.setWindowTitle(title)
    
    # Create process output widget
    process_widget = ProcessOutputWidget(title)
    
    # Create Charm3D process capture that integrates with existing signals
    charm3d_capture = Charm3DProcessOutputCapture(charm3d_process)
    
    # Set the widget as the central widget of the subwindow
    sub_window.setWidget(process_widget)
    
    # Add the sub-window to the MDI area
    mdiArea.addSubWindow(sub_window)
    
    # Resize to a decent size
    sub_window.resize(1000, 700)
    
    # Show the sub-window
    sub_window.show()
    
    # Start the Charm3D process with signal integration
    process_widget.runCharm3DProcess(charm3d_capture, working_dir)
    
    logger.info(f'Charm3D process output subwindow created: {title}')
    
    return sub_window, process_widget


def createBasePySideExecutorOutputSubwindow(mdiArea, title: str, executor) -> tuple[QMdiSubWindow, ProcessOutputWidget]:
    """
    Create a specialized subwindow for BasePySideExecutor process output
    
    This is a generic function that works with any BasePySideExecutor instance or its subclasses
    (WamitPysideExecutor, etc.). It connects to the executor's outputReady, errorReady, and finished signals.
    
    Args:
        mdiArea: QMdiArea to add the subwindow to
        title: Window title
        executor: BasePySideExecutor instance or subclass
    
    Returns:
        tuple: (sub_window, process_output_widget)
        
    Example:
        executor = WamitPysideExecutor(wamit_path)
        executor.setWorkingDirectory(working_dir)
        sub_window, widget = createBasePySideExecutorOutputSubwindow(
            mdiArea, "Process Output", 
            executor
        )
    """
    logger = setupLogger("ProcessOutputHelper")
    
    # Create sub-window
    sub_window = QMdiSubWindow()
    sub_window.setWindowTitle(title)
    
    # Create process output widget
    process_widget = ProcessOutputWidget(title)
    
    # Set the widget as the central widget of the subwindow
    sub_window.setWidget(process_widget)
    
    # Add the sub-window to the MDI area
    mdiArea.addSubWindow(sub_window)
    
    # Resize to a decent size
    sub_window.resize(1000, 700)
    
    # Connect executor signals to widget display methods
    # ExecutionResult objects are passed with stdout/stderr/returnCode
    def handle_output(result):
        if result.stdout:
            process_widget.appendOutput(result.stdout)
    
    def handle_error(result):
        if result.stderr:
            process_widget.appendError(result.stderr)
    
    def handle_finished(result):
        status_msg = f"Process finished with exit code: {result.returnCode}"
        if result.returnCode == 0:
            process_widget.appendOutput(status_msg)
        else:
            process_widget.appendError(status_msg)
        process_widget.onProcessFinished(result.returnCode)
    
    executor.outputReady.connect(handle_output)
    executor.errorReady.connect(handle_error)
    executor.finished.connect(handle_finished)
    
    # Clear and initialize output widget
    process_widget.clearOutput()
    process_widget.appendOutput(f"Starting process: {title}")
    process_widget.appendOutput(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    process_widget.appendOutput("-" * 50)
    process_widget.onProcessStarted()
    
    # Show the sub-window
    sub_window.show()
    
    logger.info(f'BasePySideExecutor process output subwindow created: {title}')
    
    return sub_window, process_widget


def createWamitProcessOutputSubwindow(mdiArea, title: str, wamit_process, wamit_exe_path: str, working_dir: str) -> tuple[QMdiSubWindow, ProcessOutputWidget]:
    """
    Create a specialized subwindow for WAMIT process output
    
    This function integrates with WamitProcess and uses its executeWamit() method.
    
    Args:
        mdiArea: QMdiArea to add the subwindow to
        title: Window title
        wamit_process: WamitProcess instance
        wamit_exe_path: Path to WAMIT executable
        working_dir: Working directory for the process
    
    Returns:
        tuple: (sub_window, process_output_widget, wamit_capture)
        
    Example:
        wamit_process = WamitProcess()
        sub_window, widget, capture = createWamitProcessOutputSubwindow(
            mdiArea, "WAMIT Output", 
            wamit_process, 
            wamit_exe_path, 
            working_dir
        )
    """
    logger = setupLogger("ProcessOutputHelper")
    
    # Create sub-window
    sub_window = QMdiSubWindow()
    sub_window.setWindowTitle(title)
    
    # Create process output widget
    process_widget = ProcessOutputWidget(title)
    
    # Create WAMIT process capture that integrates with WamitProcess
    wamit_capture = WamitProcessOutputCapture(wamit_process=wamit_process)
    
    # Set the widget as the central widget of the subwindow
    sub_window.setWidget(process_widget)
    
    # Add the sub-window to the MDI area
    mdiArea.addSubWindow(sub_window)
    
    # Resize to a decent size
    sub_window.resize(1000, 700)
    
    # Show the sub-window
    sub_window.show()
    
    # Start the WAMIT process with signal integration using WamitProcess.executeWamit()
    process_widget.runWamitProcess(wamit_capture, wamit_exe_path, working_dir)
    
    logger.info(f'WAMIT process output subwindow created: {title}')
    
    return sub_window, process_widget, wamit_capture


# Usage example functions
def createNewProcessOutputWindow(mdiArea, title: str = "Process Output"):
    """Create a new empty process output window"""
    return createProcessOutputSubwindow(mdiArea, title)


def runFunctionInNewWindow(mdiArea, title: str, func: Callable, *args, **kwargs):
    """Run a function in a new process output window"""
    return createProcessOutputSubwindow(mdiArea, title, func, *args, **kwargs)