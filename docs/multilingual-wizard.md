# Multilingual Setup Wizard - Usage Guide

## Overview

Wenyi Ketab now supports interactive multilingual translation with a guided setup wizard. This guide explains how to use the new features.

## Quick Start

### Basic Usage (Interactive Wizard)

The simplest way to start a translation:

```bash
uv run trans-novel translate book.epub
```

This launches the interactive setup wizard that guides you through:
1. **File Selection** - Validates EPUB file
2. **Target Language** - Choose from 6 languages (Farsi, English, Spanish, French, German, Russian)
3. **API Provider** - Select your LLM provider (DeepSeek, OpenAI, OpenRouter, Google Gemini, Ollama, vLLM)
4. **API Key Configuration** - Automatically detects environment variables or prompts for input
5. **Output Formats** - Select output formats (EPUB, TXT, HTML, Markdown, Word)
6. **Quality Settings** - Enable optional polishing and review stages
7. **Confirmation** - Review and confirm all settings

## Wizard Screenshots

### Step 1: Welcome Screen
```
╔════════════════════════════════════════════════════════════╗
║          Welcome to Wenyi Ketab - Setup Wizard             ║
║                                                            ║
║   Transform your books into multiple languages            ║
║   with AI-powered translation and quality review          ║
╚════════════════════════════════════════════════════════════╝
```

### Step 2: Target Language Selection
```
Step 2/6: Target Language

╭─ Available Target Languages ───────────────────────────────╮
│ #  Language        Native Name                            │
├────────────────────────────────────────────────────────────┤
│ 1  Farsi           فارسی                                   │
│ 2  English         English                                │
│ 3  Spanish         Español                                │
│ 4  French          Français                               │
│ 5  German          Deutsch                                │
│ 6  Russian         Русский                                │
╰────────────────────────────────────────────────────────────╯

Select language [1]: 1
✓ Selected: Farsi (فارسی)
```

### Step 3: API Provider & Key
```
Step 3/6: API Provider and Key

╭─ Available LLM Providers ──────────────────────────────────╮
│ #  Provider                                               │
├────────────────────────────────────────────────────────────┤
│ 1  DeepSeek                                               │
│ 2  OpenAI                                                 │
│ 3  OpenRouter                                             │
│ 4  Google Gemini                                          │
│ 5  Ollama                                                 │
│ 6  vLLM                                                   │
╰────────────────────────────────────────────────────────────╯

Select provider [1]: 1
✓ Selected: DeepSeek

🔑 Found DEEPSEEK_API_KEY in environment
Use this API key? [Y/n]: y
✓ Using environment API key
```

### Step 4: Output Formats
```
Step 4/6: Output Formats

Select output formats (space-separated numbers or 'all'):
  1. EPUB
  2. TXT
  3. HTML
  4. Markdown
  5. Word (.docx)

Output formats [1]: 1 5
✓ Selected: EPUB, Word (.docx)

⚠ Word format requires additional dependency (python-docx)
  Install with: pip install python-docx
```

### Step 5: Quality Settings
```
Step 5/6: Quality Settings

Polishing: Improve translation quality with a stronger model
Enable polishing? [y/N]: n
✗ Polishing disabled

Final Review: AI-driven whole-book consistency review
Enable final review? [y/N]: n
✗ Final review disabled

Bilingual Output: Source and translation side-by-side
Enable bilingual output? [Y/n]: y
✓ Bilingual output enabled
```

### Step 6: Review & Confirm
```
Step 6/6: Confirm Configuration

╭─ Configuration Summary ────────────────────────────────────╮
│ Setting              Value                               │
├────────────────────────────────────────────────────────────┤
│ File                 book.epub                            │
│ Target Language      Farsi (فارسی)                        │
│ LLM Provider         Deepseek                             │
│ Output Formats       EPUB, WORD                           │
│ Polishing            ✗ Disabled                           │
│ Final Review         ✗ Disabled                           │
│ Bilingual            ✓ Enabled                            │
╰────────────────────────────────────────────────────────────╯

Is this configuration correct? [Y/n]: y
✓ Configuration saved

╔════════════════════════════════════════════════════════════╗
║                 Setup Complete!                          ║
║   Starting translation: book.epub                        ║
╚════════════════════════════════════════════════════════════╝
```

## Advanced Usage

### Command-Line Options (Skip Wizard)

If you prefer not to use the wizard:

```bash
# Translate to Farsi without wizard
uv run trans-novel translate book.epub --no-wizard \
  --language fa \
  --provider deepseek \
  --polish \
  --bilingual
```

### Environment Variables

Set API keys via environment variables to skip interactive input:

```bash
# DeepSeek
export DEEPSEEK_API_KEY="sk-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# OpenRouter
export OPENROUTER_API_KEY="sk-..."

# Google Gemini
export GOOGLE_API_KEY="..."

# Ollama (local)
export OLLAMA_API_KEY="..."

# vLLM
export VLLM_API_KEY="..."
```

Then run:

```bash
uv run trans-novel translate book.epub
```

## Output Formats

### Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| **EPUB** | `.epub` | Standard e-book format, preserves styling and images |
| **TXT** | `.txt` | Plain text, simplest format |
| **HTML** | `.html` | Web-ready format with styling |
| **Markdown** | `.md` | Markdown format for documentation |
| **Word** | `.docx` | Microsoft Word with BiDi and multilingual support |

### Word Format - BiDi Support

The Word exporter includes special handling for bidirectional text:

- **RTL Languages (Farsi, Arabic)**: Proper paragraph direction and alignment
- **Mixed Text**: Intelligent segmentation of LTR/RTL runs
- **Bilingual Output**: Source text styled as gray italic, translation in normal
- **Character Support**: Full Unicode support for Persian, Arabic, Hebrew

Example Word output structure:
```
[Book Title]

[Chapter 1: Opening]

(English source text in gray italic)
متن ترجمه‌شده به فارسی در سطح معمولی

(English source text in gray italic)
متن ترجمه‌شده به فارسی در سطر بعد
```

### Installing Optional Dependencies

For Word format support:

```bash
# Using pip
pip install python-docx python-bidi

# Using uv
uv sync --extra word-output
```

## Supported Languages

| Code | Language | Native Name | Direction |
|------|----------|-------------|----------|
| `fa` | Farsi | فارسی | RTL |
| `en` | English | English | LTR |
| `es` | Spanish | Español | LTR |
| `fr` | French | Français | LTR |
| `de` | German | Deutsch | LTR |
| `ru` | Russian | Русский | LTR |

## Configuration File

After using the wizard, configuration is saved internally. To view or edit manually:

```yaml
# config.yaml example
epub_path: "book.epub"
target_language: "fa"
provider: "deepseek"
api_key: "${DEEPSEEK_API_KEY}"  # References environment variable
output_formats:
  - epub
  - word
polish: false
review: false
bilinngual: true
```

## Troubleshooting

### API Key Not Found

If the wizard can't find your API key in environment variables:

1. Check the environment variable name is correct
2. Restart your terminal/IDE after setting the variable
3. Verify with: `echo $DEEPSEEK_API_KEY`
4. Or enter the key when prompted during setup

### Word Export Issues

If Word export fails:

```bash
# Install required dependencies
pip install python-docx python-bidi
```

### Bilingual Output Issues

For best bilingual results with RTL languages:

1. Ensure source text language is properly detected
2. Use Word format for best bidirectional text handling
3. EPUB bilingual support depends on e-reader capabilities

## Examples

### Example 1: Translate to Farsi with Bilingual EPUB

```bash
uv run trans-novel translate book.epub
# Follow wizard prompts, select:
# - Farsi
# - DeepSeek
# - EPUB output
# - Bilingual: yes
```

### Example 2: Translate to Spanish with Word Output

```bash
uv run trans-novel translate book.epub --no-wizard \
  --language es \
  --bilingual
```

Then select Word format when prompted.

### Example 3: High-Quality Translation with Review

```bash
uv run trans-novel translate book.epub
# Follow wizard, enable:
# - Polish (stronger model)
# - Final Review (quality check)
# - Bilingual output
```

## Next Steps

1. **Prepare only** (no translation): `uv run trans-novel prepare book.epub`
2. **Check status**: `uv run trans-novel status book.epub`
3. **Run final review**: `uv run trans-novel review book.epub`
4. **Resume interrupted translation**: Run the same command again

## See Also

- [Main README](../README.md)
- [Configuration Guide](configuration.md)
- [Translation Pipeline](pipeline.md)
