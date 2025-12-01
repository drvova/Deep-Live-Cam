#!/usr/bin/env python3
"""Deep-Live-Cam application entry point."""

import tkinter_fix  # Apply tkinter patch for frozen environments
from modules.core.app import run

if __name__ == "__main__":
    run()
