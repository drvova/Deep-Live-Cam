#!/usr/bin/env python3
"""Deep-Live-Cam application entry point."""

# Import the tkinter fix to patch the ScreenChanged error
import tkinter_fix
from modules.core.app import run

if __name__ == "__main__":
    run()
