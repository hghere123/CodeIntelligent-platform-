"""Detector tests."""

from pathlib import Path

from utils.detector import ConfigurationAnalyzer


def test_package_json_detection() -> None:
    """Detector parses package dependencies and finds frameworks."""

    analyzer = ConfigurationAnalyzer()
    facts = analyzer.analyze_file(Path("package.json"), '{"dependencies":{"react":"latest","express":"latest","openai":"latest"}}')
    detected = analyzer.detect(facts["dependencies"], [])
    assert "React" in detected["frameworks"]
    assert "Express" in detected["frameworks"]
    assert "OpenAI" in detected["ai_ml"]


def test_infrastructure_and_api_detection() -> None:
    """Detector identifies Kubernetes and REST routes."""

    analyzer = ConfigurationAnalyzer()
    detected = analyzer.detect([], ["apiVersion: apps/v1\nkind: Deployment\n@app.get('/health')"])
    assert "Kubernetes" in detected["containers"]
    assert "REST routes" in detected["apis"]

