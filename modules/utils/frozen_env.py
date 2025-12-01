"""Frozen environment utilities for PyInstaller builds."""

import os
import sys


class FrozenEnv:
    """Single source of truth for frozen environment detection and path resolution."""

    @classmethod
    def setup(cls) -> None:
        """Configure paths and working directory for frozen environment."""
        if getattr(sys, "frozen", False):
            base = sys._MEIPASS
            if base not in sys.path:
                sys.path.insert(0, base)
            os.chdir(base)

    @classmethod
    def get_path(cls, *parts: str) -> str:
        """Get absolute path that works in both dev and frozen environments."""
        base = (
            sys._MEIPASS
            if getattr(sys, "frozen", False)
            else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        return os.path.join(base, *parts)
