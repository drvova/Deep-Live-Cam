import json
import os
import sys
from pathlib import Path


def get_locales_path():
    """Get the locales directory path, works for both dev and frozen environments."""
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
        return Path(base_path) / "locales"
    return Path(__file__).parent.parent.parent / "locales"


class LanguageManager:
    def __init__(self, default_language="en"):
        self.current_language = default_language
        self.translations = {}
        self.load_language(default_language)

    def load_language(self, language_code) -> bool:
        """Load language file."""
        if language_code == "en":
            return True
        try:
            file_path = get_locales_path() / f"{language_code}.json"
            with open(file_path, "r", encoding="utf-8") as file:
                self.translations = json.load(file)
            self.current_language = language_code
            return True
        except FileNotFoundError:
            print(f"Language file not found: {language_code}")
            return False
        except Exception as e:
            print(f"Error loading language {language_code}: {e}")
            return False

    def _(self, key, default=None) -> str:
        """Get translated text."""
        return self.translations.get(key, default if default else key)
