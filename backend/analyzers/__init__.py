"""Analyzer plugin registry."""

from analyzers.languages import ANALYZERS, analyzer_for_extension

__all__ = ["ANALYZERS", "analyzer_for_extension"]

