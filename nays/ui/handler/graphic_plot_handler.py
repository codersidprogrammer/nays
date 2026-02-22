import sys
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
)


class GraphicPlotHandlerBuilder:
    def __init__(self, dataHeaders: list[str], data: np.ndarray):
        self.figure = Figure(figsize=(10, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.headers = dataHeaders
        self.data = data
        self.subplot = self.figure.add_subplot(111)
        self.last_x = None
        self.last_y = None

    def setHeaders(self, dataHeaders: list[str]):
        self.headers = dataHeaders
        return self

    def setData(self, data: np.ndarray):
        self.data = data
        return self

    def plotData(self, xAxes: str, components: list[str]):
        self.subplot.cla()
        # Get column indices
        x_idx = self.headers.index(xAxes)
        component_indices = [self.headers.index(comp) for comp in components]

        # Extract data columns
        x_data = self.data[:, x_idx]
        component_data = [self.data[:, idx] for idx in component_indices]

        # Sort data by x-axis to ensure proper plotting
        sort_idx = np.argsort(x_data)
        x_data = x_data[sort_idx]
        component_data = [col[sort_idx] for col in component_data]

        for i, comp in enumerate(components):
            self.line = self.subplot.plot(x_data, component_data[i], label=comp, marker="o")

        # Add labels and title
        self.subplot.set_xlabel(xAxes)
        self.subplot.set_ylabel("Values")
        self.subplot.set_title(f"{', '.join(components)} vs {xAxes}")
        self.subplot.legend()
        self.subplot.grid(True)

        return self

    def build(self):
        self.canvas.draw()
        return self

    def __convertFigureToQImage(self):
        """Convert the Matplotlib figure to QImage."""
        buf = BytesIO()
        self.canvas.print_png(buf)  # Print the figure as PNG to the buffer
        buf.seek(0)
        qimage = QImage.fromData(buf.read())  # Convert to QImage from the buffer
        return qimage

    def __getPixmap(self):
        """Convert the QImage to QPixmap and return."""
        qimage = self.__convertFigureToQImage()
        pixmap = QPixmap.fromImage(qimage)
        return pixmap
