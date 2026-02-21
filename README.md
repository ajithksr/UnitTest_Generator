# Agentic C++ Unit Tester

This tool analyzes C++ codebases, identifies test coverage gaps, and generates Google Test (gtest) code using an LLM-assisted workflow. It calculates cyclomatic complexity (for MCDC) and identifies external dependencies for mocking.

## Features

- **AST Analysis**: Parses C++ files using `libclang` to extract functions, classes, and namespaces.
- **Coverage Mapping**: Compares source functions with existing tests (Regex-based).
- **MCDC Calculation**: Estimates cyclomatic complexity based on branching logic.
- **Strategy Generation**: Proposes test cases, including failure injection for dependencies.
- **Agentic Code Generation**: Uses OpenAI or Gemini to generate actual C++ test bodies based on the strategy.

## Installation

### Prerequisites

- Python 3.8+
- `libclang` (Ensure it's installed on your system)
- C++ Compiler (for verification)

### Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables (optional, for LLM support):
   Create a `.env` file in the root directory:
   ```env
   # To use Cloud APIs:
   LLM_API_KEY=your_api_key_here

   # To force a specific provider (e.g., ollama, openai, gemini):
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=qwen2.5-coder:7b
   ```
   *Note: If no API key is found, the tool will auto-detect if Ollama is running locally and use it.*

## usage

The tool is accessible via the `main.py` CLI.

### 1. Analyze a Source File

Analyze a C++ source file to identify functions and coverage gaps. This produces a strategy in both YAML and Markdown formats.

```bash
python3 main.py analyze <source_file> --test-file <existing_test_file>
```

**Example:**
```bash
python3 main.py analyze tests/fixtures/SimpleMath.cpp --test-file tests/fixtures/SimpleMathTest.cpp
```

**Outputs:**
- `SimpleMath_strategy.yaml`: Structured strategy for the generator.
- `SimpleMath_strategy.md`: Human-readable report with coverage indicators.

### 2. Generate Test Code

Generate C++ Google Test code from a strategy file.

```bash
python3 main.py generate <strategy_file> <output_file>
```

**Example:**
```bash
python3 main.py generate tests/fixtures/SimpleMath_strategy.yaml tests/fixtures/SimpleMath_generated.cpp
```

## Project Structure

- `main.py`: CLI entry point.
- `src/analyzer.py`: AST parsing and complexity analysis.
- `src/test_parser.py`: Existing test identification logic.
- `src/strategy.py`: Logic to map functions to tests and propose new cases.
- `src/generator.py`: Test code scaffolding using Jinja2.
- `src/llm_client.py`: Interface for OpenAI and Gemini APIs.
- `templates/`: Jinja2 templates for C++ code generation and CMakeLists.txt.
- `scripts/`: Helper scripts, including the verification pipeline.

## Verification

You can verify the generated tests using the interactive verification script.

### Prerequisites for Verification

The verification pipeline requires `cmake` and `g++`. If not installed:
```bash
sudo apt update
sudo apt install cmake g++ lcov
```

### Running the Pipeline

The script will guide you through Generating CMake, Building, Running Tests, and Coverage.

```bash
python3 scripts/verify_pipeline.py <source_file> <test_file>
```

**Example:**
```bash
python3 scripts/verify_pipeline.py tests/fixtures/SimpleMath.cpp tests/fixtures/SimpleMath_ollama_generated.cpp
```
