"""Language definitions and metadata for Wenyi Ketab.

Supports target languages for translation with language-specific configuration.
"""

from dataclasses import dataclass
from typing import Dict, Literal


@dataclass
class LanguageConfig:
    """Configuration for a target language."""

    code: str  # ISO 639-1 code (e.g., 'fa', 'en')
    name: str  # Display name in English
    native_name: str  # Name in native language
    direction: Literal["ltr", "rtl"]  # Text direction
    description: str  # Brief description


# Supported target languages for translation
LANGUAGES: Dict[str, LanguageConfig] = {
    "fa": LanguageConfig(
        code="fa",
        name="Farsi",
        native_name="فارسی",
        direction="rtl",
        description="Persian language support",
    ),
    "en": LanguageConfig(
        code="en",
        name="English",
        native_name="English",
        direction="ltr",
        description="English language support",
    ),
    "es": LanguageConfig(
        code="es",
        name="Spanish",
        native_name="Español",
        direction="ltr",
        description="Spanish language support",
    ),
    "fr": LanguageConfig(
        code="fr",
        name="French",
        native_name="Français",
        direction="ltr",
        description="French language support",
    ),
    "de": LanguageConfig(
        code="de",
        name="German",
        native_name="Deutsch",
        direction="ltr",
        description="German language support",
    ),
    "ru": LanguageConfig(
        code="ru",
        name="Russian",
        native_name="Русский",
        direction="ltr",
        description="Russian language support",
    ),
}


def get_language(code: str) -> LanguageConfig:
    """Get language configuration by code.
    
    Args:
        code: ISO 639-1 language code
        
    Returns:
        LanguageConfig for the requested language
        
    Raises:
        ValueError: If language code is not supported
    """
    if code not in LANGUAGES:
        supported = ", ".join(LANGUAGES.keys())
        raise ValueError(f"Language '{code}' not supported. Supported: {supported}")
    return LANGUAGES[code]


def list_languages() -> Dict[str, str]:
    """Get list of supported languages for display.
    
    Returns:
        Dictionary mapping codes to display names
    """
    return {code: lang.name for code, lang in LANGUAGES.items()}


def is_rtl(code: str) -> bool:
    """Check if language uses right-to-left text direction.
    
    Args:
        code: ISO 639-1 language code
        
    Returns:
        True if language is RTL, False otherwise
    """
    return get_language(code).direction == "rtl"
