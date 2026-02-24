import clang.cindex
from typing import List, Dict, Optional, Any
import os
import sys

# Map clang AccessSpecifier enum to readable strings
_ACCESS_MAP = {
    clang.cindex.AccessSpecifier.PUBLIC: "public",
    clang.cindex.AccessSpecifier.PROTECTED: "protected",
    clang.cindex.AccessSpecifier.PRIVATE: "private",
    clang.cindex.AccessSpecifier.NONE: "none",
    clang.cindex.AccessSpecifier.INVALID: "none",
}

# Cursor kinds we want to capture: free functions, member methods, constructors, destructors
_FUNCTION_KINDS = {
    clang.cindex.CursorKind.FUNCTION_DECL,
    clang.cindex.CursorKind.CXX_METHOD,
    clang.cindex.CursorKind.CONSTRUCTOR,
    clang.cindex.CursorKind.DESTRUCTOR,
}

# C-compatible file extensions
_C_EXTENSIONS = {".c", ".h"}
# C++-compatible file extensions
_CPP_EXTENSIONS = {".cpp", ".cxx", ".cc", ".hpp", ".hxx", ".hh"}


def _detect_language(file_path: str) -> str:
    """Return 'C' or 'C++' based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext in _C_EXTENSIONS:
        return "C"
    return "C++"


def _parse_args_for_file(file_path: str) -> List[str]:
    """Return appropriate clang parse flags for the given source file."""
    lang = _detect_language(file_path)
    if lang == "C":
        return ["-x", "c", "-std=c11"]
    else:
        return ["-x", "c++", "-std=c++14"]


class CodeAnalyzer:
    def __init__(self):
        self.index = clang.cindex.Index.create()

    def analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyzes a single C or C++ source file and extracts function details."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        abs_file_path = os.path.abspath(file_path)
        parse_args = _parse_args_for_file(abs_file_path)
        language = _detect_language(abs_file_path)

        tu = self.index.parse(abs_file_path, args=parse_args)

        if tu.diagnostics:
            for diag in tu.diagnostics:
                if diag.severity >= clang.cindex.Diagnostic.Warning:
                    print(f"[WARN] Clang: {diag.spelling} at {diag.location}", file=sys.stderr)

        functions = []
        self._traverse(tu.cursor, functions, abs_file_path, language=language)
        return functions

    def _traverse(
        self,
        cursor,
        functions: List[Dict[str, Any]],
        target_file: str,
        namespace: str = "",
        language: str = "C++",
    ):
        """Recursively traverse the AST and collect function/method info."""
        current_namespace = namespace
        if cursor.kind == clang.cindex.CursorKind.NAMESPACE:
            current_namespace = (
                f"{namespace}::{cursor.displayname}" if namespace else cursor.displayname
            )

        if cursor.kind in _FUNCTION_KINDS:
            if cursor.location.file and os.path.abspath(cursor.location.file.name) == target_file:
                func_info = self._extract_function_info(cursor, current_namespace, language)
                functions.append(func_info)

        for child in cursor.get_children():
            self._traverse(child, functions, target_file, current_namespace, language)

    def _extract_function_info(self, cursor, namespace: str, language: str) -> Dict[str, Any]:
        """Extract rich metadata about a function or method cursor."""
        # Parameters
        params = []
        for arg in cursor.get_arguments():
            params.append(
                {
                    "name": arg.displayname,
                    "type": arg.type.spelling,
                }
            )

        # Class membership
        class_name = None
        parent = cursor.semantic_parent
        if parent and parent.kind in (
            clang.cindex.CursorKind.CLASS_DECL,
            clang.cindex.CursorKind.STRUCT_DECL,
            clang.cindex.CursorKind.CLASS_TEMPLATE,
        ):
            class_name = parent.displayname

        # Static detection
        # For C/C++ free functions: storage-class == STATIC means file-static
        # For C++ methods: is_static_method()
        is_static = False
        if cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
            is_static = cursor.is_static_method()
        elif cursor.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            is_static = cursor.storage_class == clang.cindex.StorageClass.STATIC

        # Access specifier (only meaningful for class members)
        access_specifier = _ACCESS_MAP.get(cursor.access_specifier, "none")

        # Function kind label
        kind_label = "free_function"
        if cursor.kind == clang.cindex.CursorKind.CONSTRUCTOR:
            kind_label = "constructor"
        elif cursor.kind == clang.cindex.CursorKind.DESTRUCTOR:
            kind_label = "destructor"
        elif cursor.kind == clang.cindex.CursorKind.CXX_METHOD:
            if is_static:
                kind_label = "static_method"
            elif access_specifier == "private":
                kind_label = "private_method"
            elif access_specifier == "protected":
                kind_label = "protected_method"
            else:
                kind_label = "public_method"

        # Dependencies, complexity, and body extraction (only available for definitions)
        dependencies = []
        complexity = 0
        body_code = None
        if cursor.is_definition():
            self._extract_calls(cursor, dependencies)
            complexity = self._calculate_complexity(cursor)
            body_code = self._extract_source_code(cursor)

        return {
            "name": cursor.spelling,
            "return_type": cursor.result_type.spelling,
            "parameters": params,
            "namespace": namespace,
            "class_name": class_name,
            "is_static": is_static,
            "access_specifier": access_specifier,
            "kind": kind_label,
            "language": language,
            "location": {
                "file": cursor.location.file.name if cursor.location.file else None,
                "line": cursor.location.line,
            },
            "is_definition": cursor.is_definition(),
            "signature": cursor.displayname,
            "body_code": body_code,
            "dependencies": dependencies,
            "complexity": complexity,
        }

    def _extract_source_code(self, cursor) -> Optional[str]:
        """Reads the source code for the given cursor definition."""
        if not cursor.location.file or not cursor.extent:
            return None
        
        try:
            with open(cursor.location.file.name, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # clang lines and columns are 1-indexed
                start_line = cursor.extent.start.line - 1
                end_line = cursor.extent.end.line
                
                # Extract the range of lines
                body_lines = lines[start_line:end_line]
                
                # Optional: trim if needed, but usually we want the whole block including { }
                return "".join(body_lines)
        except Exception as e:
            print(f"[WARN] Failed to extract source for {cursor.displayname}: {e}", file=sys.stderr)
            return None

    def _extract_calls(self, cursor, dependencies: List[str]):
        """Recursively find function calls within a function body."""
        if cursor.kind == clang.cindex.CursorKind.CALL_EXPR:
            if cursor.spelling:
                dependencies.append(cursor.spelling)

        for child in cursor.get_children():
            self._extract_calls(child, dependencies)

    def _calculate_complexity(self, cursor) -> int:
        """
        Estimate Cyclomatic Complexity by counting control-flow branching nodes.
        Base value is 1. Each IF, FOR, WHILE, CASE, CONDITIONAL_OPERATOR adds 1.
        """
        return self._recursive_complexity(cursor, 1)

    def _recursive_complexity(self, cursor, count: int) -> int:
        kind = cursor.kind
        if kind in (
            clang.cindex.CursorKind.IF_STMT,
            clang.cindex.CursorKind.FOR_STMT,
            clang.cindex.CursorKind.WHILE_STMT,
            clang.cindex.CursorKind.DO_STMT,
            clang.cindex.CursorKind.CASE_STMT,
            clang.cindex.CursorKind.CONDITIONAL_OPERATOR,  # ternary ? :
        ):
            count += 1

        for child in cursor.get_children():
            count = self._recursive_complexity(child, count)

        return count


if __name__ == "__main__":
    import json

    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <source_file>")
        sys.exit(1)

    analyzer = CodeAnalyzer()
    results = analyzer.analyze_file(sys.argv[1])
    print(json.dumps(results, indent=2))
