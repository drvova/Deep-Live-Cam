#!/usr/bin/env python3
"""Deep-Live-Cam application entry point."""

import os
import sys


def get_base_path():
    """Get the base path for the application, works for both dev and frozen."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def setup_frozen_environment():
    """Setup paths for PyInstaller frozen environment."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        os.chdir(base_path)


setup_frozen_environment()

import tkinter_fix
from modules.core.app import run

if __name__ == "__main__":
    run()
