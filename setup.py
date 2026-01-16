from setuptools import setup

APP = ['main.py']
DATA_FILES = ['exiftool_src']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['PyQt6'],
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'ExifGeek',
        'CFBundleDisplayName': 'ExifGeek',
        'CFBundleGetInfoString': "ExifGeek Metadata Tool",
        'CFBundleIdentifier': "com.trae.exifgeek",
        'CFBundleVersion': "0.1.0",
        'CFBundleShortVersionString': "0.1.0",
        'NSHumanReadableCopyright': u"@JhihHe"
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
