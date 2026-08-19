"""Configuration schema and validation for Wenyi Ketab."""

from pathlib import Path
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from trans_novel.config.languages import LANGUAGES


class TranslationConfig(BaseModel):
    """Configuration model for translation job."""

    # File configuration
    epub_path: str = Field(..., description="Path to EPUB file")
    output_dir: str = Field(default="output", description="Output directory")

    # Language configuration
    source_language: Optional[str] = Field(
        default=None, description="Source language (auto-detect if None)"
    )
    target_language: str = Field(..., description="Target language code")

    # LLM configuration
    provider: Literal[
        "deepseek", "openai", "openrouter", "google_gemini", "ollama", "vllm"
    ] = Field(default="deepseek", description="LLM provider")
    api_key: str = Field(..., description="API key for LLM provider")
    model: Optional[str] = Field(default=None, description="Specific model name")

    # Pipeline configuration
    polish: bool = Field(default=False, description="Enable polishing stage")
    review: bool = Field(default=False, description="Enable final review stage")
    bilingual: bool = Field(
        default=True, description="Generate bilingual output"
    )

    # Output configuration
    output_formats: List[Literal["epub", "txt", "html", "markdown", "word"]] = Field(
        default=["epub"], description="Output formats"
    )

    # Processing configuration
    batch_size: int = Field(default=3, description="Batch size for processing")
    max_workers: int = Field(default=4, description="Number of parallel workers")
    resumable: bool = Field(
        default=True, description="Enable checkpoint-based resumability"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "epub_path": "book.epub",
                "target_language": "fa",
                "provider": "deepseek",
                "api_key": "sk-...",
                "output_formats": ["epub", "txt"],
                "polish": False,
                "review": False,
                "bilingual": True,
            }
        }

    @field_validator("epub_path")
    @classmethod
    def validate_epub_path(cls, v: str) -> str:
        """Validate EPUB file exists and has correct extension."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"File not found: {v}")
        if path.suffix.lower() != ".epub":
            raise ValueError(f"File must be EPUB format, got: {path.suffix}")
        return v

    @field_validator("target_language")
    @classmethod
    def validate_target_language(cls, v: str) -> str:
        """Validate target language is supported."""
        if v not in LANGUAGES:
            supported = ", ".join(LANGUAGES.keys())
            raise ValueError(
                f"Language '{v}' not supported. Supported: {supported}"
            )
        return v

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate LLM provider."""
        valid_providers = [
            "deepseek",
            "openai",
            "openrouter",
            "google_gemini",
            "ollama",
            "vllm",
        ]
        if v.lower() not in valid_providers:
            raise ValueError(f"Invalid provider: {v}")
        return v.lower()

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate API key is not empty."""
        if not v or not v.strip():
            raise ValueError("API key cannot be empty")
        return v

    @field_validator("output_formats")
    @classmethod
    def validate_output_formats(cls, v: List[str]) -> List[str]:
        """Validate output formats."""
        valid_formats = ["epub", "txt", "html", "markdown", "word"]
        for fmt in v:
            if fmt not in valid_formats:
                raise ValueError(f"Invalid format: {fmt}")
        if not v:
            raise ValueError("At least one output format must be selected")
        return v

    @field_validator("batch_size")
    @classmethod
    def validate_batch_size(cls, v: int) -> int:
        """Validate batch size."""
        if v < 1:
            raise ValueError("Batch size must be at least 1")
        return v

    @field_validator("max_workers")
    @classmethod
    def validate_max_workers(cls, v: int) -> int:
        """Validate max workers."""
        if v < 1:
            raise ValueError("Max workers must be at least 1")
        return v

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()
