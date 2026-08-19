"""Prompt and validator utilities for setup wizard."""

from typing import List


class SetupPrompts:
    """Collection of prompts for the setup wizard."""

    WELCOME = """
╔════════════════════════════════════════════════════════════╗
║          Welcome to Wenyi Ketab - Setup Wizard             ║
║                                                            ║
║   Transform your books into multiple languages            ║
║   with AI-powered translation and quality review          ║
╚════════════════════════════════════════════════════════════╝
    """

    LANGUAGE_SELECT = "Select target language:"
    FILE_PATH = "Enter EPUB file path:"
    API_PROVIDER = "Select LLM provider:"
    API_KEY = "Enter API key:"
    POLISH = "Enable translation polishing (stronger model, higher cost)?"
    REVIEW = "Enable final AI review (highest cost, best quality)?"
    BILINGUAL = "Generate bilingual output (original + translation side-by-side)?"
    OUTPUT_FORMATS = "Select output formats:"
    CONFIRM = "Is this configuration correct?"


class OutputFormat:
    """Output format definitions."""

    FORMATS = {
        "epub": {
            "name": "EPUB",
            "description": "Standard e-book format (best for readers)",
            "extension": ".epub",
            "required_deps": [],
        },
        "txt": {
            "name": "Plain Text",
            "description": "Simple text format",
            "extension": ".txt",
            "required_deps": [],
        },
        "html": {
            "name": "HTML",
            "description": "Web-ready format",
            "extension": ".html",
            "required_deps": [],
        },
        "markdown": {
            "name": "Markdown",
            "description": "Markdown format for documentation",
            "extension": ".md",
            "required_deps": [],
        },
        "word": {
            "name": "Word (.docx)",
            "description": "Microsoft Word format",
            "extension": ".docx",
            "required_deps": ["python-docx>=0.8.11"],
        },
    }

    @classmethod
    def get_info(cls, format_code: str) -> dict:
        """Get format information."""
        if format_code not in cls.FORMATS:
            raise ValueError(f"Unknown format: {format_code}")
        return cls.FORMATS[format_code]

    @classmethod
    def list_all(cls) -> dict:
        """List all available formats."""
        return cls.FORMATS

    @classmethod
    def get_required_deps(cls, formats: List[str]) -> List[str]:
        """Get all required dependencies for selected formats."""
        deps = []
        for fmt in formats:
            if fmt in cls.FORMATS:
                deps.extend(cls.FORMATS[fmt]["required_deps"])
        return list(set(deps))  # Remove duplicates


class ValidationErrors:
    """Validation error messages."""

    FILE_NOT_FOUND = "File not found: {path}"
    INVALID_FILE_FORMAT = "File must be EPUB format: {path}"
    INVALID_LANGUAGE = "Language '{lang}' is not supported."
    INVALID_PROVIDER = "Provider '{provider}' is not supported."
    INVALID_FORMAT = "Format '{fmt}' is not supported."
    INVALID_API_KEY = "API key cannot be empty."
    INVALID_CHOICE = "Please enter a valid choice."
