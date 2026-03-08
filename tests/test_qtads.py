import sys
import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QStatusBar

import PySide6QtAds as QtAds


class SimpleWindow(QMainWindow):
    """
    Creates a main window with a dock manager.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(0, 0, 400, 21)

        self.menu_bar = QMenuBar(self)
        self.menu_view = QMenu(self.menu_bar)
        self.menu_view.setTitle("View")

        self.menu_bar.addAction(self.menu_view.menuAction())
        self.setMenuBar(self.menu_bar)

        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)

        # Create the dock manager. Because the parent parameter is a QMainWindow
        # the dock manager registers itself as the central widget.
        self.dock_manager = QtAds.CDockManager(self)

        # Create example content label - this can be any application specific
        # widget
        dock_inner_widget = QLabel()
        dock_inner_widget.setWordWrap(True)
        dock_inner_widget.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        dock_inner_widget.setText("Lorem ipsum dolor sit amet, consectetuer adipiscing elit. ")

        # Create a dock widget with the title Label 1 and set the created label
        # as the dock widget content
        dock_widget = QtAds.CDockWidget("Label 1")
        dock_widget.setWidget(dock_inner_widget)

        # Add the toggleViewAction of the dock widget to the menu to give
        # the user the possibility to show the dock widget if it has been closed
        self.menu_view.addAction(dock_widget.toggleViewAction())

        # Add the dock widget to the top dock widget area
        self.dock_manager.addDockWidget(QtAds.TopDockWidgetArea, dock_widget)


class TestSimpleWindow(unittest.TestCase):
    """
    Basic QtAds tests.
    """

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    def setUp(self):
        self.window = SimpleWindow()
        self.window.show()

    def tearDown(self):
        self.window.close()

    def test_window_is_visible(self):
        assert self.window.isVisible()

    def test_use_native_windows_flag_accessible(self):
        # UseNativeWindows config flag must be accessible for users to resolve
        # drawing artifacts when mixing native and alien widgets (e.g. OpenGL)
        assert hasattr(QtAds.CDockManager, 'UseNativeWindows')

    def test_use_native_windows_flag_value(self):
        # UseNativeWindows must have the correct bit value (0x40000000)
        assert int(QtAds.CDockManager.UseNativeWindows) == 0x40000000


class NativeWindowsWindow(QMainWindow):
    """
    Creates a main window with UseNativeWindows enabled in the dock manager.
    This configuration resolves drawing artifacts when mixing native widgets
    (e.g. QOpenGLWidget) with alien widgets in the same application.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(0, 0, 400, 300)

        # Enable UseNativeWindows before creating the dock manager so that
        # CDockWidget and CDockAreaWidget call winId() in their constructors,
        # giving each a native window handle. This prevents the rendering
        # artifacts that occur when Qt mixes native and alien siblings.
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.UseNativeWindows, True)

        self.dock_manager = QtAds.CDockManager(self)

        dock_inner_widget = QLabel("Native windows enabled")
        dock_widget = QtAds.CDockWidget("NativeLabel")
        dock_widget.setWidget(dock_inner_widget)
        self.dock_manager.addDockWidget(QtAds.TopDockWidgetArea, dock_widget)
        self.dock_widget = dock_widget


class TestUseNativeWindowsFlag(unittest.TestCase):
    """
    Tests that the UseNativeWindows config flag works correctly.

    Drawing artifacts occur when Qt applications mix native widgets (those with
    their own native window handle, such as QOpenGLWidget) with alien widgets
    (regular QWidget subclasses that share their parent's window handle). In
    pure C++ applications the UseNativeWindows flag can be set on CDockManager
    to make every dock and area widget call winId(), forcing them to become
    native. The Python bindings must expose this flag so that Python users can
    apply the same fix.
    """

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)

    def setUp(self):
        # Reset to default config before each test
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.UseNativeWindows, False)
        self.window = NativeWindowsWindow()
        self.window.show()

    def tearDown(self):
        self.window.close()
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.UseNativeWindows, False)

    def test_native_windows_window_is_visible(self):
        assert self.window.isVisible()

    def test_dock_widget_is_native_when_flag_set(self):
        # With UseNativeWindows enabled every CDockWidget must have been made
        # native (WA_NativeWindow attribute set) so that it can be composited
        # correctly alongside other native widgets in the application.
        assert self.window.dock_widget.testAttribute(Qt.WA_NativeWindow)


if __name__ == '__main__':
    unittest.main()
