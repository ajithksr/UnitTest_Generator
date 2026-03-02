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

# Cursor kinds we want to capture
_FUNCTION_KINDS = {
    clang.cindex.CursorKind.FUNCTION_DECL,
    clang.cindex.CursorKind.CXX_METHOD,
    clang.cindex.CursorKind.CONSTRUCTOR,
    clang.cindex.CursorKind.DESTRUCTOR,
}

_TYPE_KINDS = {
    clang.cindex.CursorKind.ENUM_DECL,
    clang.cindex.CursorKind.STRUCT_DECL,
    clang.cindex.CursorKind.CLASS_DECL,
    clang.cindex.CursorKind.UNION_DECL,
    clang.cindex.CursorKind.TYPEDEF_DECL,
    clang.cindex.CursorKind.TYPE_ALIAS_DECL,
}

_MACRO_KINDS = {
    clang.cindex.CursorKind.MACRO_DEFINITION,
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
    args = []
    if lang == "C":
        args = ["-x", "c", "-std=c11"]
    else:
        args = ["-x", "c++", "-std=c++14"]
    
    # Enable macro expansion if possible
    args.append("-Xclang")
    args.append("-detailed-preprocessing-record")
    return args


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
        types = []
        macros = []
        
        # Traverse the whole TU to get everything (including includes)
        self._traverse(tu.cursor, functions, types, macros, abs_file_path, language=language)
        
        return {
            "functions": functions,
            "types": types,
            "macros": macros,
            "file": abs_file_path,
            "language": language
        }

    def _traverse(
        self,
        cursor,
        functions: List[Dict[str, Any]],
        types: List[Dict[str, Any]],
        macros: List[Dict[str, Any]],
        target_file: str,
        namespace: str = "",
        language: str = "C++",
    ):
        """Recursively traverse the AST and collect function/method/type/macro info."""
        current_namespace = namespace
        if cursor.kind == clang.cindex.CursorKind.NAMESPACE:
            current_namespace = (
                f"{namespace}::{cursor.displayname}" if namespace else cursor.displayname
            )

        # Check if cursor is in the target file OR in an included file
        # We might want to filter out system headers but keep local ones
        is_in_target = False
        if cursor.location.file:
            cursor_file = os.path.abspath(cursor.location.file.name)
            if cursor_file == target_file:
                is_in_target = True
            # For now, let's capture everything defined in the same directory as hints
            elif os.path.dirname(cursor_file) == os.path.dirname(target_file):
                is_in_target = True

        if is_in_target:
            if cursor.kind in _FUNCTION_KINDS:
                # Only add if it's the target file to avoid duplication in 'functions' list
                # but we can relax this if we want all functions discovered
                if os.path.abspath(cursor.location.file.name) == target_file:
                    func_info = self._extract_function_info(cursor, current_namespace, language)
                    functions.append(func_info)
            
            elif cursor.kind in _TYPE_KINDS:
                type_info = self._extract_type_info(cursor, current_namespace)
                types.append(type_info)
            
            elif cursor.kind in _MACRO_KINDS:
                macro_info = self._extract_macro_info(cursor)
                if macro_info:
                    macros.append(macro_info)

        for child in cursor.get_children():
            self._traverse(child, functions, types, macros, target_file, current_namespace, language)

    def _extract_type_info(self, cursor, namespace: str) -> Dict[str, Any]:
        """Extract info about enums, structs, classes."""
        kind_map = {
            clang.cindex.CursorKind.ENUM_DECL: "enum",
            clang.cindex.CursorKind.STRUCT_DECL: "struct",
            clang.cindex.CursorKind.CLASS_DECL: "class",
            clang.cindex.CursorKind.UNION_DECL: "union",
            clang.cindex.CursorKind.TYPEDEF_DECL: "typedef",
            clang.cindex.CursorKind.TYPE_ALIAS_DECL: "type_alias",
        }
        
        members = []
        if cursor.kind == clang.cindex.CursorKind.ENUM_DECL:
            for child in cursor.get_children():
                if child.kind == clang.cindex.CursorKind.ENUM_CONSTANT_DECL:
                    members.append({
                        "name": child.spelling,
                        "value": child.enum_value
                    })
        elif cursor.kind in (clang.cindex.CursorKind.STRUCT_DECL, clang.cindex.CursorKind.CLASS_DECL):
            for child in cursor.get_children():
                if child.kind == clang.cindex.CursorKind.FIELD_DECL:
                    members.append({
                        "name": child.spelling,
                        "type": child.type.spelling,
                        "access": _ACCESS_MAP.get(child.access_specifier, "none")
                    })

        return {
            "name": cursor.spelling,
            "kind": kind_map.get(cursor.kind, "unknown"),
            "namespace": namespace,
            "members": members,
            "location": {
                "file": cursor.location.file.name if cursor.location.file else None,
                "line": cursor.location.line,
            }
        }

    def _extract_macro_info(self, cursor) -> Optional[Dict[str, Any]]:
        """Extract macro definitions."""
        if not cursor.spelling:
            return None
        return {
            "name": cursor.spelling,
            "location": {
                "file": cursor.location.file.name if cursor.location.file else None,
                "line": cursor.location.line,
            }
        }

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
        switch_cases = []
        if cursor.is_definition():
            self._extract_calls(cursor, dependencies)
            complexity = self._calculate_complexity(cursor)
            body_code = self._extract_source_code(cursor)
            self._extract_switch_cases(cursor, switch_cases)

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
            "switch_cases": switch_cases,
        }

    def _extract_switch_cases(self, cursor, cases: List[Dict[str, Any]]):
        """Recursively find switch statements and their cases."""
        if cursor.kind == clang.cindex.CursorKind.SWITCH_STMT:
            switch_info = {"cases": []}
            self._find_cases_in_switch(cursor, switch_info["cases"])
            cases.append(switch_info)

        for child in cursor.get_children():
            self._extract_switch_cases(child, cases)

    def _find_cases_in_switch(self, cursor, case_list: List[str]):
        """Internal helper to find CASE_STMT within a SWITCH_STMT subtree."""
        for child in cursor.get_children():
            if child.kind == clang.cindex.CursorKind.CASE_STMT:
                # Try to get the case value/label
                src = self._extract_source_code(child)
                if src:
                    case_label = src.split(':')[0].replace('case', '').strip()
                    case_list.append(case_label)
            elif child.kind == clang.cindex.CursorKind.DEFAULT_STMT:
                case_list.append("default")
            
            # Continue searching in children (e.g. COMPOUND_STMT)
            self._find_cases_in_switch(child, case_list)

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
