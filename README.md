# Agentic C / C++ Unit Tester

An agentic tool that analyzes C and C++ codebases, identifies test coverage gaps, and generates Google Test (gtest/gmock) code with an LLM-assisted workflow. It supports free functions, member methods, static methods, constructors, destructors, and private/protected members — with automatic boundary, equivalence partition, and MCDC test case planning.

---

## Features

- **C and C++ AST Analysis**: Parses `.c`, `.h`, `.cpp`, `.hpp`, `.cxx`, `.hh` files using `libclang`. Detects:
  - Free functions (C and C++)
  - Class member methods (public / protected / private)
  - Static methods and file-static C functions
  - Constructors and destructors
- **Optimized Test Strategy**: Uses an LLM as a "Test Architect" to identify a **minimal but robust** set of logic-aware scenarios, avoiding brute-force permutations while ensuring critical paths and boundaries are covered.
- **Legacy C & Static Function Support**: Automatically detects static functions. For legacy C, it supports testing file-static functions by optionally including the source file directly in the test suite.
- **Recursive Directory Scanning**: Batch process entire codebases with a single command to generate strategies for all source files.
- **Boundary & Equivalence Partition Test Planning**: Automatically generates test cases per parameter type:
  - `int`/`long`/`uint*` → INT_MIN/MAX, 0, ±1
  - `float`/`double` → numeric_limits, NaN, ±Inf, -0.0
  - Pointers → nullptr/NULL, dangling pointer note
  - `char*` / `std::string` → empty, very long, special characters
  - `bool` → true / false
- **MCDC Coverage Planning**: Estimates cyclomatic complexity and flags paths that need coverage.
- **Coverage Mapping**: Compares source functions against existing tests (regex-based) and identifies gaps.
- **Mock / Failure Injection Strategy**: Lists external dependencies and suggests failure injection scenarios.
- **Agentic Test Generation**: Uses OpenAI, Gemini, or locally-running Ollama to generate complete test bodies guided by the strategy.
- **Smart Template Rendering**:
  - `extern "C" { #include "..." }` automatically emitted for C source files.
  - `#include "source.c"` automatically emitted when testing static C functions.
  - `TEST_F(...)` fixture for public member methods; `TEST(...)` for static/free functions.
  - Private/protected methods wrapped in commented-out stubs with a testing approach note.

---

## Installation

### Prerequisites

- Python 3.8+
- `libclang` Python bindings (`pip install libclang`)
- C++ compiler (for verification): `g++`, `cmake`

### Setup

```bash
pip install -r requirements.txt
```

Configure your LLM provider via a `.env` file (copy from `.env.example`):

```env
# Choose one:
LLM_PROVIDER=ollama          # local Ollama (default / recommended)
# LLM_API_KEY=sk-...         # OpenAI
# LLM_API_KEY=AIza...        # Google Gemini

OLLAMA_MODEL=qwen2.5-coder:7b
```

> If no API key is provided and Ollama is not running, the tool falls back to a **Mock provider** that generates placeholder stubs.

---

## Usage

### 1. Analyze a Source File

Accepts both C (`.c`) and C++ (`.cpp`, `.cxx`) files.

```bash
python3 main.py analyze <source_file> [--test-file <existing_test_file>]
```

**Examples:**
```bash
# C source
python3 main.py analyze tests/fixtures/SimpleCalc.c

# C++ source with existing tests
python3 main.py analyze tests/fixtures/SimpleMath.cpp --test-file tests/fixtures/SimpleMathTest.cpp
```

### 2. Batch Scan a Directory

Recursively scan a directory for all C/C++ files and generate strategies.

```bash
python3 main.py scan <directory> [--output-dir strategies]
```

### 3. Generate Test Code

```bash
python3 main.py generate <strategy_file> <output_file>
```

**Example:**
```bash
python3 main.py generate tests/fixtures/SimpleMath_strategy.yaml tests/fixtures/SimpleMath_generated.cpp
```

---

## Test Strategy Details

Each function's strategy includes:

| Section | Content |
|---|---|
| **Unified Scenarios** | Logic-aware, optimized test cases identified by LLM |
| **Boundary Cases** | Per-parameter: INT_MIN/MAX, nullptr, empty string, NaN, etc. |
| **Equivalence Partitions** | Per-parameter: valid partition, invalid partition, zero/border |
| **MCDC Requirements** | Paths needed based on cyclomatic complexity |
| **Mocks Needed** | Dependencies flagged for failure injection |
| **Private/Protected** | Guidance: test via public API, friend class, or test subclass |
| **Static / Legacy C** | Automatic source inclusion for testing file-static functions |

---

## Project Structure

```
.
├── main.py                       # CLI entry point (analyze / scan / generate)
├── src/
│   ├── analyzer.py               # libclang AST analysis (C + C++)
│   ├── strategy.py               # Strategy planner with boundary/EP logic
│   ├── generator.py              # Jinja2 test code scaffolding
│   ├── llm_client.py             # OpenAI / Gemini / Ollama / Mock providers
│   └── test_parser.py            # Regex-based existing test discovery
├── templates/
│   ├── test_framework.j2         # C/C++ gtest/gmock test template
│   └── CMakeLists.txt.j2         # CMake build template
├── tests/
│   └── fixtures/
│       ├── SimpleCalc.c / .h     # C fixture (free functions, pointer, double)
│       ├── SimpleMath.cpp / .hpp # C++ fixture (public, static, protected, private)
│       └── SimpleMathTest.cpp    # Existing test reference
└── scripts/
    └── verify_pipeline.py        # Interactive CMake build + test + coverage runner
```

---

## Verification

Verify generated tests via the interactive pipeline script (requires `cmake`, `g++`, `lcov`):

```bash
# Install build tools if needed
sudo apt install cmake g++ lcov

# Run the pipeline
python3 scripts/verify_pipeline.py <source_file> <generated_test_file>
```

---

## LLM Provider Selection

| Priority | Provider | Trigger |
|---|---|---|
| 1 | Ollama | `LLM_PROVIDER=ollama` in `.env` |
| 2 | Gemini | `LLM_API_KEY` starts with `AIza` |
| 3 | OpenAI | `LLM_API_KEY` starts with `sk-` |
| 4 | Auto Ollama | Ollama detected running at `localhost:11434` |
| 5 | Mock | Fallback — generates placeholder stubs |
