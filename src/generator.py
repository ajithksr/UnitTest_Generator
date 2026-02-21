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

        with open(strategy_file, 'r') as f:
            strategy_data = yaml.safe_load(f)

        functions = strategy_data.get('functions', [])
        if not functions:
            print("No functions in strategy.")
            return

        # Prepare context
        target_class = "UnknownClass"
        target_namespace = "UnknownNamespace"
        source_file = strategy_data.get('source_file', 'unknown.cpp')
        source_filename = os.path.basename(source_file)
        # Attempt to include header instead of source if possible
        header_filename = source_filename.replace('.cpp', '.hpp').replace('.c', '.h')
        
        mocks = set()
        
        for func in functions:
            if func.get('class_name'):
                target_class = func['class_name']
            if func.get('namespace'):
                target_namespace = func['namespace']
            
            for mock in func.get('mocks_needed', []):
                if mock and "Mock for " in mock and len(mock) > 9: # "Mock for " is 9 chars
                    mocks.add(mock)
            
            # LLM Generation
            if use_llm and not func.get('is_covered'):
                print(f"Asking LLM to generate test for: {func['name']}...")
                try:
                    # Enrich strategy dict for prompt
                    func_strategy = {
                        'suggested_test_cases': func.get('suggested_test_cases', []),
                        'mocks_needed': func.get('mocks_needed', []),
                        'class_name': target_class
                    }
                    body = self.llm_client.generate_test_body(func['signature'], func_strategy)
                    func['test_body'] = body
                except Exception as e:
                    print(f"LLM Generation failed for {func['name']}: {e}")

        context = {
            "source_filename": header_filename,
            "class_name": target_class,
            "namespace": target_namespace,
            "functions": functions,
            "mocks": list(mocks)
        }
        
        code = self.render(context, "test_framework.j2")
        
        with open(output_file, 'w') as f:
            f.write(code)
            
        print(f"Generated test code: {output_file}")

    def render(self, context: Dict[str, Any], template_name: str = "test_framework.j2") -> str:
        template = self.env.get_template(template_name)
        return template.render(context)
