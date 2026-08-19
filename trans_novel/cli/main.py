"""Main CLI entry point for Wenyi Ketab."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from trans_novel.cli.setup_wizard import SetupWizard
from trans_novel.cli.config_schema import TranslationConfig

app = typer.Typer(
    name="trans-novel",
    help="AI-powered multilingual book translation with quality review",
)
console = Console()


@app.command()
def translate(
    epub_path: Optional[str] = typer.Argument(
        None,
        help="Path to EPUB file",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Target language code (fa, en, es, fr, de, ru)",
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="LLM provider (deepseek, openai, openrouter, google_gemini, ollama, vllm)",
    ),
    polish: Optional[bool] = typer.Option(
        None,
        "--polish/--no-polish",
        help="Enable translation polishing",
    ),
    review: Optional[bool] = typer.Option(
        None,
        "--review/--no-review",
        help="Enable final AI review",
    ),
    bilingual: Optional[bool] = typer.Option(
        None,
        "--bilingual/--no-bilingual",
        help="Generate bilingual output",
    ),
    wizard: bool = typer.Option(
        True,
        "--wizard/--no-wizard",
        help="Use interactive setup wizard",
    ),
) -> None:
    """Translate an EPUB file to target language.
    
    Use interactive setup wizard by default, or provide options directly.
    """
    try:
        # Use wizard if no language specified and wizard enabled
        if wizard and not language:
            wizard_instance = SetupWizard()
            config_dict = wizard_instance.run(epub_path)
        else:
            # Validate required parameters
            if not epub_path or not language:
                console.print(
                    "[red]Error: Missing required parameters[/red]\n"
                    "Use --wizard or provide --language and EPUB path"
                )
                raise typer.Exit(code=1)

            config_dict = {
                "epub_path": epub_path,
                "target_language": language,
                "provider": provider or "deepseek",
                "polish": polish if polish is not None else False,
                "review": review if review is not None else False,
                "bilingual": bilingual if bilingual is not None else True,
            }

        # Validate configuration
        try:
            config = TranslationConfig(**config_dict)
            console.print(
                "\n[green]✓ Configuration validated successfully[/green]\n"
            )
        except ValueError as e:
            console.print(f"[red]Configuration error: {e}[/red]")
            raise typer.Exit(code=1)

        # TODO: Start translation pipeline
        console.print("[cyan]Starting translation...[/cyan]")
        console.print(f"Configuration: {config.model_dump_json(indent=2)}")

    except KeyboardInterrupt:
        console.print("\n[yellow]Setup cancelled[/yellow]")
        raise typer.Exit(code=0)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def status(
    epub_path: str = typer.Argument(..., help="Path to EPUB file"),
) -> None:
    """Check translation status."""
    console.print(f"[cyan]Checking status for: {epub_path}[/cyan]")
    # TODO: Implement status checking
    console.print("[yellow]Status feature coming soon[/yellow]")


@app.command()
def prepare(
    epub_path: str = typer.Argument(..., help="Path to EPUB file"),
) -> None:
    """Prepare book for translation (parse, analyze, prescan)."""
    console.print(f"[cyan]Preparing: {epub_path}[/cyan]")
    # TODO: Implement preparation
    console.print("[yellow]Prepare feature coming soon[/yellow]")


@app.command()
def review(
    epub_path: str = typer.Argument(..., help="Path to EPUB file"),
) -> None:
    """Run independent final review against completed translation."""
    console.print(f"[cyan]Reviewing: {epub_path}[/cyan]")
    # TODO: Implement review
    console.print("[yellow]Review feature coming soon[/yellow]")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
