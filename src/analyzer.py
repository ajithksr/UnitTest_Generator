import clang.cindex
from typing import List, Dict, Optional, Any
import os
import sys

# Configure libclang if needed.
# For now, we assume it's in the path or installed via pip.

class CodeAnalyzer:
    def __init__(self):
        self.index = clang.cindex.Index.create()

    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyzes a single C++ source file and extracts function details."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Resolve absolute path to ensure matching works
        abs_file_path = os.path.abspath(file_path)
        
        # Parse the file
        tu = self.index.parse(abs_file_path, args=['-x', 'c++', '-std=c++14'])
        
        functions = []
        self._traverse(tu.cursor, functions, abs_file_path)
        return functions

    def _traverse(self, cursor, functions: List[Dict[str, Any]], target_file: str, namespace: str = ""):
        # Update namespace context
        current_namespace = namespace
        if cursor.kind == clang.cindex.CursorKind.NAMESPACE:
            current_namespace = f"{namespace}::{cursor.displayname}" if namespace else cursor.displayname

        # Check for function or method declarations
        if cursor.kind in [clang.cindex.CursorKind.FUNCTION_DECL, clang.cindex.CursorKind.CXX_METHOD]:
            # Filter: Only care about functions defined/declared in the target file
            if cursor.location.file and os.path.abspath(cursor.location.file.name) == target_file:
                 # We prefer definitions to analyze implementation details (dependencies)
                 # But if it's just a declaration in the .cpp (unlikely) or .hpp, we take it.
                 # If we see the definition later, it might duplicate. 
                 # For now, let's take everything in the file and we can dedup or filter for is_definition later.
                 
                func_info = self._extract_function_info(cursor, current_namespace)
                functions.append(func_info)

        # Recurse
        for child in cursor.get_children():
            self._traverse(child, functions, target_file, current_namespace)

    def _extract_function_info(self, cursor, namespace) -> Dict[str, Any]:
        params = []
        for arg in cursor.get_arguments():
            params.append({
                "name": arg.displayname,
                "type": arg.type.spelling
            })

        # Determine if it's a class method
        class_name = None
        current = cursor.semantic_parent
        if current and current.kind in [clang.cindex.CursorKind.CLASS_DECL, clang.cindex.CursorKind.STRUCT_DECL]:
            class_name = current.displayname

        # Extract dependencies (function calls within this function)
        dependencies = []
        complexity = 0
        if cursor.is_definition():
            self._extract_calls(cursor, dependencies)
            complexity = self._calculate_complexity(cursor)

        return {
            "name": cursor.spelling,
            "return_type": cursor.result_type.spelling,
            "parameters": params,
            "namespace": namespace,
            "class_name": class_name,
            "location": {
                "file": cursor.location.file.name if cursor.location.file else None,
                "line": cursor.location.line
            },
            "is_definition": cursor.is_definition(),
            "signature": cursor.displayname,
            "dependencies": dependencies,
            "complexity": complexity
        }

    def _extract_calls(self, cursor, dependencies: List[str]):
        """Recursively finds function calls within a function body."""
        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            dependencies.append(cursor.spelling)
        
        for child in cursor.get_children():
            self._extract_calls(child, dependencies)

    def _calculate_complexity(self, cursor) -> int:
        """
        Estimates Cyclomatic Complexity by counting branching keywords.
        Start at 1 for the base path.
        """
        complexity = 1
        return self._recursive_complexity(cursor, complexity)

    def _recursive_complexity(self, cursor, count: int) -> int:
        # Check for branching constructs
        kind = cursor.kind
        if kind in [
            clang.cindex.CursorKind.IF_STMT,
            clang.cindex.CursorKind.FOR_STMT,
            clang.cindex.CursorKind.WHILE_STMT,
            clang.cindex.CursorKind.CASE_STMT,
            clang.cindex.CursorKind.DEFAULT_STMT, # Sometimes conditional? Usually Case handles it.
            clang.cindex.CursorKind.CONDITIONAL_OPERATOR, # Ternary ? :
            clang.cindex.CursorKind.BINARY_OPERATOR # AND/OR (Short-circuiting)
        ]:
            # For Binary Operator, we only care about && and ||
            if kind == clang.cindex.CursorKind.BINARY_OPERATOR:
                # We need to check tokens but that's expensive/hard without tokenizing.
                # Heuristic: Just assume complex ops might increase paths? 
                # Actually, standard complexity usually counts predicates + 1.
                # Let's stick to Control Flow Stmts for now to keep it fast.
                pass
            else:
                count += 1
        
        # Specific check for logic ops if easy? 
        # libclang doesn't give OpCode easily on cursor.
        
        for child in cursor.get_children():
            count = self._recursive_complexity(child, count)
        
        return count


if __name__ == "__main__":
    import json
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <cpp_file>")
        sys.exit(1)
    
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_file(sys.argv[1])
    print(json.dumps(results, indent=2))
