import typer
import sys
import os
from src.analyzer import CodeAnalyzer
from src.test_parser import TestAnalyzer
from src.strategy import StrategyGenerator
from src.generator import TestGenerator
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

@app.command()
def analyze(source_file: str, test_file: str = None):
    """
    Analyzes a C++ source file and its corresponding test file to generate a test strategy.
    """
    # 1. Analyze Source
    console.print(f"[bold green]Analyzing Source:[/bold green] {source_file}")
    analyzer = CodeAnalyzer()
    try:
        source_funcs = analyzer.analyze_file(source_file)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Source file not found: {source_file}")
        raise typer.Exit(code=1)
    
    console.print(f"Found {len(source_funcs)} functions.")

    # 2. Analyze Tests
    existing_tests = []
    if test_file and os.path.exists(test_file):
        console.print(f"[bold green]Analyzing Tests:[/bold green] {test_file}")
        test_parser = TestAnalyzer()
        existing_tests = test_parser.analyze_test_file(test_file)
        console.print(f"Found {len(existing_tests)} existing tests.")
    else:
        console.print("[yellow]No test file provided or found. Assuming 0 coverage.[/yellow]")

    # 3. Generate Strategy
    generator = StrategyGenerator()
    strategy = generator.generate_strategy(source_funcs, existing_tests)
    
    # 4. Save Artifacts
    output_base = os.path.splitext(source_file)[0]
    yaml_path = f"{output_base}_strategy.yaml"
    
    generator.save_yaml(strategy, yaml_path)
    console.print(f"[bold blue]Strategy Saved (YAML):[/bold blue] {yaml_path}")
    
    md_path = f"{output_base}_strategy.md"
    generator.save_markdown(strategy, md_path)
    console.print(f"[bold blue]Strategy Saved (MD):[/bold blue] {md_path}")
    
    # Print Summary
    table = Table(title="Function Coverage Summary")
    table.add_column("Function", style="cyan")
    table.add_column("Covered?", style="magenta")
    table.add_column("Existing Tests", style="green")
    
    for func in strategy.functions:
        status = "[green]YES[/green]" if func.is_covered else "[red]NO[/red]"
        tests = "\n".join(func.existing_tests) if func.existing_tests else "-"
        table.add_row(func.name, status, tests)
        
    console.print(table)

@app.command()
def generate(strategy_file: str, output_file: str):
    """
    Generates C++ test code from a strategy file.
    """
    console.print(f"[bold green]Generating Tests from:[/bold green] {strategy_file}")
    generator = TestGenerator()
    try:
        generator.generate_test_code(strategy_file, output_file)
        console.print(f"[bold blue]Test Code Saved:[/bold blue] {output_file}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
