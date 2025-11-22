import os
import sys
from pathlib import Path


def main() -> None:
    try:
        from PyInstaller.__main__ import run as pyinstaller_run
    except ImportError:  # pragma: no cover - defensive runtime check
        print("PyInstaller is not installed. Install it with 'pip install pyinstaller'.")
        sys.exit(1)

    project_root = Path(__file__).resolve().parent.parent

    os.chdir(project_root)

    gui_entry = project_root / "SmartStitchGUI.py"
    if not gui_entry.exists():
        print(f"Entry point not found: {gui_entry}")
        sys.exit(1)

    icon_path = project_root / "assets" / "SmartStitchLogo.ico"
    ui_path = project_root / "gui" / "layout.ui"

    add_data_args: list[str] = []

    if icon_path.exists():
        add_data_args.extend(["--add-data", f"{icon_path};assets"])

    if ui_path.exists():
        add_data_args.extend(["--add-data", f"{ui_path};gui"])

    args: list[str] = [
        str(gui_entry),
        "--name",
        "SmartStitch",
        "--noconfirm",
        "--noconsole",
        "--clean",
        "--onedir",
    ]

    args.extend(add_data_args)

    if icon_path.exists():
        args.extend(["--icon", str(icon_path)])

    pyinstaller_run(args)


if __name__ == "__main__":
    main()
