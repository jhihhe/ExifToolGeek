ExifGeek // Metadata Transporter
================================

[English](README_en.md) | [中文](README.md)

![Platform](https://img.shields.io/badge/Platform-macOS-000000?style=flat-square&logo=apple&logoColor=white)
![Language](https://img.shields.io/badge/Language-Python_3-3776AB?style=flat-square&logo=python&logoColor=white)
![Framework](https://img.shields.io/badge/Framework-PyQt6-41CD52?style=flat-square&logo=qt&logoColor=white)
![Copyright](https://img.shields.io/badge/Copyright-@JhihHe-blueviolet?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

![Screenshot](https://raw.githubusercontent.com/jhihhe/ExifToolGeek/main/界面.png)

ExifGeek is a macOS desktop application built on top of the excellent [ExifTool](https://github.com/exiftool/exiftool). It focuses on one core workflow:

- Extract full EXIF/metadata from a **source image**
- Inject that metadata into **one or many target images**

The app is designed like a terminal/geeky “compile panel”, with a Dracula-inspired color theme and code-style typography.

> Copyright @JhihHe  
> ExifTool remains under its own license.


Features
--------

- **Two-panel workflow**
  - Left: source image, EXIF preview, copy/export actions
  - Right: target images list
- **Full EXIF copy**
  - Uses ExifTool `-TagsFromFile -all:all -overwrite_original`
  - Supports injecting into a single file, multiple files, or whole folders (recursively)
- **Drag and drop**
  - Drag a source image from Finder to the left “SOURCE IMAGE” drop zone
  - Drag files or folders to the right “TARGET IMAGE(S)” drop zone
- **Chinese / English UI switch**
  - Toggle language via the `中文 / English` buttons in the top-left
  - All labels, buttons, and status messages are translated
- **Dracula themed geek UI**
  - Semi-transparent, dark “frosted glass” background
  - Code-style monospace font
  - Colored EXIF “syntax highlighting” in the preview area
  - Colored target path list (directory, filename, extension in different colors)
- **EXIF tools**
  - Copy EXIF JSON to clipboard
  - Export EXIF JSON to a `.txt` file


Tech Stack
----------

- Python 3
- PyQt6 – UI framework
- ExifTool – metadata engine (bundled)
- py2app – macOS `.app` packaging


Project Structure
-----------------

Key files and directories:

- `main.py` – PyQt6 UI and app logic (drag-and-drop, EXIF reading/writing, i18n)
- `setup.py` – py2app packaging configuration for building `ExifGeek.app`
- `exiftool_src/` – bundled ExifTool distribution used at runtime inside the app bundle
- `icon.icns` – Dracula-style macOS app icon
- `dist/ExifGeek.app` – built application bundle
- `dist/ExifGeek_prev.app` – previous UI build kept as a backup


Installation (Development)
--------------------------

1. **Clone this repository**

   ```bash
   git clone <your-repo-url>
   cd trae_exiftoolGUImac
   ```

2. **Create and activate a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   Typical requirements (for reference):

   - `pyqt6`
   - `py2app`
   - `pillow` (for icon generation, optional)


Running from Source
-------------------

From the project root:

```bash
source venv/bin/activate
python3 main.py
```

This will launch the PyQt6 window directly without packaging.


Building the macOS .app
-----------------------

To build `dist/ExifGeek.app` using py2app:

```bash
source venv/bin/activate
python3 setup.py py2app
```

Important details:

- `setup.py` is configured to:
  - Bundle `exiftool_src` into the app resources
  - Set the icon to `icon.icns`
  - Use `@JhihHe` for the bundle copyright
- At runtime, `ExifGeek` detects the bundled ExifTool via the `RESOURCEPATH` environment variable and falls back to `exiftool` in `PATH` if needed.


Usage
-----

### 1. Choose the UI language

- Use the top-left buttons:
  - `中文` – Chinese
  - `English` – English

### 2. Load the source image

- Drag a file from Finder onto the left drop zone labeled “SOURCE IMAGE”
  - Or click the drop zone and choose a file from the file dialog
- The app will:
  - Call ExifTool to read EXIF (`-j` JSON)
  - Show a colorized, code-like EXIF view in the left text area

You can then:

- **Copy** – copy the EXIF JSON to clipboard
- **Export TXT** – save the EXIF JSON to a `.txt` file

### 3. Add target images

- Drag files or folders onto the right drop zone labeled “TARGET IMAGE(S)”
  - Folders are scanned recursively
  - Hidden files (starting with `.`) are ignored
- The target list shows colored paths:
  - Directory in a muted color
  - Filename and extension in different Dracula colors

### 4. Inject metadata

- When there is a source image and at least one target, the `>>> INJECT METADATA >>>` button becomes active.
- Click it:
  - ExifGeek runs ExifTool with:

    ```bash
    -TagsFromFile <source> -all:all -overwrite_original <target>
    ```

  - All targets are processed in a loop
  - The status bar shows progress and a final summary (success count vs total)

### 5. Clear and start over

- Click **CLEAR ALL** to:
  - Reset source path
  - Clear the EXIF preview
  - Clear the target list
  - Disable the inject button


Internationalization (i18n)
---------------------------

The app has a simple key-based translation system:

- `TRANSLATIONS` dictionary in `main.py` contains `en` and `zh` entries.
- UI text is looked up via `self.tr(key)` based on `self.curr_lang`.
- Language buttons call `change_language('en' | 'zh')`, which:
  - Updates the current language
  - Refreshes all labels, button texts, drop zone hints, and status text

If you want to add another language:

1. Add a new language entry (for example `ja`) to `TRANSLATIONS`.
2. Add a new toggle button and hook it to `change_language`.


EXIF Display Details
--------------------

- Raw JSON from ExifTool is kept in memory (`self.current_meta`) for:
  - Clipboard copy
  - TXT export
- The preview area uses HTML with inline styles to:
  - Color keys and values differently
  - Treat numbers, lists, and dictionaries with different highlight rules
  - Keep a monospaced “code block” appearance


Known Limitations
-----------------

- No progress bar per file, only a simple status summary.
- No undo: `-overwrite_original` is used to avoid `_original` backup files.
- Error details are printed to stdout / console, not shown in the GUI dialog.


License
-------

- ExifGeek source code: © @JhihHe, all rights reserved.
- ExifTool: Copyright and license belong to Phil Harvey and contributors.  
  See the original ExifTool repository for details: https://github.com/exiftool/exiftool


Contact
-------

For feedback or feature requests, please open an issue on the GitHub repository or contact **@JhihHe**.

