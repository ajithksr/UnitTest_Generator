import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import os

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
    suggested_test_cases: List[str] = field(default_factory=list)
    mocks_needed: List[str] = field(default_factory=list)
    mcdc_cases: List[str] = field(default_factory=list)

@dataclass
class FileStrategy:
    source_file: str
    functions: List[FunctionStrategy] = field(default_factory=list)

class StrategyGenerator:
    def __init__(self):
        pass

    def generate_strategy(self, file_functions: List[Dict[str, Any]], existing_tests: List[Dict[str, Any]]) -> FileStrategy:
        """
        Compares analyzed functions with existing tests to generate a strategy.
        """
        strategy = FileStrategy(source_file=file_functions[0]['location']['file'] if file_functions else "unknown")

        for func in file_functions:
            func_name = func['name']
            class_name = func.get('class_name')
            namespace = func.get('namespace')
            
            # Simple Heuristic for mapping:
            # Check if any test suite contains the class name (if class exists) or namespace.
            # Check if test name contains function name.
            
            matched_tests = []
            for test in existing_tests:
                # 1. Match Class/Suite
                suite_matches = False
                if class_name and class_name.lower() in test['suite_name'].lower():
                    suite_matches = True
                elif namespace and namespace.lower() in test['suite_name'].lower(): 
                    # Looser match if no class
                    suite_matches = True
                elif not class_name and not namespace:
                     # Global function, relies on some convention? 
                     # Maybe suite name contains "Global" or file name?
                     pass
                
                # 2. Match Function Name
                # Test name often includes function name: e.g. AddTests for add()
                name_matches = func_name.lower() in test['test_name'].lower()
                
                if suite_matches and name_matches:
                    matched_tests.append(test['full_name'])
                elif name_matches: 
                    # If just name matches, it's a weak match, but maybe valid for simple setups
                    matched_tests.append(test['full_name'] + " (Weak Match)")

            # Determine coverage
            is_covered = len(matched_tests) > 0

            # Define Mocks needed & Failure Injection
            # Based on dependencies extracted by Analyzer
            mocks = []
            suggested_cases = func.get('suggested_test_cases', []) if func.get('suggested_test_cases') else []
            
            # Default cases if not already present
            if not suggested_cases:
                suggested_cases = ["Positive Case", "Negative Case", "Boundary Case"] if not is_covered else ["Additional Verification"]

            # Failure Injection for Mocks
            for dep in func.get('dependencies', []):
                # Heuristic: Dependencies that look like calls (and we assume are external/mockable)
                # In a real scenario, we'd check if 'dep' is a method of an injected class.
                # Here we just list them.
                if dep: 
                    mocks.append(f"Mock for {dep}")
                    # Add Failure Case
                    suggested_cases.append(f"Failure Injection: {dep} throws/returns error")

            # MCDC Analysis
            complexity = func.get('complexity', 1)
            mcdc_cases = []
            if complexity > 1:
                # Suggest exhaustive Logic Coverage
                mcdc_cases.append(f"MCDC: Complexity is {complexity}. Need to cover all path combinations.")
                suggested_cases.append(f"MCDC: Verify {complexity} logical paths")

            f_strat = FunctionStrategy(
                name=func_name,
                signature=func['signature'],
                file=func['location']['file'],
                line=func['location']['line'],
                class_name=class_name,
                namespace=namespace,
                is_covered=is_covered,
                existing_tests=matched_tests,
                mocks_needed=mocks,
                suggested_test_cases=suggested_cases,
                mcdc_cases=mcdc_cases
            )
            strategy.functions.append(f_strat)
        
        return strategy

    def save_yaml(self, strategy: FileStrategy, output_path: str):
        with open(output_path, 'w') as f:
            yaml.dump(asdict(strategy), f, sort_keys=False)

    def save_markdown(self, strategy: FileStrategy, output_path: str):
        """
        Generates a human-readable Markdown report from the strategy.
        """
        lines = []
        lines.append(f"# Test Strategy for `{os.path.basename(strategy.source_file)}`")
        lines.append(f"\n**Source File:** `{strategy.source_file}`")
        lines.append("\n## Function Coverage Summary\n")
        
        # Summary Table
        lines.append("| Function | Covered? | Mocks Needed | Complexity |")
        lines.append("| :--- | :---: | :--- | :---: |")
        
        for func in strategy.functions:
            status = "✅ YES" if func.is_covered else "❌ NO"
            mocks = ", ".join(func.mocks_needed) if func.mocks_needed else "-"
            # Extract complexity from mcdc_cases if possible
            complexity = 1
            for case in func.mcdc_cases:
                if "Complexity is" in case:
                    try:
                        complexity = int(case.split("Complexity is ")[1].split(".")[0])
                    except:
                        pass
            lines.append(f"| `{func.name}` | {status} | {mocks} | {complexity} |")

        lines.append("\n## Detailed Strategy per Function\n")
        
        for func in strategy.functions:
            lines.append(f"### `{func.name}`")
            lines.append(f"- **Signature:** `{func.signature}`")
            lines.append(f"- **Location:** `{os.path.basename(func.file)}:{func.line}`")
            lines.append(f"- **Namespace:** `{func.namespace or 'global'}`")
            lines.append(f"- **Class:** `{func.class_name or 'None'}`")
            
            if func.existing_tests:
                lines.append("- **Existing Tests:**")
                for test in func.existing_tests:
                    lines.append(f"  - {test}")
            
            if func.suggested_test_cases:
                lines.append("- **Suggested Test Cases:**")
                for case in func.suggested_test_cases:
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

        with open(output_path, 'w') as f:
            f.write("\n".join(lines))

if __name__ == "__main__":
    # Test stub
    pass
