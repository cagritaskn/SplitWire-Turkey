"""
Language/Localization manager for SplitWire-Turkey Linux.

Provides multi-language support using JSON translation files.
Compatible with the Windows version's language file format.
"""

import json
from pathlib import Path
from typing import Optional, Any
from functools import lru_cache


class LanguageError(Exception):
    """Exception raised for language-related errors."""
    pass


class LanguageManager:
    """
    Manages application translations.

    Loads language strings from JSON files and provides
    easy access to translations via get_text().

    Language files are stored in:
    - Resources: src/splitwire/resources/languages/
    - User overrides: ~/.local/share/splitwire/languages/
    """

    # Supported languages
    LANGUAGES = {
        "tr": "Türkçe",
        "en": "English",
        "ru": "Русский",
        "es": "Español",
    }

    DEFAULT_LANGUAGE = "en"

    def __init__(self, language: str = DEFAULT_LANGUAGE, resources_dir: Optional[Path] = None):
        """
        Initialize language manager.

        Args:
            language: Language code (tr, en, ru, es)
            resources_dir: Override resources directory (for testing)
        """
        self._language = language if language in self.LANGUAGES else self.DEFAULT_LANGUAGE
        self._translations: dict[str, Any] = {}
        self._fallback_translations: dict[str, Any] = {}

        # Determine resources directory
        if resources_dir:
            self._resources_dir = resources_dir
        else:
            # Default: relative to this file's location
            self._resources_dir = Path(__file__).parent.parent / "resources" / "languages"

        # Load translations
        self._load_translations()

    @property
    def language(self) -> str:
        """Get current language code."""
        return self._language

    @property
    def language_name(self) -> str:
        """Get current language name."""
        return self.LANGUAGES.get(self._language, "Unknown")

    @classmethod
    def get_available_languages(cls) -> dict[str, str]:
        """Get dictionary of available languages (code -> name)."""
        return cls.LANGUAGES.copy()

    def set_language(self, language: str) -> bool:
        """
        Change the current language.

        Args:
            language: Language code

        Returns:
            True if language was changed successfully
        """
        if language not in self.LANGUAGES:
            return False

        if language == self._language:
            return True

        self._language = language
        self._load_translations()
        return True

    def _load_translations(self) -> None:
        """Load translations for current language."""
        # Always load fallback (English) first
        if self._language != self.DEFAULT_LANGUAGE:
            fallback_file = self._resources_dir / f"{self.DEFAULT_LANGUAGE}.json"
            self._fallback_translations = self._load_json_file(fallback_file)
        else:
            self._fallback_translations = {}

        # Load current language
        lang_file = self._resources_dir / f"{self._language}.json"
        self._translations = self._load_json_file(lang_file)

        # Clear the cache when translations change
        self.get_text.cache_clear()

    def _load_json_file(self, path: Path) -> dict[str, Any]:
        """Load a JSON translation file."""
        if not path.exists():
            return {}

        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load language file {path}: {e}")
            return {}

    @lru_cache(maxsize=512)
    def get_text(self, *keys: str, default: str = "") -> str:
        """
        Get translated text for the given key(s).

        Supports nested keys:
            get_text("messages", "error")  -> translations["messages"]["error"]
            get_text("buttons.save")       -> translations["buttons"]["save"]
            get_text("simple_key")         -> translations["simple_key"]

        Args:
            *keys: Key path (multiple args or dot-separated)
            default: Default value if key not found

        Returns:
            Translated string
        """
        # Handle both get_text("a", "b") and get_text("a.b")
        if len(keys) == 1 and "." in keys[0]:
            key_path = keys[0].split(".")
        else:
            key_path = list(keys)

        # Try current language first
        result = self._get_nested(self._translations, key_path)
        if result is not None:
            return result

        # Fall back to default language
        result = self._get_nested(self._fallback_translations, key_path)
        if result is not None:
            return result

        # Return default or key path as fallback
        return default if default else ".".join(key_path)

    def _get_nested(self, data: dict, keys: list[str]) -> Optional[str]:
        """Get nested value from dictionary."""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        # Return only if it's a string
        return current if isinstance(current, str) else None

    def format_text(self, *keys: str, **kwargs) -> str:
        """
        Get translated text and format it with the given arguments.

        Uses Python's str.format() for placeholders.
        Also supports positional {0}, {1} style (Windows compatibility).

        Args:
            *keys: Key path
            **kwargs: Format arguments

        Returns:
            Formatted translated string
        """
        text = self.get_text(*keys)

        # Handle both {name} and {0} style placeholders
        try:
            if kwargs:
                # Try named format first
                return text.format(**kwargs)
            else:
                return text
        except (KeyError, IndexError):
            return text

    def format_text_positional(self, *keys: str, args: tuple = ()) -> str:
        """
        Get translated text and format with positional arguments.

        For Windows compatibility with {0}, {1} style placeholders.

        Args:
            *keys: Key path
            args: Positional format arguments

        Returns:
            Formatted translated string
        """
        text = self.get_text(*keys)
        try:
            return text.format(*args)
        except (KeyError, IndexError):
            return text

    def get_section(self, section: str) -> dict[str, str]:
        """
        Get all translations in a section.

        Args:
            section: Section name (e.g., "buttons", "messages")

        Returns:
            Dictionary of key -> translated text
        """
        result = self._translations.get(section, {})
        if isinstance(result, dict):
            # Filter to only string values
            return {k: v for k, v in result.items() if isinstance(v, str)}
        return {}

    def reload(self) -> None:
        """Reload translations from files."""
        self._load_translations()


# Global instance for convenience
_language_manager: Optional[LanguageManager] = None


def get_language_manager() -> LanguageManager:
    """Get the global LanguageManager instance."""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager


def init_language_manager(language: str = LanguageManager.DEFAULT_LANGUAGE) -> LanguageManager:
    """Initialize the global LanguageManager with a specific language."""
    global _language_manager
    _language_manager = LanguageManager(language)
    return _language_manager


def get_text(*keys: str, default: str = "") -> str:
    """Get translated text (convenience function)."""
    return get_language_manager().get_text(*keys, default=default)


def format_text(*keys: str, **kwargs) -> str:
    """Get and format translated text (convenience function)."""
    return get_language_manager().format_text(*keys, **kwargs)


def set_language(language: str) -> bool:
    """Set the current language (convenience function)."""
    return get_language_manager().set_language(language)


def get_current_language() -> str:
    """Get current language code (convenience function)."""
    return get_language_manager().language


# Alias for Windows compatibility
_ = get_text


if __name__ == "__main__":
    # Test the language manager
    print("=" * 50)
    print("LanguageManager Test")
    print("=" * 50)

    # Create test language files
    test_dir = Path("/tmp/splitwire_lang_test")
    test_dir.mkdir(exist_ok=True)

    # English
    en_data = {
        "buttons": {
            "save": "Save",
            "cancel": "Cancel",
            "install": "Install"
        },
        "messages": {
            "success": "Operation completed successfully!",
            "error": "An error occurred: {0}",
            "confirm": "Are you sure you want to {action}?"
        },
        "simple": "A simple string"
    }
    with open(test_dir / "en.json", "w") as f:
        json.dump(en_data, f)

    # Turkish
    tr_data = {
        "buttons": {
            "save": "Kaydet",
            "cancel": "İptal",
            "install": "Yükle"
        },
        "messages": {
            "success": "İşlem başarıyla tamamlandı!",
            "error": "Bir hata oluştu: {0}",
            "confirm": "{action} işlemini onaylıyor musunuz?"
        },
        "simple": "Basit bir metin"
    }
    with open(test_dir / "tr.json", "w") as f:
        json.dump(tr_data, f)

    # Test English
    manager = LanguageManager("en", test_dir)
    print(f"\nLanguage: {manager.language_name}")
    print(f"buttons.save: {manager.get_text('buttons', 'save')}")
    print(f"buttons.cancel: {manager.get_text('buttons.cancel')}")
    print(f"messages.success: {manager.get_text('messages', 'success')}")
    print(f"simple: {manager.get_text('simple')}")
    print(f"not_found: {manager.get_text('not_found', default='DEFAULT')}")

    # Test formatting
    print(f"error formatted: {manager.format_text_positional('messages', 'error', args=('Test error',))}")
    print(f"confirm formatted: {manager.format_text('messages', 'confirm', action='install')}")

    # Test Turkish
    print("\n--- Switching to Turkish ---")
    manager.set_language("tr")
    print(f"Language: {manager.language_name}")
    print(f"buttons.save: {manager.get_text('buttons', 'save')}")
    print(f"messages.success: {manager.get_text('messages', 'success')}")

    # Test get_section
    print("\n--- Section test ---")
    buttons = manager.get_section("buttons")
    print(f"All buttons: {buttons}")

    # Cleanup
    import shutil
    shutil.rmtree(test_dir)
    print("\nTest completed!")
