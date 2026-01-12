# -*- mode: python ; coding: utf-8 -*-
"""
NewsDigest PyInstaller Specification File

This file configures PyInstaller to build standalone executables
for the NewsDigest CLI application.

Usage:
    pyinstaller newsdigest.spec --distpath dist --workpath build/pyinstaller

Or use the packaging script:
    ./scripts/package.sh --exe
    scripts\package.bat --exe
"""

import sys
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(SPECPATH)
SRC_DIR = PROJECT_ROOT / "src"
NEWSDIGEST_DIR = SRC_DIR / "newsdigest"

# Get version from pyproject.toml
try:
    import tomllib
    with open(PROJECT_ROOT / "pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
        VERSION = pyproject["project"]["version"]
except Exception:
    VERSION = "0.1.0"

# Platform-specific settings
if sys.platform == "win32":
    EXE_NAME = f"newsdigest-{VERSION}-windows"
    ICON = None  # Add path to .ico file if available
elif sys.platform == "darwin":
    EXE_NAME = f"newsdigest-{VERSION}-macos"
    ICON = None  # Add path to .icns file if available
else:
    EXE_NAME = f"newsdigest-{VERSION}-linux"
    ICON = None

# Hidden imports for dynamic dependencies
HIDDEN_IMPORTS = [
    # CLI framework
    "click",
    "click.core",
    "click.decorators",
    "click.testing",

    # Rich console
    "rich",
    "rich.console",
    "rich.table",
    "rich.progress",
    "rich.markup",
    "rich.text",

    # HTTP client
    "httpx",
    "httpx._transports",
    "httpx._transports.default",
    "httpcore",

    # HTML/XML parsing
    "bs4",
    "bs4.builder",
    "bs4.builder._lxml",
    "lxml",
    "lxml.etree",
    "lxml.html",
    "readability",
    "readability.readability",
    "feedparser",

    # NLP
    "spacy",

    # Configuration
    "yaml",
    "pydantic",
    "pydantic.main",
    "pydantic_core",
    "dotenv",

    # Date utilities
    "dateutil",
    "dateutil.parser",

    # Standard library extras
    "encodings",
    "encodings.utf_8",
    "encodings.ascii",
    "encodings.latin_1",
]

# Data files to include
DATAS = [
    # Include package data
    (str(NEWSDIGEST_DIR), "newsdigest"),
]

# Analysis
a = Analysis(
    [str(SRC_DIR / "newsdigest" / "cli" / "main.py")],
    pathex=[str(SRC_DIR)],
    binaries=[],
    datas=DATAS,
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude development dependencies
        "pytest",
        "mypy",
        "ruff",
        "pre_commit",
        "mkdocs",

        # Exclude optional heavy dependencies
        "torch",
        "transformers",
        "tensorflow",
        "keras",

        # Exclude test files
        "tests",

        # Exclude documentation
        "docs",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove unnecessary files to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith("libQt")]
a.binaries = [x for x in a.binaries if not x[0].startswith("PyQt")]

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=EXE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable if UPX is available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # CLI application needs console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON,
)
