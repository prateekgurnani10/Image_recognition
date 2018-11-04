import pytest
from coreUI import main_window as dejavu_window_main
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPushButton


@pytest.yield_fixture(scope='session')
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        yield app
        app.exit()
    else:
        yield app


class QtBot(object):

    def click(self, widget):
        widget.click()


@pytest.yield_fixture
def qtbot(qapp, request):
    result = QtBot()
    yield result
    qapp.closeAllWindows()


def test_button_clicked(qtbot):
    button = QPushButton()
    clicked = [False]

    def on_clicked():
        clicked[0] = True

    button.clicked.connect(on_clicked)
    button.clicked.connect(lambda: print("--> test button clicked"))
    qtbot.click(button)
    assert clicked[0]


def test_main_window(qtbot):
    main_window = dejavu_window_main.MainWindow().importButton
    clicked = [False]

    def on_clicked():
        clicked[0] = True

    main_window.importButton.clicked.connect(on_clicked)
    main_window.importButton.clicked.connect(lambda: print("--> import button clicked"))
    qtbot.click(main_window.importButton)
    assert clicked[0]
