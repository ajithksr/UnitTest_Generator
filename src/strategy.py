import yaml
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import os

from .prompts import TEST_MAPPING_PROMPT

# ---------------------------------------------------------------------------
# Boundary & Equivalence Partition helpers
# ---------------------------------------------------------------------------

# Numeric types we know boundaries for
_INT_TYPES = {"int", "long", "short", "char", "int8_t", "int16_t", "int32_t", "int64_t",
              "uint8_t", "uint16_t", "uint32_t", "uint64_t", "size_t", "unsigned int",
              "unsigned long", "unsigned char"}
_FLOAT_TYPES = {"float", "double", "long double"}
_STRING_TYPES = {"char *", "const char *", "std::string", "const std::string &",
                 "std::string_view"}
_POINTER_TYPES_SUFFIX = ("*", "* const", "const *")
_BOOL_TYPES = {"bool"}


def _clean_type(type_str: str) -> str:
    """Helper to strip const, volatile, and reference decorations for lookup."""
    import re
    # Remove const, volatile, and & / &&
    cleaned = re.sub(r'\b(const|volatile)\b', '', type_str)
    cleaned = re.sub(r'&\s*&?', '', cleaned)
    # Remove extra spaces
    return " ".join(cleaned.split()).lower()


def _boundary_cases_for_type(param_name: str, type_str: str) -> List[str]:
    """Return boundary-condition test case descriptions for a single parameter."""
    t = type_str.strip().lower()
    bare = _clean_type(t)
    cases = []

    if bare in _INT_TYPES or any(bare.startswith(it) for it in _INT_TYPES):
        cases.append(f"Boundary [{param_name}]: INT_MIN / INT_MAX (overflow edge)")
        cases.append(f"Boundary [{param_name}]: value = 0 (zero boundary)")
        cases.append(f"Boundary [{param_name}]: value = -1 and +1 (near-zero)")
    elif bare in _FLOAT_TYPES:
        cases.append(f"Boundary [{param_name}]: std::numeric_limits<{bare}>::max()")
        cases.append(f"Boundary [{param_name}]: std::numeric_limits<{bare}>::min() (smallest positive)")
        cases.append(f"Boundary [{param_name}]: 0.0 and -0.0")
        cases.append(f"Boundary [{param_name}]: NaN, +Inf, -Inf")
    elif any(t.endswith(sfx) for sfx in _POINTER_TYPES_SUFFIX) or t.endswith("*"):
        cases.append(f"Boundary [{param_name}]: nullptr / NULL (null pointer)")
        cases.append(f"Boundary [{param_name}]: dangling or uninitialized pointer (UB check)")
    elif bare in {s.lower().replace("const ", "").replace(" &", "") for s in _STRING_TYPES}:
        cases.append(f"Boundary [{param_name}]: empty string \"\"")
        cases.append(f"Boundary [{param_name}]: very long string (> 256 chars)")
        cases.append(f"Boundary [{param_name}]: string with special chars / null byte")
    elif bare == "bool":
        cases.append(f"Boundary [{param_name}]: true")
        cases.append(f"Boundary [{param_name}]: false")

    return cases


def _equivalence_cases_for_type(param_name: str, type_str: str) -> List[str]:
    """Return equivalence partition test case descriptions for a single parameter."""
    t = type_str.strip().lower()
    bare = _clean_type(t)
    cases = []

    if bare in _INT_TYPES or any(bare.startswith(it) for it in _INT_TYPES):
        cases.append(f"EP [{param_name}]: Typical positive value (valid partition)")
        cases.append(f"EP [{param_name}]: Typical negative value (if signed, valid partition)")
        cases.append(f"EP [{param_name}]: Zero (border between partitions)")
        cases.append(f"EP [{param_name}]: Out-of-range / invalid value (invalid partition)")
    elif bare in _FLOAT_TYPES:
        cases.append(f"EP [{param_name}]: Typical positive real (valid partition)")
        cases.append(f"EP [{param_name}]: Typical negative real (valid partition if signed)")
        cases.append(f"EP [{param_name}]: Very small denormalized value")
    elif any(t.endswith(sfx) for sfx in _POINTER_TYPES_SUFFIX) or t.endswith("*"):
        cases.append(f"EP [{param_name}]: Valid, non-null pointer (valid partition)")
        cases.append(f"EP [{param_name}]: nullptr (invalid partition)")
    elif bare in {s.lower().replace("const ", "").replace(" &", "") for s in _STRING_TYPES}:
        cases.append(f"EP [{param_name}]: Normal non-empty string (valid partition)")
        cases.append(f"EP [{param_name}]: Empty string (boundary / invalid partition)")
        cases.append(f"EP [{param_name}]: Whitespace-only string (edge partition)")

    return cases


def _generate_boundary_ep_cases(parameters: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """Return (boundary_cases, ep_cases) for all function parameters."""
    boundary = []
    ep = []
    for param in parameters:
        pname = param.get("name") or "param"
        ptype = param.get("type", "")
        boundary.extend(_boundary_cases_for_type(pname, ptype))
        ep.extend(_equivalence_cases_for_type(pname, ptype))

    # Fallback for parameterless functions
    if not parameters:
        boundary.append("Boundary: no parameters — verify pure side-effects / return value")
        ep.append("EP: call with implicit state valid vs. invalid")

    return boundary, ep


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class FunctionStrategy:
    name: str
    signature: str
    file: str
    line: int
    return_type: str
    is_covered: bool
    existing_tests: List[str]
    existing_test_details: List[Dict[str, Any]] = field(default_factory=list) # Includes body and strategy
    class_name: Optional[str] = None
    namespace: Optional[str] = None
    language: str = "C++"
    kind: str = "free_function"          # constructor / destructor / static_method / private_method / …
    is_static: bool = False
    access_specifier: str = "none"       # public / private / protected / none
    suggested_test_cases: List[str] = field(default_factory=list)  # This will hold the UNIFIED scenarios
    technical_baseline: Dict[str, List[str]] = field(default_factory=dict)  # Hidden baseline for reference
    mocks_needed: List[str] = field(default_factory=list)
    mcdc_cases: List[str] = field(default_factory=list)
    switch_cases: List[Dict[str, Any]] = field(default_factory=list)
    body_code: str = ""


@dataclass
class FileStrategy:
    source_file: str
    functions: List[FunctionStrategy] = field(default_factory=list)
    types: List[Dict[str, Any]] = field(default_factory=list)
    macros: List[Dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Strategy generator
# ---------------------------------------------------------------------------

class StrategyGenerator:
    def __init__(self):
        pass

    def generate_strategy(
        self,
        analysis_results: Dict[str, Any],
        existing_tests: List[Dict[str, Any]],
        llm_client: Optional[Any] = None,
    ) -> FileStrategy:
        """
        Compares analyzed functions with existing tests and generates a rich strategy,
        including boundary and equivalence partition test cases.
        """
        file_functions = analysis_results.get("functions", [])
        source_file = analysis_results.get("file", "unknown")
        
        # Sort functions by name as requested
        file_functions = sorted(file_functions, key=lambda x: x["name"])
        
        strategy = FileStrategy(
            source_file=source_file,
            types=analysis_results.get("types", []),
            macros=analysis_results.get("macros", [])
        )

        unassigned_tests = existing_tests[:]
        function_mappings = {} # func_name -> list of tests

        # 1. First Pass: Simple Name-Based Matching
        for func in file_functions:
            func_name = func["name"]
            class_name = func.get("class_name")
            namespace = func.get("namespace")
            
            matched_for_this_func = []
            remaining_unassigned = []
            
            for test in unassigned_tests:
                suite_matches = False
                if class_name and class_name.lower() in test["suite_name"].lower():
                    suite_matches = True
                elif namespace and namespace.lower() in test["suite_name"].lower():
                    suite_matches = True

                name_matches = func_name.lower() in test["test_name"].lower()

                if suite_matches and name_matches:
                    matched_for_this_func.append(test)
                else:
                    remaining_unassigned.append(test)
            
            function_mappings[func_name] = matched_for_this_func
            unassigned_tests = remaining_unassigned

        # 2. Second Pass: LLM-Based Matching for remaining unassigned tests
        if llm_client and unassigned_tests and file_functions:
            print(f"[INFO] Attempting to map {len(unassigned_tests)} unassigned tests using LLM...")
            # Prepare a list of function names and signatures
            func_list = [f"{f['name']} ({f['signature']})" for f in file_functions]
            test_list = [f"{t['full_name']} (Body: {t['body'] if len(t['body']) < 200 else t['body'][:200] + '...'})" for t in unassigned_tests]
            
            mapping_prompt = TEST_MAPPING_PROMPT.format(
                functions=json.dumps(func_list, indent=2),
                tests=json.dumps(test_list, indent=2)
            )
            try:
                response = llm_client.provider.generate_code(mapping_prompt)
                import re
                json_match = re.search(r'\{.*\}', response.strip(), re.DOTALL)
                if json_match:
                    llm_mapping = json.loads(json_match.group(0))
                    for test_fullname, func_target in llm_mapping.items():
                        # Find the test and function
                        target_test = next((t for t in existing_tests if t["full_name"] == test_fullname), None)
                        if target_test and func_target in function_mappings:
                            if target_test not in function_mappings[func_target]:
                                function_mappings[func_target].append(target_test)
                                print(f"[INFO] LLM Mapped {test_fullname} -> {func_target}")
            except Exception as e:
                print(f"[WARN] LLM Test Mapping failed: {e}")

        # 3. Build Final Function Strategy Objects
        for func in file_functions:
            func_name = func["name"]
            class_name = func.get("class_name")
            namespace = func.get("namespace")
            language = func.get("language", "C++")
            kind = func.get("kind", "free_function")
            is_static = func.get("is_static", False)
            access_specifier = func.get("access_specifier", "none")
            parameters = func.get("parameters", [])
            return_type = func.get("return_type", "void")
            switch_cases = func.get("switch_cases", [])

            matched_tests = function_mappings.get(func_name, [])
            matched_test_names = [t["full_name"] for t in matched_tests]
            is_covered = len(matched_tests) > 0

            # ------------------------------------------------------------------
            # Technical Requirements Baseline (Internal Context)
            # ------------------------------------------------------------------
            boundary_cases, ep_cases = _generate_boundary_ep_cases(parameters)
            
            if switch_cases:
                for sw in switch_cases:
                    for case in sw.get("cases", []):
                        boundary_cases.append(f"Switch Case: {case}")

            mocks = []
            for dep in func.get("dependencies", []):
                if dep:
                    mocks.append(f"Mock for {dep}")

            complexity = func.get("complexity", 1)
            mcdc_cases = []
            if complexity > 1:
                mcdc_cases.append(
                    f"MCDC: Complexity is {complexity}. Ensure all {complexity} logical decision branches are covered."
                )

            technical_context = {
                "boundary_cases": boundary_cases,
                "equivalence_partition_cases": ep_cases,
                "mocks_needed": mocks,
                "mcdc_cases": mcdc_cases,
                "types": strategy.types,
                "macros": strategy.macros
            }

            # ------------------------------------------------------------------
            # UNIFIED LLM Logic-Aware Test Strategy
            # ------------------------------------------------------------------
            suggested_cases = []
            body_code = func.get("body_code")
            if llm_client and body_code:
                # Add existing test strategies for comparison
                existing_strat_summary = []
                for t in matched_tests:
                    if t.get("strategy"):
                        existing_strat_summary.extend(t["strategy"])
                
                technical_context["existing_strategies"] = existing_strat_summary

                print(f"[INFO] Identifying unified master strategy for {func_name} using LLM...")
                llm_cases = llm_client.identify_test_strategy(
                    func["signature"], body_code, language, technical_context
                )
                if llm_cases:
                    suggested_cases.extend(llm_cases)
            
            if not suggested_cases:
                if not is_covered:
                    suggested_cases.extend(boundary_cases)
                    suggested_cases.extend(ep_cases)
                    suggested_cases.extend(mcdc_cases)
                    if not suggested_cases:
                        suggested_cases = ["Positive Case", "Negative Case"]
                else:
                    suggested_cases = ["Additional Verification"]

            if access_specifier in ("private", "protected"):
                suggested_cases.append(f"NOTE: Test via public API or test subclass (Access: {access_specifier})")
            if is_static:
                suggested_cases.append("NOTE: Call directly via class scope (Static method)")

            f_strat = FunctionStrategy(
                name=func_name,
                signature=func["signature"],
                file=func["location"]["file"],
                line=func["location"]["line"],
                class_name=class_name,
                namespace=namespace,
                language=language,
                kind=kind,
                is_static=is_static,
                access_specifier=access_specifier,
                return_type=return_type,
                is_covered=is_covered,
                existing_tests=matched_test_names,
                existing_test_details=matched_tests,
                mocks_needed=mocks,
                suggested_test_cases=suggested_cases,
                technical_baseline=technical_context,
                mcdc_cases=mcdc_cases,
                switch_cases=switch_cases,
                body_code=func.get("body_code", ""),
            )
            strategy.functions.append(f_strat)

        return strategy

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    def save_yaml(self, strategy: FileStrategy, output_path: str):
        with open(output_path, "w") as f:
            yaml.dump(asdict(strategy), f, sort_keys=False)

    def save_markdown(self, strategy: FileStrategy, output_path: str):
        """Generate a human-readable Markdown report from the strategy."""
        lines = []
        lines.append(f"# Test Strategy for `{os.path.basename(strategy.source_file)}`")
        lines.append(f"\n**Source File:** `{strategy.source_file}`")
        lines.append("\n## Function Coverage Summary\n")

        lines.append("| Function | Kind | Access | Lang | Covered? | Complexity |")
        lines.append("| :--- | :--- | :--- | :--- | :---: | :---: |")

        for func in strategy.functions:
            status = "✅ YES" if func.is_covered else "❌ NO"
            complexity = 1
            for case in func.mcdc_cases:
                if "Complexity is" in case:
                    try:
                        complexity = int(case.split("Complexity is ")[1].split(".")[0])
                    except Exception:
                        pass
            static_tag = " 🔒static" if func.is_static else ""
            lines.append(
                f"| `{func.name}` | {func.kind}{static_tag} | {func.access_specifier} "
                f"| {func.language} | {status} | {complexity} |"
            )

        if strategy.types:
            lines.append("\n## Types (Enums, Structs, Classes)\n")
            for t in strategy.types:
                lines.append(f"- **{t['name']}** ({t['kind']})")
                if t.get('members'):
                    for m in t['members']:
                        if t['kind'] == 'enum':
                            lines.append(f"  - `{m['name']} = {m.get('value')}`")
                        else:
                            lines.append(f"  - `{m['name']}` ({m.get('type')})")

        if strategy.macros:
            lines.append("\n## Macros (#define)\n")
            for m in strategy.macros:
                lines.append(f"- `{m['name']}`")

        lines.append("\n## Detailed Strategy per Function\n")

        for func in strategy.functions:
            lines.append(f"### `{func.name}`")
            lines.append(f"- **Signature:** `{func.signature}`")
            lines.append(f"- **Location:** `{os.path.basename(func.file)}:{func.line}`")
            lines.append(f"- **Kind:** `{func.kind}`")
            lines.append(f"- **Language:** `{func.language}`")
            lines.append(f"- **Namespace:** `{func.namespace or 'global'}`")
            lines.append(f"- **Class:** `{func.class_name or 'None'}`")
            lines.append(f"- **Static:** `{func.is_static}`")
            lines.append(f"- **Access:** `{func.access_specifier}`")

            if func.existing_tests:
                lines.append("- **Existing Tests & Analyzed Strategies:**")
                for test in func.existing_test_details:
                    lines.append(f"  - **{test['full_name']}** (`{os.path.basename(test['location']['file'])}:{test['location']['line']}`)")
                    if test.get("strategy"):
                        for s in test["strategy"]:
                            lines.append(f"    - [Existing] {s}")

            if func.suggested_test_cases:
                lines.append("- **Needed / Suggested Test Scenarios:**")
                for case in func.suggested_test_cases:
                    lines.append(f"  - [Add] {case}")

            if func.switch_cases:
                lines.append("- **Switch Cases found:**")
                for sw in func.switch_cases:
                    lines.append(f"  - Cases: {', '.join(sw['cases'])}")

            if func.mocks_needed:
                lines.append("- **Mocks Needed:**")
                for mock in func.mocks_needed:
                    lines.append(f"  - {mock}")

            if func.mcdc_cases:
                lines.append("- **MCDC Requirements:**")
                for case in func.mcdc_cases:
                    lines.append(f"  - {case}")

            lines.append("")

        with open(output_path, "w") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    # Test stub
    pass
