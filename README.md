# Agentic C / C++ Unit Tester

An agentic tool that analyzes C and C++ codebases, identifies test coverage gaps, and generates Google Test (gtest/gmock) code with an LLM-assisted workflow. It supports free functions, member methods, static methods, constructors, destructors, and private/protected members — with automatic boundary, equivalence partition, and MCDC test case planning.

---

## 🚀 Key Enhancements

- **Modular LLM Client Architecture**: Decoupled providers for **Ollama**, **Gemini**, **OpenAI**, and **Mock** (for testing/verification). Select your backend via `LLM_PROVIDER`.
- **Rich Code Analysis**: Full-depth extraction of **Enums**, **Structs**, **Unions**, **Classes**, and **#define macros**.
- **Switch-Case Awareness**: Recursively identifies switch-case values (including enum labels) to ensure comprehensive branch coverage strategies.
- **Private & Protected Testing**: Implements a macro-based access bypass (`#define private public`) in generated tests, enabling direct verification of internal state and private methods.
- **Existing Test Strategy Analysis**: Uses LLM to "reverse engineer" the strategy behind existing unit tests, aggregating findings from multiple test files and mapping them back to source functions.
- **Smart Strategy Comparison**: Compares needed technical strategies (boundaries, MCDC, mocks) against already covered strategies to highlight missing gaps.
- **Automated Directory Organization**:
  - 📝 **Test Strategies**: Automatically saved to `./TestStrategy/` (YAML and Markdown).
  - 🛠️ **Generated Tests**: New test files are automatically saved to `./GeneratedUT/`.

---

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- `libclang` Python bindings (`pip install libclang`)
- C++ compiler (for verification): `g++`, `cmake`

### Setup

```bash
pip install -r requirements.txt
```

Configure your LLM provider via a `.env` file:

```env
LLM_PROVIDER=gemini          # ollama, gemini, openai, mock
LLM_API_KEY=AIza...          # Required for Gemini/OpenAI
OLLAMA_MODEL=qwen2.5-coder:7b # Required for Ollama
```

---

## 📖 Usage

### 1. Analyze a Source File
Analyzes a source file, identifies coverage gaps (scanning the workspace for tests), and generates a strategy.

```bash
python3 main.py analyze <source_file>
```

- **Output**: `./TestStrategy/<source>_strategy.md` & `.yaml`

### 2. Batch Scan a Directory
Recursively scan a directory for all C/C++ files and generate strategies.

```bash
python3 main.py scan <directory>
```

### 3. Generate Test Code
Generates C++ Google Test code from a strategy file.

```bash
python3 main.py generate <strategy_file>
```

- **Output**: `./GeneratedUT/<source>_test.cpp`

---

## 🏗️ Project Structure

```
.
├── main.py                       # CLI entry point
├── src/
│   ├── analyzer.py               # Rich AST analysis (Types, Macros, Switch-cases)
│   ├── strategy.py               # Strategy planner & existing test aggregator
│   ├── generator.py              # Test code generation engine
│   ├── llm_client.py             # LLM Factory (Provider selection)
│   ├── test_parser.py            # Test body extractor & LLM strategy analyzer
│   └── llm/                      # Modular LLM Providers
│       ├── base.py, ollama.py, gemini.py, openai.py, mock.py
├── templates/
│   └── test_framework.j2         # GTest template with private access bypass
├── TestStrategy/                 # Default output for strategies
└── GeneratedUT/                  # Default output for generated tests
```

---

## 🧪 Verification

Verify generated tests via the interactive pipeline script:

```bash
python3 scripts/verify_pipeline.py <source_file> <generated_test_file>
```

---

## 🤖 LLM Providers

| Provider | Requirement | Description |
|---|---|---|
| **Ollama** | `LLM_PROVIDER=ollama` | Local LLM execution (Privacy-focused) |
| **Gemini** | `LLM_PROVIDER=gemini` | High-performance reasoning via Google AI |
| **OpenAI** | `LLM_PROVIDER=openai` | Industry-standard Reasoning |
| **Mock** | `LLM_PROVIDER=mock` | Zero-cost verification of tool logic |
