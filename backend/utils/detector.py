"""Configuration parsing and technology detectors."""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Iterable, List, Set

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib


TECH_SIGNATURES: Dict[str, Dict[str, List[str]]] = {
    "frameworks": {
        "React": ["react"],
        "Angular": ["@angular/core", "angular"],
        "Vue": ["vue"],
        "Next.js": ["next"],
        "Nuxt": ["nuxt"],
        "Django": ["django"],
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "Spring Boot": ["spring-boot", "org.springframework.boot"],
        "Express": ["express"],
        "NestJS": ["@nestjs/core"],
        "ASP.NET": ["microsoft.aspnetcore", "aspnet"],
        "Laravel": ["laravel/framework"],
        "Rails": ["rails"],
    },
    "databases": {
        "PostgreSQL": ["postgres", "psycopg", "pg"],
        "MySQL": ["mysql", "pymysql"],
        "MongoDB": ["mongodb", "mongoose", "pymongo"],
        "Redis": ["redis"],
        "SQLite": ["sqlite", "sqlite3"],
        "Elasticsearch": ["elasticsearch"],
        "DynamoDB": ["dynamodb"],
    },
    "cloud": {
        "AWS": ["boto3", "aws-sdk", "amazonaws", "aws"],
        "Azure": ["azure", "microsoft.azure"],
        "GCP": ["google-cloud", "gcp"],
        "DigitalOcean": ["digitalocean"],
        "Heroku": ["heroku"],
        "Vercel": ["vercel"],
        "Netlify": ["netlify"],
        "Cloudflare": ["cloudflare"],
    },
    "containers": {
        "Docker": ["dockerfile", "docker "],
        "Docker Compose": ["docker-compose", "services:"],
        "Kubernetes": ["apiVersion:", "kind: Deployment", "kind: Service"],
        "Helm": ["chart.yaml", "helm"],
        "Podman": ["podman"],
    },
    "ai_ml": {
        "TensorFlow": ["tensorflow"],
        "PyTorch": ["torch", "pytorch"],
        "Keras": ["keras"],
        "Hugging Face": ["transformers", "huggingface"],
        "LangChain": ["langchain"],
        "LlamaIndex": ["llama-index", "llama_index"],
        "OpenAI": ["openai"],
        "Anthropic": ["anthropic"],
        "Gemini": ["google-generativeai", "gemini"],
        "Pinecone": ["pinecone"],
        "Weaviate": ["weaviate"],
        "Chroma": ["chromadb", "chroma"],
        "FAISS": ["faiss"],
    },
    "queues": {
        "RabbitMQ": ["rabbitmq", "amqp"],
        "Kafka": ["kafka"],
        "Redis Pub/Sub": ["pubsub", "redis.publish", "redis.subscribe"],
        "SQS": ["sqs"],
        "Pub/Sub": ["pubsub", "google-cloud-pubsub"],
    },
}


class ConfigurationAnalyzer:
    """Parse dependency and infrastructure configuration files."""

    def analyze_file(self, path: Path, content: str) -> Dict[str, Any]:
        """Extract dependencies and config facts from one file."""

        name = path.name.lower()
        if name == "package.json" or name == "composer.json":
            return self._json_dependencies(content)
        if name in {"requirements.txt", "gemfile"}:
            return {"dependencies": self._line_dependencies(content)}
        if name in {"pyproject.toml", "cargo.toml"}:
            return self._toml_dependencies(content)
        if name in {"pom.xml", "packages.config"} or path.suffix.lower() == ".csproj":
            return self._xml_dependencies(content)
        if name == "go.mod":
            return {"dependencies": re.findall(r"^\s*([\w./-]+)\s+v[\w.-]+", content, re.MULTILINE)}
        if "dockerfile" == name:
            return {"containers": ["Docker"], "base_images": re.findall(r"^FROM\s+([^\s]+)", content, re.MULTILINE)}
        if path.suffix.lower() in {".yml", ".yaml", ".tf"} or name in {".gitlab-ci.yml", "jenkinsfile"}:
            return {"infrastructure": self._infrastructure_hints(path, content)}
        return {"dependencies": []}

    def detect(self, dependency_names: Iterable[str], content_blobs: Iterable[str]) -> Dict[str, List[str]]:
        """Detect technologies from dependencies and content."""

        haystack = "\n".join(list(dependency_names) + list(content_blobs)).lower()
        detected: Dict[str, List[str]] = {}
        for category, signatures in TECH_SIGNATURES.items():
            matches = []
            for label, tokens in signatures.items():
                if any(token.lower() in haystack for token in tokens):
                    matches.append(label)
            detected[category] = sorted(set(matches))
        detected["apis"] = self.detect_apis(haystack)
        return detected

    def detect_apis(self, content: str) -> List[str]:
        """Detect API styles and endpoints from content."""

        apis: Set[str] = set()
        if re.search(r"@(app|router)\.(get|post|put|delete|patch)|app\.(get|post|put|delete|patch)\(", content):
            apis.add("REST routes")
        if "graphql" in content or "type query" in content:
            apis.add("GraphQL")
        if "grpc" in content or "service " in content and "rpc " in content:
            apis.add("gRPC")
        if "websocket" in content or "socket.io" in content:
            apis.add("WebSocket")
        return sorted(apis)

    def _json_dependencies(self, content: str) -> Dict[str, Any]:
        data = json.loads(content)
        dependencies: Dict[str, Any] = {}
        for key in ("dependencies", "devDependencies", "peerDependencies", "require", "require-dev"):
            value = data.get(key, {})
            if isinstance(value, dict):
                dependencies.update(value)
        return {"dependencies": sorted(dependencies)}

    def _line_dependencies(self, content: str) -> List[str]:
        deps = []
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("source "):
                continue
            deps.append(re.split(r"[<>=~\s]", line, maxsplit=1)[0].strip("'\""))
        return deps

    def _toml_dependencies(self, content: str) -> Dict[str, Any]:
        data = tomllib.loads(content)
        deps: Set[str] = set()
        for section in ("dependencies", "dev-dependencies"):
            value = data.get(section, {})
            if isinstance(value, dict):
                deps.update(value)
        project = data.get("project", {})
        if isinstance(project, dict):
            deps.update(str(item).split("=", 1)[0].strip() for item in project.get("dependencies", []))
        tool = data.get("tool", {})
        poetry = tool.get("poetry", {}) if isinstance(tool, dict) else {}
        if isinstance(poetry, dict):
            deps.update(poetry.get("dependencies", {}).keys())
        return {"dependencies": sorted(deps)}

    def _xml_dependencies(self, content: str) -> Dict[str, Any]:
        deps: Set[str] = set()
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return {"dependencies": []}
        for element in root.iter():
            artifact = element.findtext("artifactId")
            include = element.attrib.get("Include")
            package_id = element.attrib.get("id")
            for value in (artifact, include, package_id):
                if value:
                    deps.add(value)
        return {"dependencies": sorted(deps)}

    def _infrastructure_hints(self, path: Path, content: str) -> List[str]:
        hints = []
        lower = content.lower()
        if "github/workflows" in path.as_posix() or "on:" in lower and "jobs:" in lower:
            hints.append("GitHub Actions")
        if "gitlab-ci" in path.name:
            hints.append("GitLab CI")
        if "jenkinsfile" in path.name.lower():
            hints.append("Jenkins")
        if "apiVersion:" in content:
            hints.append("Kubernetes")
        if "resource " in lower or path.suffix.lower() == ".tf":
            hints.append("Terraform")
        return sorted(set(hints))

