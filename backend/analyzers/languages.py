"""Language-specific analyzer plugins."""

from __future__ import annotations

import ast
from typing import Any, List

from analyzers.base import RegexAnalyzer
from models.graph import Entity, EntityType, FileAnalysis


class PythonAnalyzer(RegexAnalyzer):
    """Analyzer for Python source files."""

    language = "python"
    extensions = [".py"]
    class_patterns = [r"^\s*class\s+(?P<name>[A-Za-z_][\w]*)"]
    function_patterns = [r"^\s*(?:async\s+)?def\s+(?P<name>[A-Za-z_][\w]*)"]
    import_patterns = [r"^\s*import\s+(?P<name>[\w.]+)", r"^\s*from\s+(?P<name>[\w.]+)\s+import"]

    def analyze(self, file_path: str, content: str) -> FileAnalysis:
        """Analyze Python using the standard AST with regex fallback."""

        result = super().analyze(file_path, content)
        try:
            module = ast.parse(content)
        except SyntaxError as exc:
            result.errors.append(str(exc))
            return result

        entities: List[Entity] = []
        imports: List[str] = []
        calls: List[str] = []
        for node in ast.walk(module):
            if isinstance(node, ast.ClassDef):
                entities.append(
                    Entity(
                        id=f"{file_path}:class:{node.name}:{node.lineno}",
                        type=EntityType.CLASS,
                        name=node.name,
                        file_path=file_path,
                        line=node.lineno,
                        metadata={
                            "bases": [getattr(base, "id", getattr(base, "attr", "")) for base in node.bases],
                            "decorators": [getattr(item, "id", "") for item in node.decorator_list],
                        },
                    )
                )
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                entities.append(
                    Entity(
                        id=f"{file_path}:function:{node.name}:{node.lineno}",
                        type=EntityType.FUNCTION,
                        name=node.name,
                        file_path=file_path,
                        line=node.lineno,
                        metadata={
                            "async": isinstance(node, ast.AsyncFunctionDef),
                            "args": [arg.arg for arg in node.args.args],
                            "returns": ast.unparse(node.returns) if node.returns else None,
                        },
                    )
                )
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls.append(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    calls.append(node.func.attr)

        if entities:
            result.entities = entities
            result.imports = sorted(set(imports or result.imports))
            result.calls = sorted(set(calls or result.calls))
            result.metrics.functions = len([item for item in entities if item.type == EntityType.FUNCTION])
            result.metrics.classes = len([item for item in entities if item.type == EntityType.CLASS])
        return result


class JavaScriptAnalyzer(RegexAnalyzer):
    """Analyzer for JavaScript, TypeScript, and JSX source files."""

    language = "javascript"
    extensions = [".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"]
    class_patterns = [r"\bclass\s+(?P<name>[A-Za-z_$][\w$]*)"]
    interface_patterns = [r"\binterface\s+(?P<name>[A-Za-z_$][\w$]*)"]
    function_patterns = [
        r"\bfunction\s+(?P<name>[A-Za-z_$][\w$]*)",
        r"\b(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(",
        r"\b(?P<name>[A-Za-z_$][\w$]*)\s*:\s*(?:async\s*)?\(",
    ]
    import_patterns = [r"\bfrom\s+['\"](?P<name>[^'\"]+)", r"\bimport\s+['\"](?P<name>[^'\"]+)"]


class JavaAnalyzer(RegexAnalyzer):
    """Analyzer for Java source files."""

    language = "java"
    extensions = [".java"]
    class_patterns = [r"\bclass\s+(?P<name>[A-Za-z_][\w]*)"]
    interface_patterns = [r"\binterface\s+(?P<name>[A-Za-z_][\w]*)"]
    function_patterns = [r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+(?P<name>[A-Za-z_][\w]*)\s*\("]
    import_patterns = [r"^\s*import\s+(?P<name>[\w.*]+);"]


class CSharpAnalyzer(RegexAnalyzer):
    """Analyzer for C# source files."""

    language = "c_sharp"
    extensions = [".cs"]
    class_patterns = [r"\bclass\s+(?P<name>[A-Za-z_][\w]*)"]
    interface_patterns = [r"\binterface\s+(?P<name>[A-Za-z_][\w]*)"]
    function_patterns = [r"(?:public|private|protected|internal|static|async|\s)+[\w<>\[\]]+\s+(?P<name>[A-Za-z_][\w]*)\s*\("]
    import_patterns = [r"^\s*using\s+(?P<name>[\w.]+);"]


class GoAnalyzer(RegexAnalyzer):
    """Analyzer for Go source files."""

    language = "go"
    extensions = [".go"]
    class_patterns = [r"\btype\s+(?P<name>[A-Za-z_][\w]*)\s+struct"]
    interface_patterns = [r"\btype\s+(?P<name>[A-Za-z_][\w]*)\s+interface"]
    function_patterns = [r"\bfunc\s+(?:\([^)]+\)\s*)?(?P<name>[A-Za-z_][\w]*)\s*\("]
    import_patterns = [r"\"(?P<name>[\w./-]+)\""]


class RustAnalyzer(RegexAnalyzer):
    """Analyzer for Rust source files."""

    language = "rust"
    extensions = [".rs"]
    class_patterns = [r"\bstruct\s+(?P<name>[A-Za-z_][\w]*)", r"\benum\s+(?P<name>[A-Za-z_][\w]*)"]
    interface_patterns = [r"\btrait\s+(?P<name>[A-Za-z_][\w]*)"]
    function_patterns = [r"\bfn\s+(?P<name>[A-Za-z_][\w]*)\s*(?:<[^>]+>)?\("]
    import_patterns = [r"\buse\s+(?P<name>[\w:]+)"]


class CppAnalyzer(RegexAnalyzer):
    """Analyzer for C and C++ source files."""

    language = "cpp"
    extensions = [".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh"]
    class_patterns = [r"\bclass\s+(?P<name>[A-Za-z_][\w]*)", r"\bstruct\s+(?P<name>[A-Za-z_][\w]*)"]
    function_patterns = [r"^[\w:<>\*&\s~]+\s+(?P<name>[A-Za-z_][\w]*)\s*\([^;]*\)\s*\{"]
    import_patterns = [r"^\s*#include\s+[<\"](?P<name>[^>\"]+)"]


class RubyAnalyzer(RegexAnalyzer):
    """Analyzer for Ruby source files."""

    language = "ruby"
    extensions = [".rb"]
    class_patterns = [r"^\s*class\s+(?P<name>[A-Za-z_][\w:]*)"]
    interface_patterns = [r"^\s*module\s+(?P<name>[A-Za-z_][\w:]*)"]
    function_patterns = [r"^\s*def\s+(?P<name>[A-Za-z_][\w!?=]*)"]
    import_patterns = [r"^\s*require\s+['\"](?P<name>[^'\"]+)"]


class PhpAnalyzer(RegexAnalyzer):
    """Analyzer for PHP source files."""

    language = "php"
    extensions = [".php"]
    class_patterns = [r"\bclass\s+(?P<name>[A-Za-z_][\w]*)", r"\btrait\s+(?P<name>[A-Za-z_][\w]*)"]
    interface_patterns = [r"\binterface\s+(?P<name>[A-Za-z_][\w]*)"]
    function_patterns = [r"\bfunction\s+(?P<name>[A-Za-z_][\w]*)\s*\("]
    import_patterns = [r"\buse\s+(?P<name>[A-Za-z_\\][\w\\]*)"]


ANALYZERS = [
    PythonAnalyzer(),
    JavaScriptAnalyzer(),
    JavaAnalyzer(),
    CSharpAnalyzer(),
    GoAnalyzer(),
    RustAnalyzer(),
    CppAnalyzer(),
    RubyAnalyzer(),
    PhpAnalyzer(),
]


def analyzer_for_extension(extension: str) -> RegexAnalyzer | None:
    """Return analyzer matching a file extension."""

    for analyzer in ANALYZERS:
        if extension.lower() in analyzer.extensions:
            return analyzer
    return None

