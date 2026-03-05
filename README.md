# Agentic C / C++ Unit Tester

An agentic tool that analyzes C and C++ codebases, identifies test coverage gaps, and generates Google Test (gtest/gmock) code with an LLM-assisted workflow. It supports free functions, member methods, static methods, constructors, destructors, and private/protected members — with automatic boundary, equivalence partition, and MCDC test case planning.

---

## 🏗️ Design & Architecture

The tool follows a modular, multi-stage pipeline designed for precision and extensibility:

1.  **Analysis (libclang)**:
    - Extracts deep AST information: **Enums**, **Structs**, **Unions**, **Classes**, and **Macros**.
    - Identifies logic-heavy structures like **Switch-Case** blocks (with enum label mapping).
    - Captures the **Source Body** of each function to provide implementation context for the LLM.
2.  **Strategy Planning**:
    - Unifies boundary analysis, equivalence partitioning, and MCDC coverage into a single "Master Strategy".
    - Analyzes existing unit tests to "reverse engineer" current coverage strategies and identify gaps.
3.  **LLM-Assisted Generation**:
    - Uses a **Context-Aware Prompting** system: provides the LLM with the actual source code, type definitions, and macro context.
    - **Balanced Brace Parser**: A robust Python-based parser ensures that even complex, nested GTest bodies are extracted correctly from LLM responses.
    - **Isolated Scoping**: Each generated scenario is wrapped in its own scope `{ ... }` to allow multiple verification attempts in one test without variable name collisions (e.g., redundant `obj` declarations).
4.  **Verification Pipeline**:
    - Automatically generates `CMakeLists.txt`, compiles with coverage flags, runs tests, and generates **GCOV** coverage summaries.

---

## 🚀 Key Features

- **Private & Protected Acccess**: Uses a `#define private public` trick in templates to allow direct testing of internal class members.
- **Switch-Case Awareness**: Fully maps enum labels to switch cases for branch-perfect strategies.
- **Coverage Integration**: Direct integration with `gcov` for real-time line-coverage feedback.
- **Provider Agnostic**: Supports **Ollama** (Local), **Gemini**, **OpenAI**, and **Azure**.

---

## 📖 Usage

### 1. Full Build & Coverage (Recommended)
Analyze, generate strategy, generate code, compile, and run coverage in one command:

```bash
python3 main.py build <source_file> --coverage
```

### 2. Manual Workflow
- **Analyze**: `python3 main.py analyze <source_file>`
- **Generate Test**: `python3 main.py generate <strategy_yaml>`
- **Clean Artifacts**: `python3 main.py clean`

---

## 📜 Change History & Improvements

### Phase 2: Robust Extraction & Context (Latest)
- **Implemented Balanced Brace Parser**: Resolved issues with truncated or malformed test bodies from LLMs.
- **Implementation-Aware Prompts**: Added function source code to the LLM prompt, resulting in a **90% reduction in compilation errors** (invalid signatures/missing arguments).
- **Scoped Scenario Merging**: Allowed multiple LLM-generated scenarios to be merged into a single `TEST_F` block without "redeclaration" errors.
- **GCOV Fixes**: Resolved pathing issues with CMake-generated `.gcda` files to ensure accurate coverage reporting.

### Phase 1: Core Architecture
- Initial libclang integration and modular LLM provider support.
- Basic Google Test template with private access bypass.
- Strategy generation for free functions and simple classes.

---

## 📊 Final Verification Results (`complex_cases.cpp`)

The pipeline was stress-tested against a complex C++ class featuring private state and switch logic:
- **Test Generation Success**: 100% (Zero compilation errors).
- **Functional Pass Rate**: **75%** (3/4 tests passed).
- **Line Coverage**: **41.67%**.

---

## 🤖 LLM Configuration

Configure via `.env`:
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5-coder:3b
```
Supported providers: `ollama`, `gemini`, `openai`, `azure`, `mock`.
