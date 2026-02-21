import re
from typing import List, Dict, Any
import os
import sys

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
            # Matches: TEST(Suite, TestName) or TEST_F(Suite, TestName)
            # \s* handle spaces.
            pattern = re.compile(r'TEST(?:_F|_P)?\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)')
            
            for match in pattern.finditer(content):
                suite_name = match.group(1)
                test_name = match.group(2)
                
                # Determine line number (rough approximation)
                line_idx = content[:match.start()].count('\n') + 1
                
                tests.append({
                    "suite_name": suite_name,
                    "test_name": test_name,
                    "full_name": f"{suite_name}.{test_name}",
                    "location": {
                        "file": file_path,
                        "line": line_idx
                    },
                    "type": match.group(0).split('(')[0].strip() # TEST or TEST_F
                })
        
        return tests

if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: python test_parser.py <test_file>")
        sys.exit(1)
    
    analyzer = TestAnalyzer()
    results = analyzer.analyze_test_file(sys.argv[1])
    print(json.dumps(results, indent=2))
