import sys
import unittest

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMenu,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

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
        # UseNativeWindows is a valid opt-in feature; verify it is reachable.
        assert hasattr(QtAds.CDockManager, 'UseNativeWindows')

    def test_use_native_windows_flag_value(self):
        # UseNativeWindows must have the correct bit value (0x40000000)
        assert int(QtAds.CDockManager.UseNativeWindows) == 0x40000000


# ---------------------------------------------------------------------------
# Helper widget that mimics QVTKRenderWindowInteractor: it calls winId() in
# its constructor *without* first setting Qt.WA_DontCreateNativeAncestors.
# Without the fix in CDockWidget.setWidget this makes Qt promote every
# ancestor widget (container, scroll area, CDockWidget, CDockAreaWidget,
# CDockManager, …) to native, causing drawing artifacts when the floating
# dock window is resized.
# ---------------------------------------------------------------------------

class _NativeChildWidget(QWidget):
    """QWidget that acquires a native window handle during construction."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.winId()  # promotes ancestors unless WA_DontCreateNativeAncestors is set


class TestNativeChildDrawingArtefacts(unittest.TestCase):
    """
    Regression tests for the drawing artifacts reported when embedding a
    widget that calls winId() (e.g. QVTKRenderWindowInteractor) inside a
    CDockWidget.

    Root cause
    ----------
    When a child widget calls winId() without first setting
    Qt.WA_DontCreateNativeAncestors, Qt promotes *every* ancestor to native.
    That propagation reaches the dock-manager internals and causes visual
    artifacts when the floating window is resized.

    The pure-C++ application avoids this by setting
    Qt::WA_DontCreateNativeAncestors on the native widget before calling
    winId(), keeping all dock-hierarchy ancestors alien.

    Fix
    ---
    CDockWidget.setWidget injects code that walks the widget subtree and sets
    Qt::WA_DontCreateNativeAncestors on every widget that already has
    Qt::WA_NativeWindow, capping propagation at the dock boundary before the
    widget is reparented into the dock hierarchy.
    """

    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)

    def setUp(self):
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.UseNativeWindows, False)
        self.main_window = QMainWindow()
        self.dock_manager = QtAds.CDockManager(self.main_window)
        self.main_window.show()

    def tearDown(self):
        self.main_window.close()

    def test_dock_manager_stays_alien_when_native_child_is_added(self):
        """CDockManager must not become native when a widget that contains a
        native child (via winId()) is passed to CDockWidget.setWidget()."""
        container = QWidget()
        layout = QVBoxLayout(container)
        native_child = _NativeChildWidget(container)
        layout.addWidget(native_child)

        dock = QtAds.CDockWidget("NativeChild")
        dock.setWidget(container)
        self.dock_manager.addDockWidget(QtAds.TopDockWidgetArea, dock)

        assert not self.dock_manager.testAttribute(Qt.WA_NativeWindow), (
            "CDockManager became native due to native-child propagation; "
            "this causes drawing artifacts when the floating window is resized."
        )

    def test_native_child_keeps_its_handle_after_setWidget(self):
        """The native child widget must retain its own native window handle
        even after being embedded inside the dock hierarchy."""
        container = QWidget()
        layout = QVBoxLayout(container)
        native_child = _NativeChildWidget(container)
        layout.addWidget(native_child)

        dock = QtAds.CDockWidget("NativeChild")
        dock.setWidget(container)
        self.dock_manager.addDockWidget(QtAds.TopDockWidgetArea, dock)

        assert native_child.testAttribute(Qt.WA_NativeWindow), (
            "Native child widget lost its native window handle after setWidget()."
        )


if __name__ == '__main__':
    unittest.main()
