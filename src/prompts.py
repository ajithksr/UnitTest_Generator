"""
LLM Prompts for C++ Unit Test Generator.
"""

SYSTEM_CONTEXT = (
    "You are an expert C and C++ unit test generator using Google Test (gtest/gmock). "
    "You handle free functions (C and C++), static functions, class member methods "
    "(including private and protected), constructors, and destructors. "
    "Always include boundary, equivalence partition, and MCDC test cases."
)

STRATEGY_ANALYSIS_PROMPT = """
You are an expert Test Architect. Analyze the following {language} function and produce a UNIFIED, OPTIMIZED set of high-quality test scenarios.

### Function details:
Language: {language}
Function: {signature}
Return Type: {return_type}
Implementation:
```cpp
{body_code}
```

### Technical Requirements to Integrate:
These are the technical baseline requirements (Boundary values, Equivalence Partitions, and Mocks) you MUST consider and integrate into your logic analysis:

**Contextual Types (Enums/Structs/Classes):**
{types_txt}

**Macros (#define):**
{macros_txt}

**Boundary Conditions:**
{boundary_txt}

**Equivalence Partitions:**
{ep_txt}

**External Dependencies / Mocks:**
{mocks_txt}

**Logical Paths (MCDC):**
{mcdc_txt}

### Objective:
Identify a **minimal but robust** set of test scenarios. Do NOT brute-force every possible permutation. Instead, focus on:
1. **Critical Logic Paths:** Covered by the implementation logic.
2. **Risk-Based Scenarios:** Where the code is most likely to fail (e.g., edge cases identified in boundaries).
3. **Internal Logic Flow:** Map the technical boundaries to specific behavioral expectations (e.g., "Verify add(0, 0) returns 0" instead of just "Boundary: zero").
4. **Data Context:** Use the provided Enums and Macros to identify specific values for switch cases or return checks.

Ensure ALL identified boundary values and partitions are addressed, but consolidate them where it makes sense (e.g., one scenario can cover multiple boundaries if logical).

Format: Output ONLY a JSON list of strings.
Example: ["Check result when value is exactly 0", "Verify error when buffer is full", "Mock database failure during record insertion"]
"""

TEST_BODY_PROMPT = """
Generate the body of a {language} Google Test (gtest) for the following function:

## Target Function
Signature: {signature}
Return Type: {return_type}
Kind: {kind}
Language: {language}

## Implementation Logic (for assertion context)
```cpp
{body_code}
```

## Test Scenarios to Implement (MASTER LIST)
{cases_txt}
{baseline_info}

## Mocks Needed
{mocks_needed}

## Contextual Information
**Types:**
{types_txt}

**Macros:**
{macros_txt}

{fixture_context}

Output **ONLY** the C++ code that goes **INSIDE** the curly braces of a Google Test.
**CRITICAL: Do NOT output the `TEST(...) {{` line, DO NOT output the closing `}}`, and DO NOT output any `#include` statements.**
**CRITICAL: Use the provided `obj` instance (which is of the class type being tested) to access public, private, and protected methods. Do NOT redeclare `ComplexProcessor obj;` or any other instance of the class inside the test body. (Wait for it: No `ComplexProcessor obj;` inside the block!)**
**CRITICAL: Always prefix member function calls with `obj.` (e.g., `obj.processString(...)`). Do NOT call them as free functions.**
**CRITICAL: Do NOT hallucinate `mock*` prefix methods (e.g., `mockPrivateLogic`).**
**CRITICAL: Do NOT attempt "mock setup" by calling functions with zero or incorrect arguments (e.g. `obj.protectedAction()`). This is real code, not a mock object.**
**CRITICAL: Every function call MUST match its signature exactly. For example, if `protectedAction` takes an `int`, you MUST pass an `int`.**
**CRITICAL: Use the provided macros (e.g., `STATUS_SUCCESS`, `STATUS_ERROR`) or logical values from the implementation for expectations. Do NOT assume `0` or other arbitrary values unless the code explicitly returns them.**
**CRITICAL: If the Return Type is `void`, do NOT wrap the function call in `EXPECT_EQ`, `ASSERT_EQ`, or any comparison macro. Just call it.**
**CRITICAL: If you use `INT_MIN` or `INT_MAX`, assume `<climits>` is available.**
Ensure all scenarios listed above are covered by appropriate EXPECT_* or ASSERT_* assertions.
If the method is private or protected, assume `#define private public` trick is used to grant access—call them directly on the object.
"""

TEST_MAPPING_PROMPT = """
Given the following list of functions and existing unit tests, map each test to the function it most likely covers.
Functions:
{functions}

Tests:
{tests}

Output ONLY a JSON object mapping Test Full Name to Function Name.
Example: {{"Processor_Global.VersionCheck": "getVersion"}}
"""

EXISTING_TEST_STRATEGY_PROMPT = """
Analyze the following Google Test (gtest) body and describe the testing strategy in a few concise bullet points.
What is it verifying? What edge cases or logic is it covering?

Test Name: {test_name}
Test Body:
```cpp
{test_body}
```

Output ONLY a JSON list of strings.
Example: ["Verify handling of zero input", "Check for buffer overflow with long string", "Mock database connection failure"]
"""
