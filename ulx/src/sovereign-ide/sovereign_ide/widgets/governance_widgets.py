from __future__ import annotations

import json
from typing import Any, Iterable

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QFrame,
        QHBoxLayout,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPlainTextEdit,
        QSplitter,
        QTabWidget,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover
    Qt = None
    QFrame = object
    QHBoxLayout = object
    QLabel = object
    QListWidget = object
    QListWidgetItem = object
    QPlainTextEdit = object
    QSplitter = object
    QTabWidget = object
    QVBoxLayout = object
    QWidget = object

from sovereign_ide.governed_artifacts import (
    load_kernel_conformance,
    load_kernel_endpoint_manifest,
    load_kernel_registry_model,
    load_knowledge_ingest_conformance,
    load_knowledge_ingest_endpoint,
    load_launch_readiness,
    load_specification_dependency_graph,
    load_specification_registry,
    load_standards_traceability_matrix,
)


def _ctx_value(ctx: Any, name: str, default=None):
    getter = getattr(ctx, "get", None)
    if callable(getter):
        return getter(name, default)
    return getattr(ctx, name, default)


def _json_text(payload: Any) -> str:
    try:
        return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    except Exception:
        return str(payload)


def _count_by(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


class _SelectableArtifactPanel(QWidget):
    panel_title = "Artifact"
    panel_subtitle = "Governed artifact panel"
    panel_accent = "#5fb9ff"

    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self._summary = None
        self._items = None
        self._details = None
        self._build_ui()

    def _load_payload(self) -> dict[str, Any] | None:
        raise NotImplementedError

    def _summary_text(self, payload: dict[str, Any] | None) -> str:
        return "No payload available."

    def _item_rows(self, payload: dict[str, Any] | None) -> list[tuple[str, str]]:
        return []

    def _detail_text(self, payload: dict[str, Any] | None, item_id: str | None) -> str:
        if payload is None:
            return "Artifact unavailable."
        return _json_text(payload)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.setObjectName("governancePanel")
        self.setStyleSheet(
            f"""
            QWidget#governancePanel {{
                background: #0b1118;
                color: #eef3f8;
            }}
            QFrame#governanceHero {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.06),
                    stop:1 rgba(255,255,255,0.02));
                border: 1px solid rgba(255,255,255,0.08);
                border-left: 3px solid {self.panel_accent};
                border-radius: 18px;
            }}
            QLabel#governancePanelTitle {{
                color: #f7fbff;
                font-size: 18px;
                font-weight: 800;
            }}
            QLabel#governancePanelSubtitle {{
                color: #9dadbe;
                line-height: 1.5;
            }}
            QLabel#governancePanelSummary {{
                color: #d7e2ef;
                font-family: "Consolas", "Cascadia Mono", monospace;
                background: rgba(10, 16, 22, 0.8);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 10px 12px;
            }}
            QFrame#governanceCard {{
                background: rgba(12, 18, 25, 0.92);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
            }}
            QLabel#governanceCardTitle {{
                color: #f4f8fc;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }}
            QListWidget {{
                background: transparent;
                border: 0;
                color: #edf3f8;
                outline: 0;
                padding: 2px;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                margin: 3px 0;
                border-radius: 10px;
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.05);
            }}
            QListWidget::item:selected {{
                background: rgba(95,185,255,0.16);
                border: 1px solid rgba(95,185,255,0.6);
                color: #ffffff;
            }}
            QPlainTextEdit {{
                background: rgba(8, 12, 17, 0.96);
                color: #eaf2fa;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 10px;
                font-family: "Consolas", "Cascadia Mono", monospace;
                selection-background-color: rgba(95,185,255,0.28);
            }}
            """
        )

        title = QLabel(self.panel_title)
        title.setObjectName("governancePanelTitle")
        title.setWordWrap(True)
        subtitle = QLabel(self.panel_subtitle)
        subtitle.setObjectName("governancePanelSubtitle")
        subtitle.setWordWrap(True)

        hero = QFrame()
        hero.setObjectName("governanceHero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(16, 14, 16, 14)
        hero_layout.setSpacing(8)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        self._summary = QLabel("Loading...")
        self._summary.setObjectName("governancePanelSummary")
        self._summary.setWordWrap(True)
        hero_layout.addWidget(self._summary)
        layout.addWidget(hero)

        splitter = QSplitter(Qt.Orientation.Horizontal) if Qt is not None else None

        catalog_card = QFrame()
        catalog_card.setObjectName("governanceCard")
        catalog_layout = QVBoxLayout(catalog_card)
        catalog_layout.setContentsMargins(14, 14, 14, 14)
        catalog_layout.setSpacing(8)
        catalog_title = QLabel("Catalog")
        catalog_title.setObjectName("governanceCardTitle")
        catalog_title.setWordWrap(True)
        catalog_layout.addWidget(catalog_title)
        self._items = QListWidget()
        self._items.currentItemChanged.connect(self._on_selection_changed)
        catalog_layout.addWidget(self._items, 1)

        details_card = QFrame()
        details_card.setObjectName("governanceCard")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(14, 14, 14, 14)
        details_layout.setSpacing(8)
        details_title = QLabel("Selected Record")
        details_title.setObjectName("governanceCardTitle")
        details_title.setWordWrap(True)
        details_layout.addWidget(details_title)
        self._details = QPlainTextEdit()
        self._details.setReadOnly(True)
        self._details.setMinimumHeight(180)
        details_layout.addWidget(self._details, 1)

        if splitter is not None:
            splitter.addWidget(catalog_card)
            splitter.addWidget(details_card)
            splitter.setStretchFactor(0, 1)
            splitter.setStretchFactor(1, 2)
            layout.addWidget(splitter, 1)
        else:
            layout.addWidget(catalog_card, 1)
            layout.addWidget(details_card, 1)
        self.refresh()

    def _selected_item_id(self) -> str | None:
        if self._items is None:
            return None
        current = self._items.currentItem()
        if current is None:
            return None
        return current.data(Qt.ItemDataRole.UserRole) if Qt is not None else current.text()

    def _on_selection_changed(self, current, _previous) -> None:  # noqa: ANN001
        if self._details is None:
            return
        payload = self._load_payload()
        item_id = current.data(Qt.ItemDataRole.UserRole) if current is not None and Qt is not None else None
        self._details.setPlainText(self._detail_text(payload, item_id))

    def refresh(self) -> None:
        payload = self._load_payload()
        if self._summary is not None:
            self._summary.setText(self._summary_text(payload))
        if self._items is None or self._details is None:
            return
        previous = self._selected_item_id()
        self._items.blockSignals(True)
        self._items.clear()
        rows = self._item_rows(payload)
        for item_id, label in rows:
            item = QListWidgetItem(label)
            if Qt is not None:
                item.setData(Qt.ItemDataRole.UserRole, item_id)
            self._items.addItem(item)
        selected_row = 0
        if previous is not None:
            for index, (item_id, _) in enumerate(rows):
                if item_id == previous:
                    selected_row = index
                    break
        if rows:
            self._items.setCurrentRow(selected_row)
            current = self._items.currentItem()
            current_id = current.data(Qt.ItemDataRole.UserRole) if current is not None and Qt is not None else None
            self._details.setPlainText(self._detail_text(payload, current_id))
        else:
            self._details.setPlainText(self._detail_text(payload, None))
        self._items.blockSignals(False)


def _registry_entry(registry: dict[str, Any] | None, entry_id: str) -> dict[str, Any] | None:
    if registry is None:
        return None
    for entry in registry.get("entries", []):
        if entry.get("id") == entry_id:
            return entry
    return None


class SpecificationRegistryPanel(_SelectableArtifactPanel):
    panel_title = "Specification Registry"
    panel_subtitle = "Authoritative inventory of governed artifacts"
    panel_accent = "#5fb9ff"

    def _load_payload(self) -> dict[str, Any] | None:
        return load_specification_registry()

    def _summary_text(self, payload: dict[str, Any] | None) -> str:
        if payload is None:
            return "Specification registry unavailable."
        entries = list(payload.get("entries", []))
        normative = sum(1 for entry in entries if entry.get("classification") == "normative")
        informative = sum(1 for entry in entries if entry.get("classification") == "informative")
        ready = sum(1 for entry in entries if entry.get("launchReadiness") == "ready")
        return f"entries={len(entries)}\nnormative={normative}\ninformative={informative}\nready={ready}"

    def _item_rows(self, payload: dict[str, Any] | None) -> list[tuple[str, str]]:
        if payload is None:
            return []
        entries = sorted(payload.get("entries", []), key=lambda entry: entry.get("id", ""))
        return [
            (
                entry.get("id", ""),
                f"{entry.get('id', '')} | {entry.get('artifactType', '')} | {entry.get('documentStatus', '')} | {entry.get('launchReadiness', '')}",
            )
            for entry in entries
        ]

    def _detail_text(self, payload: dict[str, Any] | None, item_id: str | None) -> str:
        entry = _registry_entry(payload, item_id or "") if item_id else None
        if entry is None:
            return "Select a registry entry to inspect its governed metadata."
        return _json_text(
            {
                "id": entry.get("id"),
                "name": entry.get("name"),
                "artifactType": entry.get("artifactType"),
                "documentStatus": entry.get("documentStatus"),
                "version": entry.get("version"),
                "steward": entry.get("steward"),
                "classification": entry.get("classification"),
                "launchReadiness": entry.get("launchReadiness"),
                "dependencies": entry.get("dependencies", []),
                "evidenceRefs": entry.get("evidenceRefs", []),
                "implementationRefs": entry.get("implementationRefs", []),
                "traceabilityRefs": entry.get("traceabilityRefs", []),
                "notes": entry.get("notes", ""),
            }
        )


class SpecificationDependencyGraphPanel(_SelectableArtifactPanel):
    panel_title = "Specification Dependency Graph"
    panel_subtitle = "Inspect governed artifact relationships and drift edges"
    panel_accent = "#2dd4bf"

    def _load_payload(self) -> dict[str, Any] | None:
        return load_specification_dependency_graph()

    def _summary_text(self, payload: dict[str, Any] | None) -> str:
        if payload is None:
            return "Specification dependency graph unavailable."
        nodes = list(payload.get("nodes", []))
        edges = list(payload.get("edges", []))
        by_type = _count_by(edge.get("type", "") for edge in edges)
        return f"nodes={len(nodes)}\nedges={len(edges)}\ndependsOn={by_type.get('dependsOn', 0)}"

    def _item_rows(self, payload: dict[str, Any] | None) -> list[tuple[str, str]]:
        if payload is None:
            return []
        nodes = sorted(payload.get("nodes", []), key=lambda node: node.get("id", ""))
        return [
            (
                node.get("id", ""),
                f"{node.get('id', '')} | {node.get('artifactType', '')} | {node.get('launchReadiness', '')}",
            )
            for node in nodes
        ]

    def _detail_text(self, payload: dict[str, Any] | None, item_id: str | None) -> str:
        if payload is None or item_id is None:
            return "Select a dependency graph node to inspect its relationships."
        node = next((entry for entry in payload.get("nodes", []) if entry.get("id") == item_id), None)
        if node is None:
            return "Select a dependency graph node to inspect its relationships."
        outgoing = sorted(
            edge.get("to", "")
            for edge in payload.get("edges", [])
            if edge.get("from") == item_id
        )
        incoming = sorted(
            edge.get("from", "")
            for edge in payload.get("edges", [])
            if edge.get("to") == item_id
        )
        return _json_text(
            {
                "node": node,
                "incoming": incoming,
                "outgoing": outgoing,
            }
        )


class LaunchReadinessPanel(_SelectableArtifactPanel):
    panel_title = "Launch Readiness"
    panel_subtitle = "Blockers, evidence, and readiness gates for governed artifacts"
    panel_accent = "#f59e0b"

    def _load_payload(self) -> dict[str, Any] | None:
        return load_launch_readiness()

    def _summary_text(self, payload: dict[str, Any] | None) -> str:
        if payload is None:
            return "Launch readiness unavailable."
        entries = list(payload.get("entries", []))
        ready = sum(1 for entry in entries if entry.get("readiness") == "ready")
        mirror_only = sum(1 for entry in entries if entry.get("readiness") == "mirror-only")
        blockers = sum(len(entry.get("blockers", [])) for entry in entries)
        return f"entries={len(entries)}\nready={ready}\nmirror_only={mirror_only}\nblockers={blockers}"

    def _item_rows(self, payload: dict[str, Any] | None) -> list[tuple[str, str]]:
        if payload is None:
            return []
        entries = sorted(payload.get("entries", []), key=lambda entry: entry.get("artifactId", ""))
        return [
            (
                entry.get("artifactId", ""),
                f"{entry.get('artifactId', '')} | {entry.get('readiness', '')} | blockers={len(entry.get('blockers', []))}",
            )
            for entry in entries
        ]

    def _detail_text(self, payload: dict[str, Any] | None, item_id: str | None) -> str:
        if payload is None or item_id is None:
            return "Select a launch readiness entry to inspect its blockers and evidence."
        entry = next((row for row in payload.get("entries", []) if row.get("artifactId") == item_id), None)
        if entry is None:
            return "Select a launch readiness entry to inspect its blockers and evidence."
        return _json_text(entry)


class StandardsTraceabilityPanel(_SelectableArtifactPanel):
    panel_title = "Standards Traceability"
    panel_subtitle = "Trace requirement statements to governed artifacts"
    panel_accent = "#a78bfa"

    def _load_payload(self) -> dict[str, Any] | None:
        return load_standards_traceability_matrix()

    def _summary_text(self, payload: dict[str, Any] | None) -> str:
        if payload is None:
            return "Traceability matrix unavailable."
        rows = list(payload.get("rows", []))
        status_counts = _count_by(row.get("status", "") for row in rows)
        return (
            f"rows={len(rows)}\n"
            f"traceable={status_counts.get('traceable', 0)}\n"
            f"partial={status_counts.get('partial', 0)}\n"
            f"deferred={status_counts.get('deferred', 0)}"
        )

    def _item_rows(self, payload: dict[str, Any] | None) -> list[tuple[str, str]]:
        if payload is None:
            return []
        rows = sorted(payload.get("rows", []), key=lambda row: row.get("artifactId", ""))
        return [
            (
                row.get("artifactId", ""),
                f"{row.get('artifactId', '')} | {row.get('requirementId', '')} | {row.get('status', '')}",
            )
            for row in rows
        ]

    def _detail_text(self, payload: dict[str, Any] | None, item_id: str | None) -> str:
        if payload is None or item_id is None:
            return "Select a traceability row to inspect its requirements and evidence."
        row = next((entry for entry in payload.get("rows", []) if entry.get("artifactId") == item_id), None)
        if row is None:
            return "Select a traceability row to inspect its requirements and evidence."
        return _json_text(row)


class KnowledgeStorePanel(_SelectableArtifactPanel):
    panel_title = "Governed Knowledge Store"
    panel_subtitle = "Knowledge module governance, ingest surface, and conformance"
    panel_accent = "#34d399"

    def __init__(self, ctx):
        self._bundle_cache: dict[str, Any] | None = None
        super().__init__(ctx)

    def _load_payload(self) -> dict[str, Any] | None:
        registry = load_specification_registry()
        entry = _registry_entry(registry, "governed-knowledge-store")
        endpoint = load_knowledge_ingest_endpoint()
        conformance = load_knowledge_ingest_conformance()
        if entry is None and endpoint is None and conformance is None:
            return None
        return {
            "registry_entry": entry,
            "endpoint": endpoint,
            "conformance": conformance,
        }

    def _summary_text(self, payload: dict[str, Any] | None) -> str:
        if payload is None:
            return "Governed knowledge store unavailable."
        entry = payload.get("registry_entry") or {}
        endpoint = payload.get("endpoint") or {}
        conformance = payload.get("conformance") or {}
        return (
            f"module={entry.get('name', 'Governed Knowledge Store')}\n"
            f"documentStatus={entry.get('documentStatus', 'unknown')}\n"
            f"launchReadiness={entry.get('launchReadiness', 'unknown')}\n"
            f"endpoint={endpoint.get('id', 'knowledge-ingest')}\n"
            f"conformance={conformance.get('artifact', 'knowledge-ingest.endpoint.json')}"
        )

    def _item_rows(self, payload: dict[str, Any] | None) -> list[tuple[str, str]]:
        if payload is None:
            return []
        entry = payload.get("registry_entry")
        endpoint = payload.get("endpoint")
        conformance = payload.get("conformance")
        rows: list[tuple[str, str]] = []
        if entry is not None:
            rows.append(("registry_entry", f"{entry.get('id', '')} | {entry.get('artifactType', '')} | {entry.get('launchReadiness', '')}"))
        if endpoint is not None:
            rows.append(("endpoint", f"{endpoint.get('id', '')} | {endpoint.get('endpoint', {}).get('method', '')} {endpoint.get('endpoint', {}).get('path', '')}"))
        if conformance is not None:
            rows.append(("conformance", f"{conformance.get('$id', conformance.get('artifact', 'knowledge-ingest'))} | conformance"))
        return rows

    def _detail_text(self, payload: dict[str, Any] | None, item_id: str | None) -> str:
        if payload is None or item_id is None:
            return "Select a governed knowledge surface to inspect its governing artifact."
        if item_id == "registry_entry":
            return _json_text(payload.get("registry_entry"))
        if item_id == "endpoint":
            return _json_text(payload.get("endpoint"))
        if item_id == "conformance":
            return _json_text(payload.get("conformance"))
        return "Select a governed knowledge surface to inspect its governing artifact."


class KernelPanel(_SelectableArtifactPanel):
    panel_title = "Sovereign OS Constitutional Kernel"
    panel_subtitle = "CSL, ISL, CIC, CCC, and COE registry model"
    panel_accent = "#fb7185"

    def _load_payload(self) -> dict[str, Any] | None:
        registry_model = load_kernel_registry_model()
        endpoint = load_kernel_endpoint_manifest()
        conformance = load_kernel_conformance()
        if registry_model is None and endpoint is None and conformance is None:
            return None
        return {
            "registry_model": registry_model,
            "endpoint": endpoint,
            "conformance": conformance,
        }

    def _summary_text(self, payload: dict[str, Any] | None) -> str:
        if payload is None:
            return "Kernel specification unavailable."
        registry_model = payload.get("registry_model") or {}
        layers = list(registry_model.get("layers", []))
        return (
            f"kernel={registry_model.get('kernel', 'Sovereign OS Constitutional Kernel v1.0')}\n"
            f"layers={len(layers)}\n"
            f"documentStatus={registry_model.get('documentStatus', 'unknown')}\n"
            f"launchReadiness={registry_model.get('launchReadiness', 'unknown')}"
        )

    def _item_rows(self, payload: dict[str, Any] | None) -> list[tuple[str, str]]:
        if payload is None:
            return []
        rows: list[tuple[str, str]] = []
        registry_model = payload.get("registry_model")
        endpoint = payload.get("endpoint")
        conformance = payload.get("conformance")
        if registry_model is not None:
            rows.append(("registry_model", f"{registry_model.get('id', '')} | registry model"))
            for layer in registry_model.get("layers", []):
                rows.append((f"layer:{layer.get('id', '')}", f"{layer.get('id', '')} | {layer.get('name', '')}"))
        if endpoint is not None:
            rows.append(("endpoint", f"{endpoint.get('id', '')} | {endpoint.get('endpoint', {}).get('method', '')} {endpoint.get('endpoint', {}).get('path', '')}"))
        if conformance is not None:
            rows.append(("conformance", f"{conformance.get('artifact_id', conformance.get('$id', 'conformance'))} | conformance"))
        return rows

    def _detail_text(self, payload: dict[str, Any] | None, item_id: str | None) -> str:
        if payload is None or item_id is None:
            return "Select a kernel surface to inspect its governing artifact."
        registry_model = payload.get("registry_model")
        endpoint = payload.get("endpoint")
        conformance = payload.get("conformance")
        if item_id == "registry_model":
            return _json_text(registry_model)
        if item_id == "endpoint":
            return _json_text(endpoint)
        if item_id == "conformance":
            return _json_text(conformance)
        if item_id.startswith("layer:") and registry_model is not None:
            layer_id = item_id.split(":", 1)[1]
            layer = next((entry for entry in registry_model.get("layers", []) if entry.get("id") == layer_id), None)
            return _json_text(layer)
        return "Select a kernel surface to inspect its governing artifact."


class GovernanceBrowserWidget(QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self._summary = None
        self._tabs = None
        self._panels: list[_SelectableArtifactPanel] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        self.setObjectName("governanceBrowser")
        self.setStyleSheet(
            """
            QWidget#governanceBrowser {
                background: #091018;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
                margin-top: 6px;
                background: rgba(8, 13, 19, 0.96);
            }
            QTabBar::tab {
                background: rgba(255,255,255,0.03);
                color: #cdd8e3;
                border: 1px solid rgba(255,255,255,0.08);
                border-bottom: 0;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                padding: 9px 14px;
                margin-right: 4px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: rgba(95,185,255,0.16);
                color: #ffffff;
                border-color: rgba(95,185,255,0.65);
            }
            QTabBar::tab:hover {
                background: rgba(255,255,255,0.06);
            }
            QLabel#governanceBrowserSummary {
                background: rgba(255,255,255,0.03);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 12px 14px;
                color: #d7e3ef;
                font-family: "Consolas", "Cascadia Mono", monospace;
            }
            """
        )

        title = QLabel("Governed Module Browser")
        title.setWordWrap(True)
        subtitle = QLabel("Unified browser for the registry, dependency graph, readiness, traceability, knowledge store, and kernel")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self._summary = QLabel(self._summary_text())
        self._summary.setObjectName("governanceBrowserSummary")
        self._summary.setWordWrap(True)
        layout.addWidget(self._summary)

        tabs = QTabWidget()
        self._tabs = tabs
        self._panels = [
            SpecificationRegistryPanel(self.ctx),
            SpecificationDependencyGraphPanel(self.ctx),
            LaunchReadinessPanel(self.ctx),
            StandardsTraceabilityPanel(self.ctx),
            KnowledgeStorePanel(self.ctx),
            KernelPanel(self.ctx),
        ]
        for panel in self._panels:
            tabs.addTab(panel, panel.panel_title)
        layout.addWidget(tabs, 1)

    def _summary_text(self) -> str:
        registry = load_specification_registry()
        dependency = load_specification_dependency_graph()
        readiness = load_launch_readiness()
        traceability = load_standards_traceability_matrix()
        kernel = load_kernel_registry_model()
        if registry is None:
            return "Governed browser unavailable."
        return (
            f"registry_entries={len(registry.get('entries', []))}\n"
            f"dependency_nodes={len((dependency or {}).get('nodes', []))}\n"
            f"readiness_entries={len((readiness or {}).get('entries', []))}\n"
            f"traceability_rows={len((traceability or {}).get('rows', []))}\n"
            f"kernel_layers={len((kernel or {}).get('layers', []))}"
        )

    def refresh(self) -> None:
        if self._summary is not None:
            self._summary.setText(self._summary_text())
        for panel in self._panels:
            panel.refresh()
