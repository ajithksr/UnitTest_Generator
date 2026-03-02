import re
from typing import List, Dict, Any
import os
import sys

from .prompts import EXISTING_TEST_STRATEGY_PROMPT

class TestAnalyzer:
    def __init__(self):
        pass

    def analyze_test_file(self, file_path: str) -> List[Dict[str, Any]]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        tests = []
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Regex for TEST, TEST_F, TEST_P with arguments (Suite, Name)
            # Matches: TEST(Suite, TestName) { body }
            # We need to find the matching '}' for the test body.
            pattern = re.compile(r'(TEST(?:_F|_P)?\s*\(\s*(\w+)\s*,\s*(\w+)\s*\))\s*\{')
            
            for match in pattern.finditer(content):
                full_macro = match.group(1)
                suite_name = match.group(2)
                test_name = match.group(3)
                
                # Find the matching closing brace for the body
                start_ptr = match.end()
                bracket_count = 1
                end_ptr = start_ptr
                while bracket_count > 0 and end_ptr < len(content):
                    if content[end_ptr] == '{':
                        bracket_count += 1
                    elif content[end_ptr] == '}':
                        bracket_count -= 1
                    end_ptr += 1
                
                test_body = content[start_ptr:end_ptr-1].strip()
                
                # Determine line number
                line_idx = content[:match.start()].count('\n') + 1
                
                tests.append({
                    "suite_name": suite_name,
                    "test_name": test_name,
                    "full_name": f"{suite_name}.{test_name}",
                    "location": {
                        "file": file_path,
                        "line": line_idx
                    },
                    "type": full_macro.split('(')[0].strip(),
                    "body": test_body,
                    "strategy": None # To be filled by LLM analysis
                })
        
        return tests

    def analyze_test_strategies(self, tests: List[Dict[str, Any]], llm_client: Any):
        """Uses LLM to understand the strategy behind each existing test."""
        for test in tests:
            if not test.get("body"):
                continue
                
            print(f"[INFO] Analyzing existing test strategy: {test['full_name']}...")
            prompt = EXISTING_TEST_STRATEGY_PROMPT.format(
                test_name=test['full_name'],
                test_body=test['body']
            )
            try:
                # Use a simple generation call
                response = llm_client.provider.generate_code(prompt)
                
                import json
                import re
                
                resp_text = response.strip()
                json_match = re.search(r'\[\s*".*"\s*\]', resp_text, re.DOTALL)
                if json_match:
                    try:
                        strategy = json.loads(json_match.group(0))
                        test["strategy"] = strategy
                    except:
                        pass
                
                if not test["strategy"]:
                    # Fallback to lines
                    lines = [l.strip() for l in resp_text.split('\n') if l.strip() and not l.startswith('```')]
                    test["strategy"] = lines[:5]
            except Exception as e:
                print(f"[WARN] Failed to analyze strategy for {test['full_name']}: {e}")
                test["strategy"] = ["Error analyzing strategy"]

if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: python test_parser.py <test_file>")
        sys.exit(1)
    
    analyzer = TestAnalyzer()
    results = analyzer.analyze_test_file(sys.argv[1])
    print(json.dumps(results, indent=2))
