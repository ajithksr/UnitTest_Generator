import yaml
from jinja2 import Environment, FileSystemLoader
import os
from typing import Dict, Any
from src.llm_client import LLMClient


class TestGenerator:
    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.llm_client = LLMClient()

    def generate_test_code(self, strategy_file: str, output_file: str, use_llm: bool = True):
        if not os.path.exists(strategy_file):
            raise FileNotFoundError(f"Strategy file not found: {strategy_file}")

        with open(strategy_file, "r") as f:
            strategy_data = yaml.safe_load(f)

        functions = strategy_data.get("functions", [])
        if not functions:
            print("No functions in strategy.")
            return

        # Derive language from the first function that has it, fallback to extension heuristic
        source_file = strategy_data.get("source_file", "unknown.cpp")
        source_filename = os.path.basename(source_file)

        language = "C++"  # default
        for func in functions:
            if func.get("language"):
                language = func["language"]
                break
        if language == "C":
            header_filename = source_filename.replace(".c", ".h")
        else:
            header_filename = (
                source_filename.replace(".cpp", ".hpp")
                .replace(".cxx", ".hpp")
                .replace(".cc", ".hpp")
                .replace(".c", ".h")
            )

        # Collect class/namespace info
        target_class = None
        target_namespace = None
        mocks = set()
        has_non_static_members = False

        for func in functions:
            if func.get("class_name") and not target_class:
                target_class = func["class_name"]
            if func.get("namespace") and not target_namespace:
                target_namespace = func["namespace"]

            kind = func.get("kind", "free_function")
            if kind in ("public_method", "protected_method", "private_method"):
                has_non_static_members = True

            for mock in func.get("mocks_needed", []):
                if mock and "Mock for " in mock and len(mock) > 9:
                    mocks.add(mock)

            # LLM Generation for uncovered functions
            if use_llm and not func.get("is_covered"):
                print(f"Asking LLM to generate test for: {func['name']}...")
                try:
                    func_strategy = {
                        "suggested_test_cases": func.get("suggested_test_cases", []),
                        "boundary_cases": func.get("boundary_cases", []),
                        "equivalence_partition_cases": func.get("equivalence_partition_cases", []),
                        "mocks_needed": func.get("mocks_needed", []),
                        "class_name": target_class or "UnknownClass",
                        "language": language,
                        "is_static": func.get("is_static", False),
                        "access_specifier": func.get("access_specifier", "none"),
                        "kind": func.get("kind", "free_function"),
                    }
                    body = self.llm_client.generate_test_body(func["signature"], func_strategy)
                    func["test_body"] = body
                except Exception as e:
                    print(f"LLM Generation failed for {func['name']}: {e}")

        context = {
            "source_filename": header_filename,
            "language": language,
            "class_name": target_class or "UnknownClass",
            "namespace": target_namespace or "",
            "has_class": target_class is not None,
            "has_non_static_members": has_non_static_members,
            "functions": functions,
            "mocks": list(mocks),
        }

        code = self.render(context, "test_framework.j2")

        with open(output_file, "w") as f:
            f.write(code)

        print(f"Generated test code: {output_file}")

    def render(self, context: Dict[str, Any], template_name: str = "test_framework.j2") -> str:
        template = self.env.get_template(template_name)
        return template.render(context)
