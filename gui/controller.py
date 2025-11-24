import os

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from assets.SmartStitchLogo import icon
from core.services import SettingsHandler
from core.utils.constants import OUTPUT_SUFFIX
from gui.process import GuiStitchProcess

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ProcessThread(QThread):
    progress = Signal(int, str)
    postProcessConsole = Signal(str)

    def __init__(self, parent):
        super(ProcessThread, self).__init__(parent)

    def run(self):
        process = GuiStitchProcess()
        process.run_with_error_msgs(
            input_path=MainWindow.inputField.text(),
            output_path=MainWindow.outputField.text(),
            status_func=self.progress.emit,
            console_func=self.postProcessConsole.emit,
        )


def initialize_gui():
    global MainWindow
    global settings
    global appVersion
    global appAuthor
    global processThread
    MainWindow = QUiLoader().load(os.path.join(SCRIPT_DIRECTORY, 'layout.ui'))
    settings = SettingsHandler()
    # Sets Window Title & Icon
    pixmap = QPixmap()
    pixmap.loadFromData(icon)
    appIcon = QIcon(pixmap)
    MainWindow.setWindowIcon(appIcon)
    # Sets Window Title
    appVersion = "3.1"
    appAuthor = "MechTechnology"
    MainWindow.setWindowTitle("SmartStitch By {0} [{1}]".format(appAuthor, appVersion))
    # Controls Setup
    on_load()
    bind_signals()
    # Sets up process thread
    processThread = ProcessThread(MainWindow)
    processThread.progress.connect(update_process_progress)
    processThread.postProcessConsole.connect(update_postprocess_console)
    # Show Window
    MainWindow.show()


def on_load(load_profiles=True):
    # App Fields
    MainWindow.statusField.setText("Idle")
    MainWindow.statusProgressBar.setValue(0)
    # Settings Fields
    MainWindow.outputTypeDropdown.setCurrentText(settings.load("output_type"))
    MainWindow.lossyField.setValue(settings.load("lossy_quality"))
    MainWindow.heightField.setValue(settings.load("split_height"))
    MainWindow.widthEnforcementDropdown.setCurrentIndex(settings.load("enforce_type"))
    MainWindow.customWidthField.setValue(settings.load("enforce_width"))
    MainWindow.detectorTypeDropdown.setCurrentIndex(settings.load("detector_type"))
    MainWindow.detectorSensitivityField.setValue(settings.load("senstivity"))
    MainWindow.scanStepField.setValue(settings.load("scan_step"))
    MainWindow.ignoreMarginField.setValue(settings.load("ignorable_pixels"))
    MainWindow.runProcessCheckbox.setChecked(settings.load("run_postprocess"))
    MainWindow.runComicZipCheckbox.setChecked(settings.load("run_comiczip"))
    MainWindow.postProcessAppField.setText(settings.load("postprocess_app"))
    MainWindow.postProcessArgsField.setText(settings.load("postprocess_args"))
    output_type_changed(False)
    enforce_type_changed(False)
    detector_type_changed(False)
    if load_profiles:
        update_profiles_list()
        MainWindow.currentProfileDropdown.setCurrentIndex(settings.get_current_index())
        current_profile_changed(False)


def bind_signals():
    MainWindow.inputField.textChanged.connect(input_field_changed)
    MainWindow.browseButton.clicked.connect(browse_location)
    MainWindow.outputTypeDropdown.currentTextChanged.connect(output_type_changed)
    MainWindow.lossyField.valueChanged.connect(lossy_quality_changed)
    MainWindow.heightField.valueChanged.connect(split_height_changed)
    MainWindow.widthEnforcementDropdown.currentTextChanged.connect(enforce_type_changed)
    MainWindow.customWidthField.valueChanged.connect(custom_width_changed)
    MainWindow.detectorTypeDropdown.currentTextChanged.connect(detector_type_changed)
    MainWindow.detectorSensitivityField.valueChanged.connect(
        detector_sensitivity_changed
    )
    MainWindow.scanStepField.valueChanged.connect(scan_step_changed)
    MainWindow.ignoreMarginField.valueChanged.connect(ignorable_margin_changed)
    MainWindow.currentProfileDropdown.currentTextChanged.connect(
        current_profile_changed
    )
    MainWindow.currentProfileName.textChanged.connect(current_profile_name_changed)
    MainWindow.addProfileButton.clicked.connect(add_profile)
    MainWindow.removeProfileButton.clicked.connect(remove_profile)
    MainWindow.runProcessCheckbox.stateChanged.connect(run_postprocess_changed)
    MainWindow.runComicZipCheckbox.stateChanged.connect(run_comiczip_changed)
    MainWindow.detectorHelpButton.clicked.connect(show_detector_help)
    MainWindow.browsePostProcessAppButton.clicked.connect(browse_postprocess_app)
    MainWindow.postProcessAppField.textChanged.connect(postprocess_app_changed)
    MainWindow.postProcessArgsField.textChanged.connect(postprocess_args_changed)
    MainWindow.startProcessButton.clicked.connect(launch_process_async)


def input_field_changed():
    input_path = MainWindow.inputField.text() or ""
    if input_path:
        MainWindow.outputField.setText(input_path + OUTPUT_SUFFIX)
    else:
        MainWindow.outputField.setText("")
    if (os.path.exists(input_path)):
        settings.save("last_browse_location", input_path)


def browse_location():
    start_directory = settings.load("last_browse_location")
    if not start_directory or not os.path.exists(start_directory):
        start_directory = os.path.expanduser("~")
    dialog = QFileDialog(
        MainWindow,
        'Select Input Directory Files',
        directory=start_directory,
        FileMode=QFileDialog.FileMode.Directory,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.inputField.setText(input_path)
        MainWindow.outputField.setText(input_path + OUTPUT_SUFFIX)


def output_type_changed(save=True):
    file_type = MainWindow.outputTypeDropdown.currentText()
    if save:
        settings.save("output_type", file_type)
    if file_type in ['.jpg', '.webp']:
        MainWindow.lossyWrapper.setHidden(False)
    else:
        MainWindow.lossyWrapper.setHidden(True)


def lossy_quality_changed():
    settings.save("lossy_quality", MainWindow.lossyField.value())


def split_height_changed():
    settings.save("split_height", MainWindow.heightField.value())


def enforce_type_changed(save=True):
    enforce_type = MainWindow.widthEnforcementDropdown.currentIndex()
    if save:
        settings.save("enforce_type", enforce_type)
    if enforce_type == 2:
        MainWindow.customWidthWrapper.setHidden(False)
    else:
        MainWindow.customWidthWrapper.setHidden(True)


def custom_width_changed():
    settings.save("enforce_width", MainWindow.customWidthField.value())


def detector_type_changed(save=True):
    detector_type = MainWindow.detectorTypeDropdown.currentIndex()
    if save:
        settings.save("detector_type", detector_type)
    if detector_type == 1:
        MainWindow.detectorSensitvityWrapper.setHidden(False)
        MainWindow.scanStepWrapper.setHidden(False)
        MainWindow.ignoreMarginWrapper.setHidden(False)
    else:
        MainWindow.detectorSensitvityWrapper.setHidden(True)
        MainWindow.scanStepWrapper.setHidden(True)
        MainWindow.ignoreMarginWrapper.setHidden(True)


def detector_sensitivity_changed():
    settings.save("senstivity", MainWindow.detectorSensitivityField.value())


def scan_step_changed():
    settings.save("scan_step", MainWindow.scanStepField.value())


def ignorable_margin_changed():
    settings.save("ignorable_pixels", MainWindow.ignoreMarginField.value())


def update_profiles_list():
    profile_names = settings.get_profile_names()
    MainWindow.currentProfileDropdown.clear()
    for index in range(len(profile_names)):
        MainWindow.currentProfileDropdown.insertItem(index, profile_names[index])
    return len(profile_names)


def current_profile_changed(save=True):
    current_profile = MainWindow.currentProfileDropdown.currentIndex()
    if save:
        settings.set_current_index(current_profile)
        on_load(False)
    MainWindow.currentProfileName.setText(settings.get_current_profile_name())


def current_profile_name_changed():
    new_name = MainWindow.currentProfileName.text()
    settings.set_current_profile_name(new_name)
    current = MainWindow.currentProfileDropdown.currentIndex()
    MainWindow.currentProfileDropdown.setItemText(current, new_name)


def add_profile():
    profile_name = settings.add_profile()
    new_index = update_profiles_list() - 1
    MainWindow.currentProfileDropdown.setCurrentIndex(new_index)
    MainWindow.currentProfileName.setText(profile_name)


def remove_profile():
    current_profile = MainWindow.currentProfileDropdown.currentIndex()
    settings.remove_profile(current_profile)
    MainWindow.currentProfileDropdown.removeItem(current_profile)
    MainWindow.currentProfileDropdown.setCurrentIndex(0)


def run_postprocess_changed():
    settings.save("run_postprocess", MainWindow.runProcessCheckbox.isChecked())


def run_comiczip_changed():
    settings.save("run_comiczip", MainWindow.runComicZipCheckbox.isChecked())


def show_detector_help():
    QMessageBox.information(
        MainWindow,
        "Detector Settings Help",
        (
            "Detector Type:\n"
            "- Direct Slicing: cuts pages at fixed intervals equal to the Rough Output Height,\n"
            "  ignoring pixel content. This is the fastest mode, but it may cut speech bubbles\n"
            "  or SFX.\n\n"
            "- Smart Pixel Comparison: analyzes pixels around the target cut height\n"
            "  and tries to avoid lines with abrupt color/value changes, reducing the chance\n"
            "  of cutting text or SFX. It is slower, but usually produces better panel splits.\n\n"
            "Object Detection Sensitivity [1-100%]:\n"
            "- High values (90-100): the detector only accepts very homogeneous lines,\n"
            "  minimizing cuts on important content, but producing panels with more varied\n"
            "  heights.\n"
            "- Medium/low values (20-50): the detector tolerates more pixel variation,\n"
            "  which can make panels more uniform, but increases the risk of cutting\n"
            "  speech bubbles/SFX.\n\n"
            "Scan Line Step [1-25 px]:\n"
            "- Controls how many pixels the scan line jumps when searching for the next\n"
            "  candidate cut position after rejecting the current one. Small values (1-5)\n"
            "  give dense scanning (more precise, slower); higher values (10-25) give faster,\n"
            "  but less precise scanning.\n\n"
            "Ignoreable Horizontal Margins [px]:\n"
            "- Number of pixels ignored at the left/right edges of the image during detection.\n"
            "  Useful when there are decorative frames or noise at the borders. This makes the\n"
            "  detector focus on the inner area where panels and speech bubbles are.\n"
            "  Avoid very large values relative to the image width."
        ),
    )


def browse_postprocess_app():
    dialog = QFileDialog(
        MainWindow,
        'Select Post Process Application Directory',
        FileMode=QFileDialog.FileMode.ExistingFile,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.postProcessAppField.setText(input_path)


def postprocess_app_changed():
    settings.save("postprocess_app", MainWindow.postProcessAppField.text())


def postprocess_args_changed():
    settings.save("postprocess_args", MainWindow.postProcessArgsField.text())


def update_process_progress(percentage: int, message: str):
    MainWindow.statusField.setText(message)
    MainWindow.statusProgressBar.setValue(percentage)

def update_postprocess_console(message: str):
    MainWindow.processConsoleField.append(message)


def launch_process_async():
    MainWindow.processConsoleField.clear()
    processThread.start()
