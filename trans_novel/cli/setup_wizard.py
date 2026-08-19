"""Interactive setup wizard for Wenyi Ketab translation configuration.

Guides users through language selection, model choice, and output preferences
with a step-by-step interactive interface.
"""

import os
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from trans_novel.config.languages import LANGUAGES, get_language

console = Console()


class SetupWizard:
    """Interactive setup wizard for translation configuration."""

    def __init__(self):
        """Initialize the wizard."""
        self.config = {}
        self.api_key = ""
        self.provider = ""
        self.target_language = ""
        self.output_formats = []
        self.polish_enabled = False
        self.review_enabled = False
        self.bilingual_enabled = False

    def run(self, epub_path: Optional[str] = None) -> dict:
        """Run the complete setup wizard.
        
        Args:
            epub_path: Optional path to EPUB file from command line
            
        Returns:
            Configuration dictionary
        """
        console.print(
            Panel(
                "[bold cyan]Welcome to Wenyi Ketab[/bold cyan]\n"
                "[dim]Interactive Setup Wizard[/dim]",
                border_style="cyan",
                padding=(1, 2),
            )
        )
        console.print()

        # Step 1: File path and source language detection
        self._step_1_file_and_source(epub_path)

        # Step 2: Target language selection
        self._step_2_target_language()

        # Step 3: API provider selection
        self._step_3_api_provider()

        # Step 4: Output format selection
        self._step_4_output_formats()

        # Step 5: Quality settings
        self._step_5_quality_settings()

        # Step 6: Review and confirm
        self._step_6_review_config()

        return self.config

    def _step_1_file_and_source(self, epub_path: Optional[str]) -> None:
        """Step 1: Get file path and detect source language."""
        console.print("[bold]Step 1/6: File and Source Language[/bold]")
        console.print()

        # Get file path
        if epub_path:
            file_path = epub_path
            console.print(f"📂 File path: [green]{file_path}[/green]")
        else:
            file_path = Prompt.ask("📂 Enter EPUB file path")

        # Validate file exists
        if not Path(file_path).exists():
            console.print(f"[red]✗ File not found: {file_path}[/red]")
            raise FileNotFoundError(f"EPUB file not found: {file_path}")

        self.config["epub_path"] = file_path
        console.print("[green]✓ File found[/green]")
        console.print()

    def _step_2_target_language(self) -> None:
        """Step 2: Select target language."""
        console.print("[bold]Step 2/6: Target Language[/bold]")
        console.print()

        # Display language options
        table = Table(title="Available Target Languages", show_header=False)
        table.add_column("#", style="cyan")
        table.add_column("Language", style="green")
        table.add_column("Native Name", style="dim")

        lang_list = list(LANGUAGES.items())
        for idx, (code, lang) in enumerate(lang_list, 1):
            table.add_row(str(idx), lang.name, lang.native_name)

        console.print(table)
        console.print()

        # Get user selection
        max_choice = len(lang_list)
        while True:
            try:
                choice = int(Prompt.ask("Select language", default="1"))
                if 1 <= choice <= max_choice:
                    selected_code = lang_list[choice - 1][0]
                    selected_lang = LANGUAGES[selected_code]
                    console.print(
                        f"[green]✓ Selected: {selected_lang.name} ({selected_lang.native_name})[/green]"
                    )
                    self.target_language = selected_code
                    self.config["target_language"] = selected_code
                    break
                else:
                    console.print(f"[red]Please enter a number between 1 and {max_choice}[/red]")
            except ValueError:
                console.print("[red]Please enter a valid number[/red]")

        console.print()

    def _step_3_api_provider(self) -> None:
        """Step 3: Select API provider and configure API key."""
        console.print("[bold]Step 3/6: API Provider and Key[/bold]")
        console.print()

        providers = {
            "1": "DeepSeek",
            "2": "OpenAI",
            "3": "OpenRouter",
            "4": "Google Gemini",
            "5": "Ollama",
            "6": "vLLM",
        }

        table = Table(title="Available LLM Providers", show_header=False)
        table.add_column("#", style="cyan")
        table.add_column("Provider", style="green")

        for num, provider in providers.items():
            table.add_row(num, provider)

        console.print(table)
        console.print()

        # Get provider selection
        while True:
            choice = Prompt.ask("Select provider", default="1")
            if choice in providers:
                self.provider = providers[choice].lower().replace(" ", "_")
                console.print(f"[green]✓ Selected: {providers[choice]}[/green]")
                break
            else:
                console.print("[red]Invalid choice[/red]")

        console.print()

        # Get API key
        env_var_name = self._get_api_key_env_var(providers[choice])
        env_key = os.environ.get(env_var_name)

        if env_key:
            console.print(f"🔑 Found {env_var_name} in environment")
            use_env = Confirm.ask("Use this API key?", default=True)
            if use_env:
                self.api_key = env_key
                console.print("[green]✓ Using environment API key[/green]")
            else:
                self.api_key = Prompt.ask("Enter API key", password=True)
        else:
            console.print(f"[yellow]⚠ {env_var_name} not found in environment[/yellow]")
            self.api_key = Prompt.ask("Enter API key", password=True)

        self.config["provider"] = self.provider
        self.config["api_key"] = self.api_key
        console.print()

    def _step_4_output_formats(self) -> None:
        """Step 4: Select output formats."""
        console.print("[bold]Step 4/6: Output Formats[/bold]")
        console.print()

        formats = ["EPUB", "TXT", "HTML", "Markdown", "Word (.docx)"]
        format_codes = ["epub", "txt", "html", "markdown", "word"]

        console.print("Select output formats (space-separated numbers or 'all'):")
        for idx, fmt in enumerate(formats, 1):
            console.print(f"  {idx}. {fmt}")

        console.print()

        # Get format selection
        while True:
            selection = Prompt.ask("Output formats", default="1").strip()

            if selection.lower() == "all":
                self.output_formats = format_codes
                console.print(f"[green]✓ Selected all formats[/green]")
                break
            else:
                try:
                    choices = [int(x.strip()) for x in selection.split()]
                    if all(1 <= c <= len(formats) for c in choices):
                        self.output_formats = [format_codes[c - 1] for c in choices]
                        selected = ", ".join([formats[c - 1] for c in choices])
                        console.print(f"[green]✓ Selected: {selected}[/green]")
                        break
                    else:
                        console.print(
                            f"[red]Please enter numbers between 1 and {len(formats)}[/red]"
                        )
                except ValueError:
                    console.print("[red]Please enter valid numbers[/red]")

        # Warn about Word format (additional dependency)
        if "word" in self.output_formats:
            console.print()
            console.print(
                "[yellow]⚠ Word format requires additional dependency (python-docx)[/yellow]"
            )
            console.print(
                "  Install with: [cyan]pip install python-docx[/cyan]"
            )

        self.config["output_formats"] = self.output_formats
        console.print()

    def _step_5_quality_settings(self) -> None:
        """Step 5: Configure quality settings."""
        console.print("[bold]Step 5/6: Quality Settings[/bold]")
        console.print()

        # Polish setting
        console.print("[dim]Polishing[/dim]: Improve translation quality with a stronger model")
        self.polish_enabled = Confirm.ask("Enable polishing?", default=False)
        if self.polish_enabled:
            console.print("[green]✓ Polishing enabled (may increase cost)[/green]")
        else:
            console.print("[dim]✗ Polishing disabled[/dim]")

        console.print()

        # Review setting
        console.print(
            "[dim]Final Review[/dim]: AI-driven whole-book consistency review"
        )
        self.review_enabled = Confirm.ask("Enable final review?", default=False)
        if self.review_enabled:
            console.print("[green]✓ Final review enabled (most expensive)[/green]")
        else:
            console.print("[dim]✗ Final review disabled[/dim]")

        console.print()

        # Bilingual output
        console.print(
            "[dim]Bilingual Output[/dim]: Source and translation side-by-side"
        )
        self.bilingual_enabled = Confirm.ask("Enable bilingual output?", default=True)
        if self.bilingual_enabled:
            console.print("[green]✓ Bilingual output enabled[/green]")
        else:
            console.print("[dim]✗ Bilingual output disabled[/dim]")

        self.config["polish"] = self.polish_enabled
        self.config["review"] = self.review_enabled
        self.config["bilingual"] = self.bilingual_enabled
        console.print()

    def _step_6_review_config(self) -> None:
        """Step 6: Review and confirm configuration."""
        console.print("[bold]Step 6/6: Confirm Configuration[/bold]")
        console.print()

        # Display configuration summary
        lang_config = get_language(self.target_language)
        table = Table(title="Configuration Summary", show_header=False)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("File", Path(self.config["epub_path"]).name)
        table.add_row("Target Language", f"{lang_config.name} ({lang_config.native_name})")
        table.add_row("LLM Provider", self.provider.replace("_", " ").title())
        table.add_row("Output Formats", ", ".join([f.upper() for f in self.output_formats]))
        table.add_row("Polishing", "✓ Enabled" if self.polish_enabled else "✗ Disabled")
        table.add_row("Final Review", "✓ Enabled" if self.review_enabled else "✗ Disabled")
        table.add_row(
            "Bilingual", "✓ Enabled" if self.bilingual_enabled else "✗ Disabled"
        )

        console.print(table)
        console.print()

        # Confirm
        if Confirm.ask("Is this configuration correct?", default=True):
            console.print("[green]✓ Configuration saved[/green]")
            console.print()
            console.print(
                Panel(
                    "[bold green]Setup Complete![/bold green]\n"
                    f"Starting translation: [cyan]{Path(self.config['epub_path']).name}[/cyan]",
                    border_style="green",
                )
            )
        else:
            console.print("[yellow]Setup cancelled[/yellow]")
            raise KeyboardInterrupt()

    @staticmethod
    def _get_api_key_env_var(provider: str) -> str:
        """Get environment variable name for API key.
        
        Args:
            provider: Provider name
            
        Returns:
            Environment variable name
        """
        env_map = {
            "DeepSeek": "DEEPSEEK_API_KEY",
            "OpenAI": "OPENAI_API_KEY",
            "OpenRouter": "OPENROUTER_API_KEY",
            "Google Gemini": "GOOGLE_API_KEY",
            "Ollama": "OLLAMA_API_KEY",
            "vLLM": "VLLM_API_KEY",
        }
        return env_map.get(provider, f"{provider.upper()}_API_KEY")
