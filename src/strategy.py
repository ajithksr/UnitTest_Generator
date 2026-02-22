import yaml
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import os

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


def _boundary_cases_for_type(param_name: str, type_str: str) -> List[str]:
    """Return boundary-condition test case descriptions for a single parameter."""
    t = type_str.strip().lower()
    cases = []

    # Strip const / reference decoration for lookup
    bare = t.replace("const", "").replace("&", "").replace("volatile", "").strip()

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
    bare = t.replace("const", "").replace("&", "").replace("volatile", "").strip()
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
    is_covered: bool
    existing_tests: List[str]
    class_name: Optional[str] = None
    namespace: Optional[str] = None
    language: str = "C++"
    kind: str = "free_function"          # constructor / destructor / static_method / private_method / …
    is_static: bool = False
    access_specifier: str = "none"       # public / private / protected / none
    suggested_test_cases: List[str] = field(default_factory=list)
    boundary_cases: List[str] = field(default_factory=list)
    equivalence_partition_cases: List[str] = field(default_factory=list)
    mocks_needed: List[str] = field(default_factory=list)
    mcdc_cases: List[str] = field(default_factory=list)


@dataclass
class FileStrategy:
    source_file: str
    functions: List[FunctionStrategy] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Strategy generator
# ---------------------------------------------------------------------------

class StrategyGenerator:
    def __init__(self):
        pass

    def generate_strategy(
        self,
        file_functions: List[Dict[str, Any]],
        existing_tests: List[Dict[str, Any]],
    ) -> FileStrategy:
        """
        Compares analyzed functions with existing tests and generates a rich strategy,
        including boundary and equivalence partition test cases.
        """
        source_file = (
            file_functions[0]["location"]["file"] if file_functions else "unknown"
        )
        strategy = FileStrategy(source_file=source_file)

        for func in file_functions:
            func_name = func["name"]
            class_name = func.get("class_name")
            namespace = func.get("namespace")
            language = func.get("language", "C++")
            kind = func.get("kind", "free_function")
            is_static = func.get("is_static", False)
            access_specifier = func.get("access_specifier", "none")
            parameters = func.get("parameters", [])

            # ------------------------------------------------------------------
            # Match against existing tests
            # ------------------------------------------------------------------
            matched_tests = []
            for test in existing_tests:
                suite_matches = False
                if class_name and class_name.lower() in test["suite_name"].lower():
                    suite_matches = True
                elif namespace and namespace.lower() in test["suite_name"].lower():
                    suite_matches = True

                name_matches = func_name.lower() in test["test_name"].lower()

                if suite_matches and name_matches:
                    matched_tests.append(test["full_name"])
                elif name_matches:
                    matched_tests.append(test["full_name"] + " (Weak Match)")

            is_covered = len(matched_tests) > 0

            # ------------------------------------------------------------------
            # Boundary & Equivalence Partition cases
            # ------------------------------------------------------------------
            boundary_cases, ep_cases = _generate_boundary_ep_cases(parameters)

            # ------------------------------------------------------------------
            # Basic suggested cases
            # ------------------------------------------------------------------
            suggested_cases = list(func.get("suggested_test_cases") or [])
            if not suggested_cases:
                base = ["Positive Case", "Negative Case", "Boundary Case"]
                suggested_cases = base if not is_covered else ["Additional Verification"]

            # Private / protected: note testing strategy
            if access_specifier in ("private", "protected"):
                suggested_cases.append(
                    f"Access: {access_specifier} method — test via public API, "
                    f"friend class, or expose via test subclass"
                )

            # Static functions
            if is_static:
                suggested_cases.append(
                    "Static: call directly without class instance — verify thread-safety if applicable"
                )

            # ------------------------------------------------------------------
            # Mock / failure injection from dependencies
            # ------------------------------------------------------------------
            mocks = []
            for dep in func.get("dependencies", []):
                if dep:
                    mocks.append(f"Mock for {dep}")
                    suggested_cases.append(f"Failure Injection: {dep} throws/returns error")

            # ------------------------------------------------------------------
            # MCDC analysis
            # ------------------------------------------------------------------
            complexity = func.get("complexity", 1)
            mcdc_cases = []
            if complexity > 1:
                mcdc_cases.append(
                    f"MCDC: Complexity is {complexity}. Cover all {complexity} logical path combinations."
                )
                suggested_cases.append(f"MCDC: Verify {complexity} logical paths")

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
                is_covered=is_covered,
                existing_tests=matched_tests,
                mocks_needed=mocks,
                suggested_test_cases=suggested_cases,
                boundary_cases=boundary_cases,
                equivalence_partition_cases=ep_cases,
                mcdc_cases=mcdc_cases,
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
                lines.append("- **Existing Tests:**")
                for test in func.existing_tests:
                    lines.append(f"  - {test}")

            if func.suggested_test_cases:
                lines.append("- **Suggested Test Cases:**")
                for case in func.suggested_test_cases:
                    lines.append(f"  - {case}")

            if func.boundary_cases:
                lines.append("- **Boundary Cases:**")
                for case in func.boundary_cases:
                    lines.append(f"  - {case}")

            if func.equivalence_partition_cases:
                lines.append("- **Equivalence Partition Cases:**")
                for case in func.equivalence_partition_cases:
                    lines.append(f"  - {case}")

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
