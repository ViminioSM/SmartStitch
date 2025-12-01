import os

from PySide6.QtCore import QEvent, QObject, Qt, QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMessageBox

from assets.SmartStitchLogo import icon
from core.models import WorkDirectory
from core.services import SettingsHandler, AdvancedPsdMerger, PostProcessRunner
from core.utils.constants import OUTPUT_SUFFIX, POSTPROCESS_SUFFIX
from gui.process import GuiStitchProcess

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class FolderDropFilter(QObject):
    """Event filter that lets QLineEdit fields accept folder drag-and-drop.

    When the user drags a directory from the OS file explorer and drops it
    onto a registered line edit, the line edit text is replaced with the
    directory path. No visual hint is added; behavior-only.
    """

    def eventFilter(self, obj, event):  # type: ignore[override]
        if event.type() == QEvent.Type.DragEnter:
            mime = event.mimeData()
            if mime and mime.hasUrls():
                for url in mime.urls():
                    path = url.toLocalFile()
                    if path and os.path.isdir(path):
                        event.acceptProposedAction()
                        return True
            return False

        if event.type() == QEvent.Type.Drop:
            mime = event.mimeData()
            if mime and mime.hasUrls():
                for url in mime.urls():
                    path = url.toLocalFile()
                    if path and os.path.isdir(path):
                        obj.setText(path)
                        event.acceptProposedAction()
                        return True
            return False

        return QObject.eventFilter(self, obj, event)


class ProcessThread(QThread):
    progress = Signal(int, str)
    postProcessConsole = Signal(str)

    def __init__(self, parent):
        super(ProcessThread, self).__init__(parent)

    def run(self):
        process = GuiStitchProcess()
        input_path = (MainWindow.inputField.text() or "").strip()
        output_path = (MainWindow.outputField.text() or "").strip()

        # If Basic input is configured, run the standard stitching process.
        if input_path:
            process.run_with_error_msgs(
                input_path=input_path,
                output_path=output_path,
                status_func=self.progress.emit,
                console_func=self.postProcessConsole.emit,
            )


def initialize_gui():
    global MainWindow
    global settings
    global appVersion
    global appAuthor
    global processThread
    global folderDropFilter
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
    # Enable drag-and-drop of folders into directory fields.
    folderDropFilter = FolderDropFilter(MainWindow)
    for field in [
        MainWindow.inputField,
        MainWindow.outputField,
        MainWindow.advancedNormalField,
        MainWindow.advancedEditedField,
        MainWindow.advancedPsdSourceField,
    ]:
        field.setAcceptDrops(True)
        field.installEventFilter(folderDropFilter)
    # Sets up process thread
    processThread = ProcessThread(MainWindow)
    processThread.progress.connect(update_process_progress)
    processThread.postProcessConsole.connect(update_postprocess_console)
    # When the main process thread finishes, optionally run Advanced tasks
    processThread.finished.connect(run_advanced_pipeline)
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
    # Sync visibility of Advanced controls (Two folders vs PSD source)
    advanced_source_type_changed()
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
    MainWindow.advancedSourceTypeDropdown.currentIndexChanged.connect(
        advanced_source_type_changed
    )
    MainWindow.browseAdvancedNormalButton.clicked.connect(browse_advanced_normal_folder)
    MainWindow.browseAdvancedEditedButton.clicked.connect(browse_advanced_edited_folder)
    MainWindow.browseAdvancedPsdSourceButton.clicked.connect(
        browse_advanced_psd_source_folder
    )
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


def browse_advanced_normal_folder():
    dialog = QFileDialog(
        MainWindow,
        'Select normal layer folder',
        FileMode=QFileDialog.FileMode.Directory,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.advancedNormalField.setText(input_path)


def browse_advanced_edited_folder():
    dialog = QFileDialog(
        MainWindow,
        'Select edited layer folder',
        FileMode=QFileDialog.FileMode.Directory,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.advancedEditedField.setText(input_path)


def browse_advanced_psd_source_folder():
    dialog = QFileDialog(
        MainWindow,
        'Select PSD source folder',
        FileMode=QFileDialog.FileMode.Directory,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.advancedPsdSourceField.setText(input_path)


def run_advanced_merge():
    normal_dir = (MainWindow.advancedNormalField.text() or "").strip()
    edited_dir = (MainWindow.advancedEditedField.text() or "").strip()

    if not normal_dir or not os.path.isdir(normal_dir):
        QMessageBox.warning(
            MainWindow,
            "Advanced PSD Merge",
            "Please select a valid 'Normal layer' folder.",
        )
        return
    if not edited_dir or not os.path.isdir(edited_dir):
        QMessageBox.warning(
            MainWindow,
            "Advanced PSD Merge",
            "Please select a valid 'Edited layer' folder.",
        )
        return

    def console(message: str) -> None:
        MainWindow.processConsoleField.append(message)

    merger = AdvancedPsdMerger(console_func=console)
    try:
        created = merger.merge_folders_to_psd(
            normal_dir,
            edited_dir,
            yield_func=QApplication.processEvents,
        )
    except Exception as exc:
        QMessageBox.critical(
            MainWindow,
            "Advanced PSD Merge",
            f"An error occurred while merging to PSD: {exc}",
        )
        return

    QMessageBox.information(
        MainWindow,
        "Advanced PSD Merge",
        f"Finished. Created {created} PSD file(s).",
    )


def advanced_source_type_changed():
    """Show/hide Advanced controls based on selected source type.

    Index 0: Two folders (Normal + Edited)
    Index 1: PSD source (folder of PSDs)
    """
    index = MainWindow.advancedSourceTypeDropdown.currentIndex()
    two_folders = index == 0
    psd_mode = index == 1

    # Two-folders controls
    MainWindow.advancedNormalLabel.setHidden(not two_folders)
    MainWindow.advancedNormalField.setHidden(not two_folders)
    MainWindow.browseAdvancedNormalButton.setHidden(not two_folders)
    MainWindow.advancedEditedLabel.setHidden(not two_folders)
    MainWindow.advancedEditedField.setHidden(not two_folders)
    MainWindow.browseAdvancedEditedButton.setHidden(not two_folders)
    # PSD-source controls
    MainWindow.advancedPsdSourceLabel.setHidden(not psd_mode)
    MainWindow.advancedPsdSourceField.setHidden(not psd_mode)
    MainWindow.browseAdvancedPsdSourceButton.setHidden(not psd_mode)


def run_advanced_pipeline():
    """Run Advanced tasks automatically after the main process.

    This function orchestrates the Advanced workflows after the main
    (Basic) stitching process, according to the selected source type:

    - Two folders (Normal + Edited):
      merge matching files from the two folders into 2-layer PSDs.

    - PSD source (folder of PSDs):
      1) Run a full stitching pass on the PSDs to ``[Edited]``.
      2) Run a second pass using only the first PSD layer to
         ``[Original]``.
      3) Merge ``[Original]`` and ``[Edited]`` into final 2-layer PSDs
         in ``[Merged]``.
    """
    # Determine selected source type.
    index = MainWindow.advancedSourceTypeDropdown.currentIndex()

    # --- Mode 0: Two folders (Normal + Edited) ---
    if index == 0:
        # Reuse the existing two-folder merge behavior, but only if the
        # user configured both folders.
        normal_dir = (MainWindow.advancedNormalField.text() or "").strip()
        edited_dir = (MainWindow.advancedEditedField.text() or "").strip()

        if not normal_dir and not edited_dir:
            # Nothing configured in Advanced; silently skip.
            return

        # Show that Advanced work is running and reset the progress bar
        # so it does not stay at 100% while PSDs are still being merged.
        update_process_progress(0, "Working - Running Advanced PSD merge (two folders)")
        run_advanced_merge()
        update_process_progress(100, "Idle - Advanced PSD merge (two folders) completed")
        return

    # --- Mode 1: PSD source (folder of PSDs) ---
    if index == 1:
        psd_source_dir = (MainWindow.advancedPsdSourceField.text() or "").strip()
        if not psd_source_dir:
            # No PSD source configured; nothing to do.
            return
        if not os.path.isdir(psd_source_dir):
            QMessageBox.warning(
                MainWindow,
                "Advanced PSD Source",
                "Please select a valid PSD source folder.",
            )
            return

        edited_dir = psd_source_dir + " [Edited]"
        original_dir = psd_source_dir + " [Original]"
        merged_dir = psd_source_dir + " [Merged]"

        # Log the planned workflow to the console.
        MainWindow.processConsoleField.append(
            f"[Advanced] PSD source mode enabled. Source: {psd_source_dir}"
        )
        MainWindow.processConsoleField.append(
            f"[Advanced] Edited output folder: {edited_dir}"
        )
        MainWindow.processConsoleField.append(
            f"[Advanced] Original output folder: {original_dir}"
        )
        MainWindow.processConsoleField.append(
            f"[Advanced] Merged output folder: {merged_dir}"
        )

        process = GuiStitchProcess()

        try:
            # Reset the progress bar so it reflects the Advanced PSD
            # source workflow instead of staying at 100% from the
            # previous Basic run.
            update_process_progress(0, "Working - Advanced PSD source (Edited pass)")
            # 1) Full PSD pass -> [Edited]
            process.run_with_error_msgs(
                input_path=psd_source_dir,
                output_path=edited_dir,
                status_func=update_process_progress,
                console_func=update_postprocess_console,
                disable_comiczip=True,
            )

            # 2) First-layer-only PSD pass -> [Original]
            update_process_progress(0, "Working - Advanced PSD source (Original pass)")
            process.run_with_error_msgs(
                input_path=psd_source_dir,
                output_path=original_dir,
                status_func=update_process_progress,
                console_func=update_postprocess_console,
                psd_first_layer_only=True,
                disable_postprocess=True,
                disable_comiczip=True,
            )
        except Exception as exc:
            QMessageBox.critical(
                MainWindow,
                "Advanced PSD Source",
                f"An error occurred while running the PSD source pipeline: {exc}",
            )
            return

        # 3) Merge [Original] and [Edited] into [Merged] using the
        # AdvancedPsdMerger service.
        update_process_progress(50, "Working - Advanced PSD merge (Merged folder)")
        def console(message: str) -> None:
            MainWindow.processConsoleField.append(message)

        merger = AdvancedPsdMerger(console_func=console)
        try:
            created = merger.merge_folders_to_psd(
                normal_dir=original_dir,
                edited_dir=edited_dir,
                output_dir=merged_dir,
                yield_func=QApplication.processEvents,
            )
        except Exception as exc:
            QMessageBox.critical(
                MainWindow,
                "Advanced PSD Merge",
                f"An error occurred while merging PSD folders: {exc}",
            )
            return

        # Optionally run ComicZip only on the merged folder when the
        # Advanced PSD source workflow is used.
        if settings.load("run_comiczip"):
            project_root = os.path.dirname(os.path.dirname(__file__))
            comiczip_script = os.path.join(project_root, "scripts", "comiczip.py")

            workdir = WorkDirectory(
                merged_dir,
                merged_dir,
                merged_dir + POSTPROCESS_SUFFIX,
            )
            runner = PostProcessRunner()
            try:
                runner.run(
                    workdirectory=workdir,
                    postprocess_app="python",
                    postprocess_args=f"{comiczip_script} -i [stitched] -o [processed]",
                    console_func=update_postprocess_console,
                )
            except Exception as exc:
                QMessageBox.critical(
                    MainWindow,
                    "Advanced ComicZip",
                    f"An error occurred while running ComicZip on merged folder: {exc}",
                )

        QMessageBox.information(
            MainWindow,
            "Advanced PSD Merge",
            (
                "PSD source workflow completed. Created "
                f"{created} merged PSD file(s) in:\n{merged_dir}"
            ),
        )
        update_process_progress(100, "Idle - Advanced PSD source workflow completed")


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
