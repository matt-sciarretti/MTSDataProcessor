from PyQt5 import QtWidgets, QtCore
import matplotlib
# Must specify QT backend before importing backend_qt5agg
matplotlib.use('QT5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT


# NavigationToolbar widget with custom panel of buttons
class NavToolbar(NavigationToolbar2QT):
    toolitems = [t for t in NavigationToolbar2QT.toolitems if
                 t[0] in ('Home','Pan','Zoom','Save')]
    
    

# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure(tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)    # Inherit from QWidget
        self.canvas = MplCanvas()                   # Create canvas object
        self.toolbar = NavToolbar(self.canvas,self) # Create toolbar object
        self.vbl = QtWidgets.QVBoxLayout()          # Set box for plotting
        self.vbl.setAlignment(QtCore.Qt.AlignCenter)
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(self.toolbar)
        self.setLayout(self.vbl)