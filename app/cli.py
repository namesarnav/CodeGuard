"""CLI tool for CodeGuard AI."""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from app.models.schemas import ReportFormat
from app.scanner.scanner import CodeScanner
from app.core.logging import setup_logging, get_logger

console = Console()
logger = get_logger(__name__)


@click.command()
@click.argument("target", type=click.Path(exists=False))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--format", "-f", type=click.Choice(["json", "sarif", "markdown", "html"]), default="json", help="Output format")
@click.option("--branch", "-b", type=str, help="Git branch to scan")
@click.option("--include", "-i", multiple=True, help="Include file patterns")
@click.option("--exclude", "-e", multiple=True, help="Exclude file patterns")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def scan(
    target: str,
    output: Optional[str],
    format: str,
    branch: Optional[str],
    include: tuple,
    exclude: tuple,
    verbose: bool,
) -> None:
    """
    Scan a repository or directory for vulnerabilities.

    TARGET can be:
    - A GitHub repository URL (e.g., https://github.com/user/repo)
    - A local directory path
    """
    setup_logging("DEBUG" if verbose else "INFO", "console")

    console.print(f"[bold blue]CodeGuard AI[/bold blue] - Scanning: {target}")

    scanner = CodeScanner()

    # Determine if target is URL or path
    is_url = target.startswith("http://") or target.startswith("https://")

    async def run_scan() -> None:
        """Run the scan asynchronously."""
        try:
            result = await scanner.scan(
                repository_url=target if is_url else None,
                repository_path=target if not is_url else None,
                branch=branch,
                include_patterns=list(include) if include else None,
                exclude_patterns=list(exclude) if exclude else None,
            )

            # Display summary
            display_summary(result)

            # Export results
            if output:
                export_result(result, output, format)
            else:
                # Print JSON to stdout
                print(json.dumps(result.model_dump(), indent=2, default=str))

        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            logger.exception("Scan failed")
            sys.exit(1)

    asyncio.run(run_scan())


def display_summary(result) -> None:
    """Display scan summary in a table."""
    table = Table(title="Scan Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Scan ID", result.scan_id)
    table.add_row("Status", result.status.value)
    table.add_row("Total Files", str(result.total_files))
    table.add_row("Scanned Files", str(result.scanned_files))
    table.add_row("Total Issues", str(len(result.issues)))

    if isinstance(result.summary, dict):
        by_severity = result.summary.get("by_severity", {})
        table.add_row("Critical", str(by_severity.get("critical", 0)))
        table.add_row("High", str(by_severity.get("high", 0)))
        table.add_row("Medium", str(by_severity.get("medium", 0)))
        table.add_row("Low", str(by_severity.get("low", 0)))
        table.add_row("Info", str(by_severity.get("info", 0)))

    console.print(table)


def export_result(result, output_path: str, format: str) -> None:
    """Export scan result to file."""
    output_file = Path(output_path)

    if format == "json":
        with open(output_file, "w") as f:
            json.dump(result.model_dump(), f, indent=2, default=str)
    elif format == "sarif":
        # TODO: Implement SARIF export
        console.print("[yellow]SARIF export not yet implemented[/yellow]")
    elif format == "markdown":
        # TODO: Implement Markdown export
        console.print("[yellow]Markdown export not yet implemented[/yellow]")
    elif format == "html":
        # TODO: Implement HTML export
        console.print("[yellow]HTML export not yet implemented[/yellow]")

    console.print(f"[green]Results exported to:[/green] {output_path}")


def main() -> None:
    """Main CLI entry point."""
    scan()


if __name__ == "__main__":
    main()

