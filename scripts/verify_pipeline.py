import os
import sys
import subprocess
import shutil
from jinja2 import Environment, FileSystemLoader

# Colors for output (using rich if available, fallback otherwise)
try:
    from rich.console import Console
    console = Console()
    def print_blue(msg): console.print(f"[bold blue]{msg}[/bold blue]")
    def print_green(msg): console.print(f"[bold green]{msg}[/bold green]")
    def print_red(msg): console.print(f"[bold red]{msg}[/bold red]")
    def print_yellow(msg): console.print(f"[bold yellow]{msg}[/bold yellow]")
except ImportError:
    def print_blue(msg): print(f"\033[94m{msg}\033[0m")
    def print_green(msg): print(f"\033[92m{msg}\033[0m")
    def print_red(msg): print(f"\033[91m{msg}\033[0m")
    def print_yellow(msg): print(f"\033[93m{msg}\033[0m")

def confirm(message):
    answer = input(f"{message} (y/n): ").lower()
    return answer == 'y'

def check_dependencies():
    deps = ["cmake", "make", "g++", "gcov"]
    missing = []
    for dep in deps:
        if shutil.which(dep) is None:
            missing.append(dep)
    
    if missing:
        print_red(f"Missing system dependencies: {', '.join(missing)}")
        print_yellow("Please install them using: sudo apt install " + " ".join(missing))
        return False
    return True

def run_command(cmd, cwd=None):
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print_red(f"Command failed: {cmd}")
        print_red(f"Error: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print_red("Usage: python3 verify_pipeline.py <source_file> <test_file>")
        sys.exit(1)

    if not check_dependencies():
        if not confirm("Some dependencies are missing. Continue anyway?"):
            sys.exit(1)

    source_file = os.path.abspath(sys.argv[1])
    test_file = os.path.abspath(sys.argv[2])
    project_name = os.path.basename(source_file).split('.')[0]
    
    print_blue("=== C++ Unit Test Verification Pipeline (Python) ===")

    # Stage 1: Generate CMakeLists.txt
    if confirm(f"Stage 1: Generate CMakeLists.txt for {project_name}?"):
        print_blue("Generating CMakeLists.txt...")
        try:
            env = Environment(loader=FileSystemLoader('templates'))
            template = env.get_template('CMakeLists.txt.j2')
            content = template.render(
                project_name=project_name,
                source_file=source_file,
                test_file=test_file
            )
            with open('CMakeLists.txt', 'w') as f:
                f.write(content)
            print_green("CMakeLists.txt generated.")
        except Exception as e:
            print_red(f"Failed to generate CMakeLists.txt: {e}")
            sys.exit(1)

    # Stage 2: Build
    if confirm("Stage 2: Build the project using CMake?"):
        print_blue("Building...")
        os.makedirs('build', exist_ok=True)
        if run_command("cmake ..", cwd='build') and run_command("make -j$(nproc)", cwd='build'):
            print_green("Build successful.")
        else:
            print_red("Build failed.")
            sys.exit(1)

    # Stage 3: Run Tests
    if confirm("Stage 3: Run the generated unit tests?"):
        print_blue("Running tests...")
        binary = os.path.join('build', f"{project_name}_test")
        if run_command(f"./{os.path.basename(binary)}", cwd='build'):
            print_green("Tests completed.")
        else:
            print_red("Tests failed.")

    # Stage 4: Coverage
    if confirm("Stage 4: Generate Coverage Report (gcov)?"):
        print_blue("Generating coverage...")
        if run_command("find . -name '*.gcno' -exec gcov {} +", cwd='build'):
            print_green("Gcov files generated in build/ directory.")
            
            if shutil.which("lcov"):
                print_blue("LCOV detected. Generating HTML report...")
                lcov_cmd = "lcov --capture --directory . --output-file coverage.info && " \
                           "lcov --remove coverage.info '/usr/*' '*/googletest/*' --output-file coverage.info && " \
                           "genhtml coverage.info --output-directory coverage_report"
                if run_command(lcov_cmd, cwd='build'):
                    print_green(f"HTML report available in build/coverage_report/index.html")
            else:
                print_yellow("lcov not found. Skipping HTML report.")
        else:
            print_red("Coverage generation failed.")

    print_blue("=== Pipeline Finished ===")

if __name__ == "__main__":
    main()
