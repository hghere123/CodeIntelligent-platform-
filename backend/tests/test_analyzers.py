"""Analyzer unit tests."""

from analyzers.languages import ANALYZERS, PythonAnalyzer
from models.graph import EntityType


def test_python_analyzer_extracts_classes_functions_and_imports() -> None:
    """Python analyzer extracts AST entities."""

    content = """
import os
from fastapi import FastAPI

class Service:
    async def run(self) -> str:
        return helper()

def helper():
    return "ok"
"""
    result = PythonAnalyzer().analyze("app.py", content)
    names = {entity.name for entity in result.entities}
    assert {"Service", "run", "helper"} <= names
    assert "fastapi" in {item.lower() for item in result.imports}
    assert result.metrics.classes == 1
    assert result.metrics.functions == 2


def test_all_language_analyzers_find_basic_entity() -> None:
    """Every configured analyzer extracts at least one representative entity."""

    snippets = {
        "javascript": "import React from 'react';\nclass App {}\nconst run = () => fetch('/api');",
        "java": "package demo; public class App { public void run() {} }",
        "c_sharp": "namespace Demo { public class App { public async Task Run() {} } }",
        "go": "package main\nfunc main() {}\ntype User struct{}",
        "rust": "use std::fmt;\nstruct User {}\nfn main() {}",
        "cpp": "#include <vector>\nclass App {}; int run() { return 0; }",
        "ruby": "require 'rails'\nclass App\n def run\n end\nend",
        "php": "<?php namespace Demo; class App { function run() {} }",
    }
    for analyzer in ANALYZERS:
        if analyzer.language == "python":
            continue
        result = analyzer.analyze(f"file{analyzer.extensions[0]}", snippets[analyzer.language])
        assert any(entity.type in {EntityType.CLASS, EntityType.FUNCTION, EntityType.INTERFACE} for entity in result.entities)

