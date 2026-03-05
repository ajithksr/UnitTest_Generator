import typer
import sys
import os
from src.analyzer import CodeAnalyzer
from src.test_parser import TestAnalyzer
from src.strategy import StrategyGenerator
from src.generator import TestGenerator
from src.llm_client import LLMClient
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
        analysis_results = analyzer.analyze_file(source_file)
        source_funcs = analysis_results["functions"]
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Source file not found: {source_file}")
        raise typer.Exit(code=1)
    
    console.print(f"Found {len(source_funcs)} functions, {len(analysis_results['types'])} types, and {len(analysis_results['macros'])} macros.")

    # 2. Analyze Tests
    existing_tests = []
    test_files = []
    if test_file:
        if os.path.isdir(test_file):
            for root, _, files in os.walk(test_file):
                for f in files:
                    if f.endswith((".cpp", ".cc", ".cxx", ".c")):
                        test_files.append(os.path.join(root, f))
        else:
            test_files.append(test_file)
    else:
        # Heuristic: look for tests in ./tests or same dir
        base_name = os.path.splitext(os.path.basename(source_file))[0]
        search_dirs = ["./tests", "./test", os.path.dirname(source_file)]
        for sd in search_dirs:
            if os.path.exists(sd):
                for f in os.listdir(sd):
                    if base_name.lower() in f.lower() and f.endswith((".cpp", ".cc", ".cxx", ".c")) and f != os.path.basename(source_file):
                        test_files.append(os.path.join(sd, f))

    if test_files:
        console.print(f"[bold green]Analyzing {len(test_files)} Test Files:[/bold green]")
        test_parser = TestAnalyzer()
        llm_client = LLMClient()
        for tf in test_files:
            console.print(f"  - {tf}")
            found_tests = test_parser.analyze_test_file(tf)
            test_parser.analyze_test_strategies(found_tests, llm_client)
            existing_tests.extend(found_tests)
        console.print(f"Found {len(existing_tests)} existing tests in total.")
    else:
        console.print("[yellow]No test files found. Assuming 0 coverage.[/yellow]")

    # 3. Generate Strategy
    llm_client = LLMClient()
    generator = StrategyGenerator()
    strategy = generator.generate_strategy(analysis_results, existing_tests, llm_client=llm_client)
    
    # 4. Save Artifacts
    strategy_dir = "./TestStrategy"
    if not os.path.exists(strategy_dir):
        os.makedirs(strategy_dir)
        
    output_base = os.path.splitext(os.path.basename(source_file))[0]
    yaml_path = os.path.join(strategy_dir, f"{output_base}_strategy.yaml")
    
    generator.save_yaml(strategy, yaml_path)
    console.print(f"[bold blue]Strategy Saved (YAML):[/bold blue] {yaml_path}")
    
    md_path = os.path.join(strategy_dir, f"{output_base}_strategy.md")
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
def scan(directory: str, output_dir: str = "TestStrategy"):
    """
    Recursively scans a directory for C/C++ files and generates test strategies for all.
    """
    if not os.path.isdir(directory):
        console.print(f"[bold red]Error:[/bold red] Not a directory: {directory}")
        raise typer.Exit(code=1)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    console.print(f"[bold green]Scanning Directory:[/bold green] {directory}")
    
    extensions = {".c", ".cpp", ".cxx", ".cc", ".h", ".hpp", ".hxx", ".hh"}
    files_to_process = []
    for root, _, files in os.walk(directory):
        for file in files:
            if os.path.splitext(file)[1].lower() in extensions:
                files_to_process.append(os.path.join(root, file))

    if not files_to_process:
        console.print("[yellow]No C/C++ files found.[/yellow]")
        return

    console.print(f"Found {len(files_to_process)} files.")

    analyzer = CodeAnalyzer()
    llm_client = LLMClient()
    strategy_gen = StrategyGenerator()

    for file_path in files_to_process:
        console.print(f"\n[bold green]Processing:[/bold green] {file_path}")
        try:
            analysis_results = analyzer.analyze_file(file_path)
            source_funcs = analysis_results["functions"]
            if not source_funcs:
                console.print(f"[yellow]No functions found in {file_path}. Skipping.[/yellow]")
                continue

            # For batch scan, we don't look for specific test files yet unless they follow a pattern
            # Future: pattern match file.cpp -> file_test.cpp
            strategy = strategy_gen.generate_strategy(analysis_results, [], llm_client=llm_client)
            
            rel_path = os.path.relpath(file_path, directory)
            output_base = os.path.join(output_dir, rel_path.replace(os.sep, "_"))
            
            yaml_path = f"{output_base}_strategy.yaml"
            strategy_gen.save_yaml(strategy, yaml_path)
            
            md_path = f"{output_base}_strategy.md"
            strategy_gen.save_markdown(strategy, md_path)
            
            console.print(f"Strategy saved to {output_dir}")
        except Exception as e:
            console.print(f"[bold red]Error processing {file_path}:[/bold red] {e}")

@app.command()
def generate(strategy_file: str, output_file: str = None):
    """
    Generates C++ test code from a strategy file.
    """
    if not output_file:
        ut_dir = "./GeneratedUT"
        if not os.path.exists(ut_dir):
            os.makedirs(ut_dir)
        
        # Derive name from strategy file
        base = os.path.basename(strategy_file).replace("_strategy.yaml", "_test.cpp")
        output_file = os.path.join(ut_dir, base)

    console.print(f"[bold green]Generating Tests from:[/bold green] {strategy_file}")
    generator = TestGenerator()
    try:
        generator.generate_test_code(strategy_file, output_file)
        console.print(f"[bold blue]Test Code Saved:[/bold blue] {output_file}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def build(source_file: str, test_file: str = None, run: bool = True, coverage: bool = False):
    """
    Generates CMakeLists.txt, builds the test, and optionally runs it with coverage.
    """
    if not test_file:
        # Heuristic to find generated test if not provided
        base = os.path.splitext(os.path.basename(source_file))[0]
        test_file = f"./GeneratedUT/{base}_test.cpp"
    
    if not os.path.exists(test_file):
        console.print(f"[bold red]Error:[/bold red] Test file not found: {test_file}")
        raise typer.Exit(code=1)

    console.print(f"[bold green]Generating CMake for:[/bold green] {source_file} and {test_file}")
    generator = TestGenerator()
    generator.generate_cmake(source_file, test_file)

    # Build process
    build_dir = "./build"
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    
    import subprocess
    
    console.print("[bold cyan]Running CMake...[/bold cyan]")
    ret = subprocess.call(["cmake", ".."], cwd=build_dir)
    if ret != 0:
        console.print("[bold red]CMake failed.[/bold red]")
        raise typer.Exit(code=1)
    
    console.print("[bold cyan]Running Make...[/bold cyan]")
    ret = subprocess.call(["make"], cwd=build_dir)
    if ret != 0:
        console.print("[bold red]Make failed.[/bold red]")
        raise typer.Exit(code=1)

    if run:
        # Identify the executable name from project name
        proj_name = os.path.splitext(os.path.basename(source_file))[0]
        exe_path = f"./{proj_name}_test"
        
        console.print(f"[bold green]Running Tests:[/bold green] {exe_path}")
        ret = subprocess.call([exe_path], cwd=build_dir)
        
        if coverage:
            console.print("[bold green]Generating Coverage (gcov)...[/bold green]")
            # Direct way: run gcov on the .gcda file which CMake puts in build/CMakeFiles/PROJ_test.dir/
            # The gcda name might be "source.cpp.gcda" instead of just "source.gcda"
            gcda_file = os.path.join(build_dir, "CMakeFiles", f"{proj_name}_test.dir", f"{source_file}.gcda")
            if not os.path.exists(gcda_file):
                # Try fallback: just the basename
                 gcda_file = os.path.join(build_dir, "CMakeFiles", f"{proj_name}_test.dir", f"{os.path.basename(source_file)}.gcda")

            if os.path.exists(gcda_file):
                subprocess.call(["gcov", gcda_file], cwd=os.getcwd())
            else:
                console.print(f"[bold red][WARN] GCDA file not found at {gcda_file}. Coverage might fail.[/bold red]")
                # Last resort fallback: original way
                subprocess.call(["gcov", "-o", f"CMakeFiles/{proj_name}_test.dir/", os.path.abspath(source_file)], cwd=build_dir)
            
            # Find the generated .gcov file in the current working directory
            gcov_file = os.path.basename(source_file) + ".gcov"
            if os.path.exists(gcov_file):
                console.print(f"[bold blue]Coverage detail saved to:[/bold blue] {os.path.abspath(gcov_file)}")
                # Print a small summary if possible
                with open(gcov_file, "r") as f:
                    lines = f.readlines()
                    hits = 0
                    total = 0
                    for line in lines:
                        if ":" in line:
                            parts = line.split(":")
                            count = parts[0].strip()
                            if count.isdigit():
                                hits += 1
                                total += 1
                            elif count == "#####": # Not covered
                                total += 1
                    if total > 0:
                        percent = (hits / total) * 100
                        console.print(f"[bold yellow]Estimated Line Coverage: {percent:.2f}% ({hits}/{total} lines)[/bold yellow]")
            else:
                console.print("[yellow]Could not find .gcov file. Ensure the executable was executed and linked correctly.[/yellow]")

@app.command()
def clean():
    """Cleans build and strategy artifacts."""
    import shutil
    dirs = ["./build", "./TestStrategy", "./GeneratedUT"]
    for d in dirs:
        if os.path.exists(d):
            console.print(f"Removing {d}...")
            shutil.rmtree(d)
    if os.path.exists("CMakeLists.txt"):
        os.remove("CMakeLists.txt")
    console.print("[bold green]Cleanup complete.[/bold green]")

if __name__ == "__main__":
    app()
