from __future__ import annotations

import json
import shutil
import time

try:
    from PyQt6.QtWidgets import QApplication
except Exception:  # pragma: no cover
    QApplication = None

from sovereign_ide import governed_artifacts
from sovereign_ide.app import build_runtime
from ui.shell.sovereign_ide_window import SovereignIDEWindow


def test_sovereign_ide_window_builds_canonical_panes() -> None:
    if QApplication is None:
        return

    runtime = build_runtime()
    app = QApplication.instance() or QApplication([])
    window = SovereignIDEWindow(runtime["ctx"])

    assert window._nav is not None
    assert window._stack is not None
    assert window._detail_panel is not None
    assert window._console is not None
    assert window._stack.count() == 5
    assert window.windowTitle() == "Sovereign IDE"


def test_sovereign_ide_window_renders_aais_projection_panel() -> None:
    if QApplication is None:
        return

    runtime = build_runtime()
    runtime["ctx"].aais_projection = {
        "capabilities": [
            {
                "id": "capability-discovery-engine",
                "name": "Capability Discovery Engine",
                "kind": "engine",
                "summary": "Finds the best approved capability for a task.",
            }
        ],
        "codingCapabilities": [
            {
                "id": "RefactorCode",
                "name": "RefactorCode",
                "description": "Refactors existing code while preserving behavior and guarded logic.",
                "inputs": ["target files"],
                "governanceConstraints": ["must preserve tests passing"],
                "routing": {},
            }
        ],
        "provenance": {
            "records": [
                {
                    "capabilityName": "Capability Discovery Engine",
                    "filesChanged": ["packages/aais/src/capabilities.ts"],
                    "testsRan": ["packages/aais/src/AAISRuntime.test.ts"],
                    "model": "qwen-7b",
                    "constraintsApplied": ["must preserve behavior"],
                    "evidence": ["routing catalog"],
                }
            ]
        },
    }

    app = QApplication.instance() or QApplication([])
    window = SovereignIDEWindow(runtime["ctx"])

    assert window._aais_panel is not None
    assert window._aais_panel._summary is not None
    assert window._aais_panel._details is not None
    assert "capabilities=1" in window._aais_panel._summary.text()
    assert "Capability Discovery Engine" in window._aais_panel._details.toPlainText()


def test_sovereign_ide_window_renders_governance_browser() -> None:
    if QApplication is None:
        return

    runtime = build_runtime()
    app = QApplication.instance() or QApplication([])
    window = SovereignIDEWindow(runtime["ctx"])

    assert window._governance_browser is not None
    assert window._governance_browser._tabs is not None
    assert window._governance_browser._tabs.count() == 6
    assert window._governance_browser._summary is not None
    assert "registry_entries=" in window._governance_browser._summary.text()
    assert "Specification Registry" == window._governance_browser._tabs.tabText(0)
    assert "Kernel" in window._governance_browser._tabs.tabText(5)


def test_sovereign_ide_window_refreshes_governance_browser_from_registry_file(tmp_path, monkeypatch) -> None:
    if QApplication is None:
        return

    constitutional_root = tmp_path / "constitutional"
    constitutional_root.mkdir()
    for filename in [
        "specification-registry.json",
        "specification-dependency-graph.json",
        "standards-traceability-matrix.json",
        "launch-readiness.json",
        "knowledge-ingest.endpoint.json",
        "knowledge-ingest.conformance.json",
        "sovereign-os-constitutional-kernel.registry-model.json",
        "sovereign-os-constitutional-kernel.endpoint.json",
        "sovereign-os-constitutional-kernel.conformance.json",
    ]:
        shutil.copy2(
            governed_artifacts.CONSTITUTIONAL_ROOT / filename,
            constitutional_root / filename,
        )

    monkeypatch.setattr(governed_artifacts, "CONSTITUTIONAL_ROOT", constitutional_root)

    registry_path = constitutional_root / "specification-registry.json"
    registry_payload = json.loads(registry_path.read_text(encoding="utf-8"))
    original_entry_count = len(registry_payload.get("entries", []))
    registry_payload["entries"].append(
        {
            "id": "test-fixture-governance-artifact",
            "name": "Test Fixture Governance Artifact",
            "artifactType": "governance-artifact",
            "documentStatus": "published",
            "version": "0.0.1",
            "steward": "ULX Test Harness",
            "classification": "informative",
            "launchReadiness": "preview",
            "dependencies": ["cis-core"],
            "evidenceRefs": ["tests/fixtures/test-fixture-governance-artifact.md"],
            "notes": "Temporary fixture used to prove browser refresh semantics.",
        }
    )
    registry_path.write_text(json.dumps(registry_payload, indent=2), encoding="utf-8")

    runtime = build_runtime()
    app = QApplication.instance() or QApplication([])
    window = SovereignIDEWindow(runtime["ctx"])

    registry_panel = window._governance_browser._tabs.widget(0)
    assert registry_panel is not None
    assert "entries=" in registry_panel._summary.text()
    assert f"entries={original_entry_count + 1}" in registry_panel._summary.text()

    registry_items = [registry_panel._items.item(index).text() for index in range(registry_panel._items.count())]
    assert any("test-fixture-governance-artifact" in text for text in registry_items)
    for index in range(registry_panel._items.count()):
        if "test-fixture-governance-artifact" in registry_panel._items.item(index).text():
            registry_panel._items.setCurrentRow(index)
            break
    assert "test-fixture-governance-artifact" in registry_panel._details.toPlainText()

    registry_payload["entries"].append(
        {
            "id": "test-fixture-governance-artifact-2",
            "name": "Test Fixture Governance Artifact Two",
            "artifactType": "implementation",
            "documentStatus": "published",
            "version": "0.0.2",
            "steward": "ULX Test Harness",
            "classification": "normative",
            "launchReadiness": "ready",
            "dependencies": ["governed-knowledge-store"],
            "evidenceRefs": ["tests/fixtures/test-fixture-governance-artifact-2.md"],
            "notes": "Temporary fixture used to prove browser refresh semantics.",
        }
    )
    registry_path.write_text(json.dumps(registry_payload, indent=2), encoding="utf-8")

    for _ in range(20):
        app.processEvents()
        time.sleep(0.01)

    registry_items = [registry_panel._items.item(index).text() for index in range(registry_panel._items.count())]
    assert any("test-fixture-governance-artifact-2" in text for text in registry_items)
    for index in range(registry_panel._items.count()):
        if "test-fixture-governance-artifact-2" in registry_panel._items.item(index).text():
            registry_panel._items.setCurrentRow(index)
            break
    assert "test-fixture-governance-artifact-2" in registry_panel._details.toPlainText()
    assert f"entries={original_entry_count + 2}" in registry_panel._summary.text()
    assert f"registry_entries={original_entry_count + 2}" in window._governance_browser._summary.text()


def test_sovereign_ide_window_refreshes_aais_projection_from_projection_file(tmp_path, monkeypatch) -> None:
    if QApplication is None:
        return

    projection_path = tmp_path / "aais-projection.json"
    projection_path.write_text(
        json.dumps(
            {
                "capabilities": [
                    {
                        "id": "capability-discovery-engine",
                        "name": "Capability Discovery Engine",
                        "kind": "engine",
                        "summary": "Finds the best approved capability for a task.",
                    }
                ],
                "codingCapabilities": [
                    {
                        "id": "RefactorCode",
                        "name": "RefactorCode",
                        "description": "Refactors existing code while preserving behavior and guarded logic.",
                        "inputs": ["target files"],
                        "governanceConstraints": ["must preserve tests passing"],
                        "routing": {},
                    }
                ],
                "provenance": {
                    "records": [
                        {
                            "capabilityName": "Capability Discovery Engine",
                            "filesChanged": ["packages/aais/src/capabilities.ts"],
                            "testsRan": ["packages/aais/src/AAISRuntime.test.ts"],
                            "model": "qwen-7b",
                            "constraintsApplied": ["must preserve behavior"],
                            "evidence": ["routing catalog"],
                        }
                    ]
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ULX_AAIS_PROJECTION_PATH", str(projection_path))

    runtime = build_runtime()
    app = QApplication.instance() or QApplication([])
    window = SovereignIDEWindow(runtime["ctx"])

    assert window._aais_panel is not None
    assert "capabilities=1" in window._aais_panel._summary.text()
    assert "Capability Discovery Engine" in window._aais_panel._details.toPlainText()

    projection_path.write_text(
        json.dumps(
            {
                "capabilities": [
                    {
                        "id": "capability-discovery-engine",
                        "name": "Capability Discovery Engine",
                        "kind": "engine",
                        "summary": "Finds the best approved capability for a task.",
                    },
                    {
                        "id": "capability-evidence-router",
                        "name": "Evidence Router",
                        "kind": "router",
                        "summary": "Routes evidence to the right governed stores.",
                    },
                ],
                "codingCapabilities": [
                    {
                        "id": "RefactorCode",
                        "name": "RefactorCode",
                        "description": "Refactors existing code while preserving behavior and guarded logic.",
                        "inputs": ["target files"],
                        "governanceConstraints": ["must preserve tests passing"],
                        "routing": {},
                    },
                    {
                        "id": "ReplayLineage",
                        "name": "ReplayLineage",
                        "description": "Replays lineage and verifies constitutional outcomes.",
                        "inputs": ["lineage records"],
                        "governanceConstraints": ["must preserve replay parity"],
                        "routing": {},
                    },
                ],
                "provenance": {
                    "records": [
                        {
                            "capabilityName": "Capability Discovery Engine",
                            "filesChanged": ["packages/aais/src/capabilities.ts"],
                            "testsRan": ["packages/aais/src/AAISRuntime.test.ts"],
                            "model": "qwen-7b",
                            "constraintsApplied": ["must preserve behavior"],
                            "evidence": ["routing catalog"],
                        },
                        {
                            "capabilityName": "Evidence Router",
                            "filesChanged": ["packages/aais/src/routing.ts"],
                            "testsRan": ["packages/aais/src/EvidenceRouter.test.ts"],
                            "model": "qwen-7b",
                            "constraintsApplied": ["must preserve evidence chain"],
                            "evidence": ["replay bundle"],
                        },
                    ]
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    window.sync_runtime()

    assert "capabilities=2" in window._aais_panel._summary.text()
    assert "Evidence Router" in window._aais_panel._details.toPlainText()
