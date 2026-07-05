"""File classification helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List


SOURCE_EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "javascript",
    ".tsx": "javascript",
    ".java": "java",
    ".cs": "c_sharp",
    ".go": "go",
    ".rs": "rust",
    ".c": "cpp",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".h": "cpp",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
}

CONFIG_NAMES = {
    "package.json",
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
    "pom.xml",
    "build.gradle",
    "cargo.toml",
    "go.mod",
    "composer.json",
    "gemfile",
    ".csproj",
    "packages.config",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    ".gitlab-ci.yml",
    "jenkinsfile",
    ".git-blame-ignore-revs",
    ".gitattributes",
    ".gitignore",
    "authors",
    "makefile",
    "news",
    "version",
    "scrapy_bash_completion",
    "scrapy_zsh_completion",
}

CONFIG_EXTENSIONS = {".json", ".toml", ".xml", ".gradle", ".yml", ".yaml", ".tf", ".cff", ".rst"}
ALLOWED_EXTENSIONS = set(SOURCE_EXTENSIONS) | CONFIG_EXTENSIONS | {
    ".txt",
    ".md",
    ".rst",
    ".dockerfile",
    ".config",
    ".csproj",
    # Stylesheets
    ".css",
    ".scss",
    ".less",
    # Images
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".gif",
    ".ico",
    ".bmp",
    ".webp",
    # Fonts
    ".woff",
    ".woff2",
    ".eot",
    ".ttf",
    ".otf",
    # Misc
    ".ini",
    ".cfg",
    ".in",
    # HTML
    ".html",
    ".htm",
}
IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
IGNORED_EXTENSIONS = {".pyc"}


def iter_repository_files(root: Path) -> Iterable[Path]:
    """Yield relevant files under a repository root."""

    ignored = IGNORED_DIRS
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file() and not is_binary_file(path):
            yield path


def is_source_file(path: Path) -> bool:
    """Return whether a path is a supported source file."""

    return path.suffix.lower() in SOURCE_EXTENSIONS


def is_config_file(path: Path) -> bool:
    """Return whether a path is a supported configuration file."""

    name = path.name.lower()
    return name in CONFIG_NAMES or path.suffix.lower() in CONFIG_EXTENSIONS or ".github/workflows" in path.as_posix()


def detect_language(path: Path) -> str:
    """Return language key for a file path."""

    return SOURCE_EXTENSIONS.get(path.suffix.lower(), "config" if is_config_file(path) else "text")


def read_text(path: Path) -> str:
    """Read file content safely as text."""

    return path.read_text(encoding="utf-8", errors="ignore")


def repository_tree(root: Path) -> dict:
    """Build a nested repository tree dictionary."""

    def build(path: Path) -> dict:
        children: List[dict] = []
        if path.is_dir():
            for child in sorted(path.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower())):
                if child.name in {".git", "node_modules", "__pycache__"}:
                    continue
                children.append(build(child))
        return {
            "name": path.name,
            "path": path.relative_to(root).as_posix() if path != root else "",
            "type": "directory" if path.is_dir() else "file",
            "children": children,
        }

    return build(root)


def is_binary_file(path: Path) -> bool:
    """Best-effort binary file check."""

    try:
        chunk = path.read_bytes()[:2048]
    except OSError:
        return True
    return b"\0" in chunk

