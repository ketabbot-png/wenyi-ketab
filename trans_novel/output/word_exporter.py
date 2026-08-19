"""Word (.docx) output handler with proper bilingual and BiDi support.

Handles mixed LTR/RTL text with proper paragraph-level and run-level
direction management for languages like Farsi, Arabic, and Hebrew.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_PARAGRAPH_ALIGNMENT
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.shared import Pt, RGBColor, Inches
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from bidi.algorithm import get_display
    BIDI_AVAILABLE = True
except ImportError:
    BIDI_AVAILABLE = False

from trans_novel.config.languages import is_rtl, get_language


class BiDiTextRun:
    """Represents a text run with language-specific direction.
    
    Segments text into runs based on language script direction (LTR/RTL).
    """

    def __init__(self, text: str, direction: str, lang_code: str):
        """Initialize a BiDi-aware text run.
        
        Args:
            text: Text content
            direction: 'ltr' or 'rtl'
            lang_code: ISO 639-1 language code
        """
        self.text = text
        self.direction = direction
        self.lang_code = lang_code


class BiDiSegmenter:
    """Segments mixed-direction text into language-specific runs.
    
    For bilingual output with mixed LTR and RTL text, intelligently
    separates text runs by language and direction.
    """

    # Unicode ranges for common scripts
    ARABIC_SCRIPT = re.compile(r'[\u0600-\u06FF]+')
    FARSI_SCRIPT = re.compile(r'[\u06A0-\u06FF]+')
    CJK_SCRIPT = re.compile(r'[\u4E00-\u9FFF]+')  # Chinese
    LATIN_SCRIPT = re.compile(r'[a-zA-Z0-9\u0020-\u007E]+')

    @classmethod
    def segment_text(cls, text: str, target_lang: str) -> List[BiDiTextRun]:
        """Segment mixed text into directional runs.
        
        Args:
            text: Mixed LTR/RTL text
            target_lang: Target language code
            
        Returns:
            List of BiDiTextRun objects
        """
        runs = []
        target_is_rtl = is_rtl(target_lang)
        
        # Simple regex-based segmentation for Persian/Arabic text
        if target_is_rtl:
            # For RTL languages, segment by detecting LTR vs RTL runs
            segments = cls._segment_by_direction(text)
            for segment_text, detected_direction in segments:
                runs.append(
                    BiDiTextRun(
                        text=segment_text.strip(),
                        direction=detected_direction,
                        lang_code=target_lang if detected_direction == 'rtl' else 'en',
                    )
                )
        else:
            # For LTR languages, keep as single run
            runs.append(BiDiTextRun(text=text, direction='ltr', lang_code=target_lang))

        return [r for r in runs if r.text]  # Filter empty runs

    @classmethod
    def _segment_by_direction(cls, text: str) -> List[Tuple[str, str]]:
        """Segment text by detecting LTR and RTL portions.
        
        Args:
            text: Mixed text
            
        Returns:
            List of (text, direction) tuples
        """
        segments = []
        current_segment = ""
        current_direction = None

        for char in text:
            # Detect character direction
            if cls._is_rtl_char(char):
                detected_dir = 'rtl'
            elif cls._is_ltr_char(char):
                detected_dir = 'ltr'
            else:
                # Neutral character (space, punctuation) - maintain current direction
                detected_dir = current_direction

            # Start new segment if direction changes
            if current_direction is not None and detected_dir != current_direction and detected_dir:
                if current_segment:
                    segments.append((current_segment, current_direction))
                current_segment = char
                current_direction = detected_dir
            else:
                current_segment += char
                if detected_dir:
                    current_direction = detected_dir

        # Add final segment
        if current_segment:
            segments.append((current_segment, current_direction or 'ltr'))

        return segments

    @staticmethod
    def _is_rtl_char(char: str) -> bool:
        """Check if character is RTL (Arabic/Farsi/Hebrew)."""
        code = ord(char)
        # Arabic: U+0600–U+06FF
        # Hebrew: U+0590–U+05FF
        return (0x0600 <= code <= 0x06FF) or (0x0590 <= code <= 0x05FF)

    @staticmethod
    def _is_ltr_char(char: str) -> bool:
        """Check if character is LTR (Latin, digits)."""
        code = ord(char)
        return (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A) or (0x0030 <= code <= 0x0039)


class WordExporter:
    """Export translated content to Word (.docx) format.
    
    Handles bilingual output with proper paragraph-level and run-level
    direction management using the python-docx library.
    """

    def __init__(self, target_language: str, bilingual: bool = False):
        """Initialize Word exporter.
        
        Args:
            target_language: Target language code
            bilingual: If True, include both source and translation
            
        Raises:
            ImportError: If python-docx is not installed
        """
        if not DOCX_AVAILABLE:
            raise ImportError(
                "python-docx is required for Word output. "
                "Install with: pip install python-docx"
            )
        
        self.target_language = target_language
        self.bilingual = bilingual
        self.is_rtl = is_rtl(target_language)
        self.lang_config = get_language(target_language)
        self.doc = Document()
        self._setup_document_rtl()

    def _setup_document_rtl(self) -> None:
        """Configure document for RTL languages if needed."""
        if self.is_rtl:
            # Set document-level RTL setting
            section = self.doc.sections[0]
            # Access section properties XML
            sectPr = section._sectPr
            # Add BiDi (bidirectional) property
            bidi = OxmlElement('w:bidi')
            sectPr.append(bidi)

    def add_title(self, title: str) -> None:
        """Add document title.
        
        Args:
            title: Book title
        """
        p = self.doc.add_paragraph()
        p.style = 'Heading 1'
        p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT if self.is_rtl else WD_PARAGRAPH_ALIGNMENT.LEFT
        
        run = p.add_run(title)
        run.font.size = Pt(24)
        run.font.bold = True
        
        # Set paragraph direction
        self._set_paragraph_direction(p)

    def add_chapter_heading(self, chapter_num: int, chapter_title: str) -> None:
        """Add chapter heading.
        
        Args:
            chapter_num: Chapter number
            chapter_title: Chapter title
        """
        p = self.doc.add_paragraph()
        p.style = 'Heading 2'
        p.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT if self.is_rtl else WD_PARAGRAPH_ALIGNMENT.LEFT
        
        run = p.add_run(f"Chapter {chapter_num}: {chapter_title}")
        run.font.size = Pt(16)
        run.font.bold = True
        
        self._set_paragraph_direction(p)
        self.doc.add_paragraph()  # Spacing

    def add_translation_paragraph(
        self,
        translated_text: str,
        source_text: Optional[str] = None,
    ) -> None:
        """Add translated paragraph with optional source text.
        
        For bilingual output, handles both LTR and RTL text properly.
        Segments text by direction and applies appropriate formatting.
        
        Args:
            translated_text: Translated text in target language
            source_text: Optional original text (for bilingual output)
        """
        if self.bilingual and source_text:
            # Add source text paragraph
            source_p = self.doc.add_paragraph()
            source_p.alignment = (
                WD_PARAGRAPH_ALIGNMENT.RIGHT
                if is_rtl('en')
                else WD_PARAGRAPH_ALIGNMENT.LEFT
            )
            
            source_run = source_p.add_run(source_text)
            source_run.font.size = Pt(10)
            source_run.font.color.rgb = RGBColor(128, 128, 128)  # Gray
            source_run.italic = True
            self._set_paragraph_direction(source_p)

        # Add translation paragraph
        trans_p = self.doc.add_paragraph()
        trans_p.alignment = (
            WD_PARAGRAPH_ALIGNMENT.RIGHT if self.is_rtl else WD_PARAGRAPH_ALIGNMENT.LEFT
        )
        
        # Segment text by direction for proper BiDi handling
        text_runs = BiDiSegmenter.segment_text(translated_text, self.target_language)
        
        for text_run in text_runs:
            run = trans_p.add_run(text_run.text)
            run.font.size = Pt(12)
            
            # Set run-level direction properties
            self._set_run_direction(run, text_run.direction)
        
        # Set paragraph-level direction
        self._set_paragraph_direction(trans_p)

    def _set_paragraph_direction(self, paragraph) -> None:
        """Set BiDi properties at paragraph level.
        
        Args:
            paragraph: python-docx Paragraph object
        """
        pPr = paragraph._element.get_or_add_pPr()
        
        # Remove existing BiDi element if present
        existing_bidi = pPr.find(qn('w:bidi'))
        if existing_bidi is not None:
            pPr.remove(existing_bidi)
        
        # Add BiDi element for RTL paragraphs
        if self.is_rtl:
            bidi = OxmlElement('w:bidi')
            pPr.append(bidi)
            
            # Set text alignment (right for RTL)
            jc = OxmlElement('w:jc')
            jc.set(qn('w:val'), 'right')
            pPr.append(jc)

    def _set_run_direction(self, run, direction: str) -> None:
        """Set BiDi properties at run level.
        
        Args:
            run: python-docx Run object
            direction: 'ltr' or 'rtl'
        """
        rPr = run._element.get_or_add_rPr()
        
        # Remove existing BiDi element if present
        existing_bidi = rPr.find(qn('w:rtl'))
        if existing_bidi is not None:
            rPr.remove(existing_bidi)
        
        # Set run-level direction
        if direction == 'rtl':
            rtl = OxmlElement('w:rtl')
            rtl.set(qn('w:val'), '1')
            rPr.append(rtl)

    def save(self, output_path: str) -> None:
        """Save document to file.
        
        Args:
            output_path: Path to save .docx file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(output_path))
        print(f"Word document saved to: {output_path}")


def export_to_word(
    chapters: List[dict],
    target_language: str,
    output_path: str,
    bilingual: bool = False,
    title: str = "Translated Book",
) -> None:
    """Export translated chapters to Word format.
    
    Convenience function to export full translation.
    
    Args:
        chapters: List of chapter dictionaries with 'title' and 'paragraphs'
        target_language: Target language code
        output_path: Output file path
        bilingual: Include source text
        title: Book title
        
    Example:
        chapters = [
            {
                'title': 'Chapter 1',
                'paragraphs': [
                    {'translation': 'سلام جهان', 'source': 'Hello World'},
                    ...
                ]
            }
        ]
        export_to_word(chapters, 'fa', 'output.docx', bilingual=True)
    """
    if not DOCX_AVAILABLE:
        raise ImportError(
            "python-docx is required. Install with: pip install python-docx"
        )
    
    exporter = WordExporter(target_language, bilingual)
    exporter.add_title(title)
    
    for chapter_idx, chapter in enumerate(chapters, 1):
        exporter.add_chapter_heading(chapter_idx, chapter.get('title', ''))
        
        for para in chapter.get('paragraphs', []):
            translation = para.get('translation', '')
            source = para.get('source') if bilingual else None
            exporter.add_translation_paragraph(translation, source)
    
    exporter.save(output_path)
