"""Tests for multilingual wizard and language configuration."""

import pytest
from trans_novel.config.languages import (
    LANGUAGES,
    get_language,
    list_languages,
    is_rtl,
)
from trans_novel.cli.prompts import OutputFormat, ValidationErrors
from trans_novel.output.word_exporter import BiDiSegmenter, BiDiTextRun


class TestLanguageConfig:
    """Test language configuration module."""

    def test_supported_languages(self):
        """Test that supported languages are defined."""
        assert len(LANGUAGES) == 6
        assert "fa" in LANGUAGES
        assert "en" in LANGUAGES
        assert "es" in LANGUAGES
        assert "fr" in LANGUAGES
        assert "de" in LANGUAGES
        assert "ru" in LANGUAGES

    def test_get_language(self):
        """Test getting language config."""
        fa_lang = get_language("fa")
        assert fa_lang.code == "fa"
        assert fa_lang.name == "Farsi"
        assert fa_lang.direction == "rtl"

    def test_get_language_invalid(self):
        """Test getting invalid language raises error."""
        with pytest.raises(ValueError):
            get_language("invalid")

    def test_list_languages(self):
        """Test listing all languages."""
        langs = list_languages()
        assert len(langs) == 6
        assert langs["fa"] == "Farsi"
        assert langs["en"] == "English"

    def test_is_rtl(self):
        """Test RTL detection."""
        assert is_rtl("fa") is True
        assert is_rtl("en") is False
        assert is_rtl("es") is False


class TestOutputFormats:
    """Test output format definitions."""

    def test_format_info(self):
        """Test getting format info."""
        epub_info = OutputFormat.get_info("epub")
        assert epub_info["name"] == "EPUB"
        assert epub_info["extension"] == ".epub"

    def test_word_format_dependencies(self):
        """Test Word format has required dependencies."""
        word_info = OutputFormat.get_info("word")
        assert len(word_info["required_deps"]) > 0
        assert any("python-docx" in dep for dep in word_info["required_deps"])

    def test_get_required_deps(self):
        """Test getting dependencies for format combination."""
        deps = OutputFormat.get_required_deps(["word", "epub"])
        assert any("python-docx" in dep for dep in deps)


class TestBiDiSegmenter:
    """Test BiDi text segmentation."""

    def test_segment_farsi_text(self):
        """Test segmenting Farsi text."""
        text = "سلام جهان"
        runs = BiDiSegmenter.segment_text(text, "fa")
        assert len(runs) > 0
        assert all(isinstance(r, BiDiTextRun) for r in runs)

    def test_segment_mixed_text(self):
        """Test segmenting mixed LTR/RTL text."""
        text = "Hello سلام World"
        runs = BiDiSegmenter.segment_text(text, "fa")
        # Should segment into multiple runs
        assert len(runs) > 1

    def test_rtl_char_detection(self):
        """Test RTL character detection."""
        assert BiDiSegmenter._is_rtl_char('ع') is True  # Arabic letter
        assert BiDiSegmenter._is_ltr_char('a') is True  # Latin letter
        assert BiDiSegmenter._is_ltr_char('ع') is False

    def test_segment_english_text(self):
        """Test segmenting English text (should be single run)."""
        text = "Hello World"
        runs = BiDiSegmenter.segment_text(text, "en")
        # For LTR languages, should be single run
        assert len(runs) == 1
        assert runs[0].direction == "ltr"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
