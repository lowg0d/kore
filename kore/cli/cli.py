import os
import shutil
import subprocess
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as Et

import click
from PySide6.QtCore import QDir
from PySide6.QtWidgets import QApplication, QFileDialog

DOTUI_PATH = "./src/gui/views/dotui"
VIEWS_PATH = "./src/gui/views"
ASSETS_PATH = "./src/gui/assets"

UIC_COMMAND = "pyside6-uic"
RCC_COMMAND = "pyside6-rcc"
DESIGNER_COMMAND = "pyside6-designer.exe"

ALLOWED_EXTENSIONS = {
    "font": "Font Files (*.ttf *.otf *.woff *.woff2)",
    "icon": "Icon Files (*.svg *.png *.ico *.jpg *.jpeg)",
}

DEFAULT_UIS = {
    "widget": """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>400</width>
    <height>271</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
 </widget>
 <resources>
  <include location="../../assets/src.qrc"/>
 </resources>
 <connections/>
</ui>""",
    "window": """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>602</width>
    <height>378</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget"/>
 </widget>
 <resources>
  <include location="../../assets/src.qrc"/>
 </resources>
 <connections/>
</ui>""",
}
ASSET_TYPE_MAP = ["font", "icon", "appicon", "theme"]
VALID_ICON_EXTENSIONS = (".svg", ".ico", ".png")


def _unzip_template(zip_name: Path, dst: Path):
    """
    Unzip the contents of a template (skipping the root folder) to the destination folder.

    Args:
        zip_name (Path): The path of the zip file to extract.
        dst (Path): The destination folder where the contents will be extracted.
    """
    try:
        # Ensure the destination directory exists
        dst.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_name, "r") as zipf:
            # Get the common prefix for all files to find the root folder (e.g., 'default/')
            root_folder = zipf.namelist()[0].split("/")[0]

            for member in zipf.infolist():
                # Skip the root folder and extract only its contents
                extracted_path = Path(member.filename).relative_to(root_folder)
                if not extracted_path:  # Skip empty root folder entry
                    continue
                destination = dst / extracted_path
                if member.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with open(destination, "wb") as file:
                        file.write(zipf.read(member))

    except Exception as e:
        print(f"Error while unzipping template: {e}")


def _open_file_dialog(
    file_types: str = "All Files (*)", title: str = "Select Files"
) -> tuple:
    """open a file dialog and return the selected files."""
    # Create a Qt application
    app = QApplication([])

    # Open the file dialog allowing the selection of multiple files
    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.ExistingFiles)  # type: ignore
    file_dialog.setWindowTitle(title)

    # Set the initial directory to the user's Downloads folder
    downloads_path = QDir.homePath() + "/Downloads"
    file_dialog.setDirectory(downloads_path)

    # Set the filter for file types
    file_dialog.setNameFilter(file_types)

    # Display the dialog and check if the user has accepted (clicked Open)
    if file_dialog.exec():
        file_paths = file_dialog.selectedFiles()
        # Return the paths of the selected files as a tuple
        return tuple(file_paths)
    else:
        # Return an empty tuple if no files are selected
        return tuple()


def _update_qrc() -> None:
    """
    add the valid icons from the icon folder to the src.qrc file and remove deprecated.
    """
    icons_path = os.path.join(ASSETS_PATH, "icons")
    src_qrc_path = os.path.join(ASSETS_PATH, "src.qrc")

    # List all valid icon files
    valid_icons = {
        f"icons/{f}"
        for f in os.listdir(icons_path)
        if f.endswith(VALID_ICON_EXTENSIONS)
    }

    # Parse the existing QRC file or create a new structure if it doesn't exist
    if os.path.exists(src_qrc_path):
        tree = Et.parse(src_qrc_path)
        root = tree.getroot()

    else:
        root = Et.Element("RCC")
        tree = Et.ElementTree(root)

    # Locate or create the <qresource prefix="icons"> element
    qresource = root.find('.//qresource[@prefix="icons"]')
    if qresource is None:
        qresource = Et.SubElement(root, "qresource", {"prefix": "icons"})

    # Current files in the QRC under the icon prefix
    existing_files = {elem.text for elem in qresource.findall("file")}

    # Determine files to add or remove
    files_to_add = valid_icons - existing_files
    files_to_remove = existing_files - valid_icons

    # Add new files to the qresource
    for file_path in files_to_add:
        print(f"[+] '{file_path}' added !")
        Et.SubElement(qresource, "file").text = file_path

    # Remove outdated files from the qresource
    for file_path in files_to_remove:
        for elem in qresource.findall("file"):
            if elem.text == file_path:
                qresource.remove(elem)

    # Write the updated QRC file
    tree.write(src_qrc_path, encoding="utf-8", xml_declaration=True)


def _compile_rcc():
    start_time: float = time.perf_counter()
    qrc_files = [f for f in os.listdir(ASSETS_PATH) if f.endswith(".qrc")]
    for qrc_file in qrc_files:
        base_name, _ = os.path.splitext(qrc_file)
        qrc_file_path = os.path.join(ASSETS_PATH, qrc_file)
        py_script_path = os.path.join(ASSETS_PATH, f"src_rc.py")

        # Convert QRC to Python script using subprocess
        subprocess.run([RCC_COMMAND, qrc_file_path, "-o", py_script_path], check=True)

    compile_time = int((time.perf_counter() - start_time) * 1000)
    print(f"[+] rcc compile complete in {compile_time}ms")


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("kind", required=True)
def new(kind: str) -> None:
    kind = kind.lower()
    if not kind in DEFAULT_UIS.keys():
        print(f"[-] Type Not Found use: {DEFAULT_UIS.keys()}")
        return

    file_name = click.prompt("[?] file_name: ", default="main_window")
    file_name += ".ui"
    file_path = os.path.join(DOTUI_PATH, file_name)

    counter = 1
    while os.path.exists(file_path):
        file_name = file_name.replace(".ui", f"({counter}).ui")
        file_path = os.path.join(DOTUI_PATH, file_name)
        counter += 1

    with open(file_path, "w") as new_file:
        new_file.write(DEFAULT_UIS[kind])

    subprocess.Popen([DESIGNER_COMMAND, file_path])


@cli.command()
@click.argument("file_name", required=True)
def edit(file_name: str) -> None:

    file_name = file_name.lower() + ".ui"
    file_path = os.path.join(DOTUI_PATH, file_name)

    if os.path.isfile(file_path):
        subprocess.Popen([DESIGNER_COMMAND, file_path])

    else:
        print(f"[-] File not found. available: {os.listdir(DOTUI_PATH)}")


@cli.command()
def compileui() -> None:
    start_time: float = time.perf_counter()

    init_file_path = os.path.join(VIEWS_PATH, "__init__.py")
    ui_files = [f for f in os.listdir(DOTUI_PATH) if f.endswith(".ui")]

    for f in ui_files:
        base_name = os.path.basename(f).replace(".ui", "")
        ui_file_path = os.path.join(DOTUI_PATH, f)
        script_path = os.path.join(VIEWS_PATH, "dotpy", f"{base_name}.py")

        print(f"[+] compiling '{ui_file_path}'...")

        # use uic to compile the files
        subprocess.run([UIC_COMMAND, ui_file_path, "-o", script_path], check=True)

        with open(script_path, "r") as pyf:
            content = pyf.read().replace(
                "import src_rc", "from src.gui.assets import src_rc"
            )

        with open(script_path, "w") as pyf:
            pyf.write(content)

    ## import the main classes to init file to make importing easier.
    if not os.path.exists(init_file_path):
        print("[!] __init__.py not found in the views directory.")
        return

    with open(init_file_path, "r") as f:
        existing_imports = [
            line.strip() for line in f if line.startswith("from .dotpy.")
        ]

    print("[+] modifying '__init__.py'...")
    for uif in ui_files:
        base_name = os.path.basename(uif).replace(".ui", "")
        uif_path = os.path.join(VIEWS_PATH, "dotpy", f"{base_name}.py")

        import_statements = ""
        with open(uif_path, "r") as f:
            for line in f:
                if line.startswith("class Ui_"):
                    ui_class = line.split()[1].split("(")[0]
                    import_statement = f"from .dotpy.{base_name} import {ui_class}"
                    if import_statement not in existing_imports:
                        import_statements += f"{import_statement}"

        with open(init_file_path, "r") as initf:
            init_contents = initf.read()

        if import_statements:
            init_contents = f"{init_contents}\n{import_statements}"

            with open(init_file_path, "w") as initf:
                initf.write(init_contents)

    compile_time = int((time.perf_counter() - start_time) * 1000)
    print(f"[+] ui compile complete in {compile_time}ms")


@cli.command()
def compilercc() -> None:
    _compile_rcc()


@cli.command()
def updatercc() -> None:
    start_time: float = time.perf_counter()
    _update_qrc()
    compile_time = int((time.perf_counter() - start_time) * 1000)
    print(f"[+] assets updated in {compile_time}ms")
    print(f"[+] recompiling src.qrc")
    _compile_rcc()


@cli.command()
def create_template() -> None:
    pass


@cli.command()
@click.argument("name", required=False)
def start(name: str) -> None:
    dst_path = os.path.abspath("./")
    if not name:
        name = click.prompt("Project Name", default="my-project")

    current_file_path = Path(__file__).parent
    template_folder = current_file_path.parent / "templates"

    if template_folder.exists() and template_folder.is_dir():
        templates = os.listdir(str(template_folder))
        templates = [
            item.replace(".zip", "") for item in templates if item.endswith(".zip")
        ]

    else:
        print(f"Template folder '{template_folder}' not found.")
        return

    template = click.prompt(
        "Select a template", type=click.Choice(templates), default=templates[0]  # type: ignore
    )

    if click.confirm("Initialize Git Repository ?", default=True):
        init_git = True
    else:
        init_git = False

    click.echo("Creating the project structure...")

    template_path = template_folder / f"{template}.zip"
    _unzip_template(template_path, Path(dst_path))


@cli.command()
@click.argument("kind", required=True)
def add(kind: str) -> None:
    if kind.endswith("s"):
        kind = kind[:-1]

    if not kind in ASSET_TYPE_MAP:
        print(f"[+] '{kind}' is not a valid type, use: {ASSET_TYPE_MAP}")
        return

    if kind == "theme":
        print("[-] Not available")
        return

    destination_path = os.path.join(ASSETS_PATH, f"{kind}s")
    files = _open_file_dialog(ALLOWED_EXTENSIONS[kind], f"Select a valid '{kind}' !")
    for f in files:
        file_path = os.path.normpath(f)
        base_name = os.path.basename(f)
        file_destination_path = os.path.join(destination_path, base_name)
        shutil.copy(file_path, file_destination_path)

        print(f"[+] '{base_name}' added to '{kind}")


def main():
    cli()


if __name__ == "__main__":
    main()
