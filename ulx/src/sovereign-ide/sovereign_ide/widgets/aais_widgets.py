from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from PyQt6.QtCore import Qt
    from PyQt6.QtWidgets import (
        QFrame,
        QLabel,
        QListWidget,
        QListWidgetItem,
        QPlainTextEdit,
        QSplitter,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover
    Qt = None
    QFrame = object
    QLabel = object
    QListWidget = object
    QListWidgetItem = object
    QPlainTextEdit = object
    QSplitter = object
    QVBoxLayout = object
    QWidget = object


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


def _load_projection_from_env() -> dict[str, Any] | None:
    projection_path = os.environ.get("ULX_AAIS_PROJECTION_PATH", "").strip()
    if not projection_path:
        return None
    path = Path(projection_path)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _projection_from_ctx(ctx: Any) -> dict[str, Any] | None:
    projection = _ctx_value(ctx, "aais_projection")
    if projection is not None:
        return projection
    return _load_projection_from_env()


def _projection_lines(projection: dict[str, Any] | None) -> list[str]:
    if projection is None:
        return [
            "AAIS projection unavailable.",
            "Set ctx.aais_projection or ULX_AAIS_PROJECTION_PATH to render the live catalog.",
        ]

    capabilities = list(projection.get("capabilities", []))
    coding = list(projection.get("codingCapabilities", []))
    provenance = projection.get("provenance", {})
    records = list(provenance.get("records", [])) if isinstance(provenance, dict) else []

    lines = [
        "AAIS projection present.",
        f"Capabilities: {len(capabilities)}",
        f"Coding capabilities: {len(coding)}",
        f"Provenance records: {len(records)}",
        "",
        "Capabilities:",
    ]
    lines.extend(f"- {item.get('name', item.get('id', 'unknown'))} [{item.get('kind', 'unknown')}]" for item in capabilities[:5])
    lines.append("")
    lines.append("Coding capabilities:")
    lines.extend(f"- {item.get('name', 'unknown')}: {item.get('description', '')}" for item in coding[:5])
    lines.append("")
    lines.append("Provenance:")
    lines.extend(
        f"- {item.get('capabilityName', 'unknown')} | model={item.get('model', 'unknown')} | files={len(item.get('filesChanged', []))}"
        for item in records[:5]
    )
    return lines


def _projection_counts(projection: dict[str, Any] | None) -> dict[str, int]:
    if projection is None:
        return {"capabilities": 0, "coding": 0, "provenance": 0}
    capabilities = list(projection.get("capabilities", []))
    coding = list(projection.get("codingCapabilities", []))
    provenance = projection.get("provenance", {})
    records = list(provenance.get("records", [])) if isinstance(provenance, dict) else []
    return {
        "capabilities": len(capabilities),
        "coding": len(coding),
        "provenance": len(records),
    }


def _projection_catalog_rows(projection: dict[str, Any] | None) -> list[tuple[str, str]]:
    if projection is None:
        return []
    rows: list[tuple[str, str]] = []
    for index, item in enumerate(list(projection.get("capabilities", []))[:8]):
        rows.append(
            (
                f"capability:{index}",
                f"{item.get('name', item.get('id', 'unknown'))} | {item.get('kind', 'unknown')}",
            )
        )
    for index, item in enumerate(list(projection.get("codingCapabilities", []))[:8]):
        rows.append(
            (
                f"coding:{index}",
                f"{item.get('name', 'unknown')} | {item.get('id', 'unknown')}",
            )
        )
    provenance = projection.get("provenance", {})
    records = list(provenance.get("records", [])) if isinstance(provenance, dict) else []
    for index, item in enumerate(records[:8]):
        rows.append(
            (
                f"provenance:{index}",
                f"{item.get('capabilityName', 'unknown')} | model={item.get('model', 'unknown')}",
            )
        )
    return rows


def _projection_detail_text(projection: dict[str, Any] | None, item_id: str | None) -> str:
    if projection is None:
        return "Select a projection record to inspect its details."
    if item_id is None:
        return "Select a projection record to inspect its details."
    if item_id.startswith("capability:"):
        index = int(item_id.split(":", 1)[1])
        capabilities = list(projection.get("capabilities", []))
        if index < len(capabilities):
            return _json_text(capabilities[index])
    if item_id.startswith("coding:"):
        index = int(item_id.split(":", 1)[1])
        coding = list(projection.get("codingCapabilities", []))
        if index < len(coding):
            return _json_text(coding[index])
    if item_id.startswith("provenance:"):
        index = int(item_id.split(":", 1)[1])
        provenance = projection.get("provenance", {})
        records = list(provenance.get("records", [])) if isinstance(provenance, dict) else []
        if index < len(records):
            return _json_text(records[index])
    return "Select a projection record to inspect its details."


class AAISProjectionPanel(QWidget):
    panel_title = "AAIS Projection"
    panel_subtitle = "Capability registry, coding catalog, and provenance graph"
    panel_accent = "#60a5fa"

    def __init__(self, ctx: Any):
        super().__init__()
        self.ctx = ctx
        self._summary = None
        self._items = None
        self._details = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        self.setObjectName("aaisPanel")
        self.setStyleSheet(
            f"""
            QWidget#aaisPanel {{
                background: #091018;
                color: #eef3f8;
            }}
            QFrame#aaisHero {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(255,255,255,0.06),
                    stop:1 rgba(255,255,255,0.02));
                border: 1px solid rgba(255,255,255,0.08);
                border-left: 3px solid {self.panel_accent};
                border-radius: 18px;
            }}
            QLabel#aaisPanelTitle {{
                color: #f7fbff;
                font-size: 18px;
                font-weight: 800;
            }}
            QLabel#aaisPanelSubtitle {{
                color: #9dadbe;
                line-height: 1.5;
            }}
            QLabel#aaisPanelSummary {{
                color: #d7e2ef;
                font-family: "Consolas", "Cascadia Mono", monospace;
                background: rgba(10, 16, 22, 0.8);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 10px 12px;
            }}
            QFrame#aaisCard {{
                background: rgba(12, 18, 25, 0.92);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 16px;
            }}
            QLabel#aaisCardTitle {{
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
                background: rgba(96,165,250,0.16);
                border: 1px solid rgba(96,165,250,0.6);
                color: #ffffff;
            }}
            QPlainTextEdit {{
                background: rgba(8, 12, 17, 0.96);
                color: #eaf2fa;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 10px;
                font-family: "Consolas", "Cascadia Mono", monospace;
                selection-background-color: rgba(96,165,250,0.28);
            }}
            """
        )

        hero = QFrame()
        hero.setObjectName("aaisHero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(16, 14, 16, 14)
        hero_layout.setSpacing(8)

        title = QLabel(self.panel_title)
        title.setObjectName("aaisPanelTitle")
        title.setWordWrap(True)
        subtitle = QLabel(self.panel_subtitle)
        subtitle.setObjectName("aaisPanelSubtitle")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)

        self._summary = QLabel(self._summary_text())
        self._summary.setObjectName("aaisPanelSummary")
        self._summary.setWordWrap(True)
        hero_layout.addWidget(self._summary)
        layout.addWidget(hero)

        body = QSplitter(Qt.Orientation.Horizontal) if Qt is not None else None

        catalog_card = QFrame()
        catalog_card.setObjectName("aaisCard")
        catalog_layout = QVBoxLayout(catalog_card)
        catalog_layout.setContentsMargins(14, 14, 14, 14)
        catalog_layout.setSpacing(8)
        catalog_title = QLabel("Catalog")
        catalog_title.setObjectName("aaisCardTitle")
        catalog_title.setWordWrap(True)
        catalog_layout.addWidget(catalog_title)
        self._items = QListWidget()
        self._items.currentItemChanged.connect(self._on_selection_changed)
        catalog_layout.addWidget(self._items, 1)

        details_card = QFrame()
        details_card.setObjectName("aaisCard")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(14, 14, 14, 14)
        details_layout.setSpacing(8)
        details_title = QLabel("Selected Record")
        details_title.setObjectName("aaisCardTitle")
        details_title.setWordWrap(True)
        details_layout.addWidget(details_title)
        self._details = QPlainTextEdit()
        self._details.setReadOnly(True)
        self._details.setMinimumHeight(180)
        details_layout.addWidget(self._details, 1)

        if body is not None:
            body.addWidget(catalog_card)
            body.addWidget(details_card)
            body.setStretchFactor(0, 1)
            body.setStretchFactor(1, 2)
            layout.addWidget(body, 1)
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
        item_id = current.data(Qt.ItemDataRole.UserRole) if current is not None and Qt is not None else None
        self._details.setPlainText(_projection_detail_text(self._projection(), item_id))

    def _projection(self) -> dict[str, Any] | None:
        return _projection_from_ctx(self.ctx)

    def _summary_text(self) -> str:
        counts = _projection_counts(self._projection())
        if sum(counts.values()) == 0:
            return "AAIS projection not loaded."
        return (
            f"capabilities={counts['capabilities']}\n"
            f"coding_capabilities={counts['coding']}\n"
            f"provenance_records={counts['provenance']}"
        )

    def _rebuild_catalog(self, projection: dict[str, Any] | None) -> None:
        if self._items is None:
            return
        rows = _projection_catalog_rows(projection)
        self._items.blockSignals(True)
        self._items.clear()
        for item_id, label in rows:
            item = QListWidgetItem(label)
            if Qt is not None:
                item.setData(Qt.ItemDataRole.UserRole, item_id)
            self._items.addItem(item)
        selected_row = len(rows) - 1 if rows else 0
        if rows:
            self._items.setCurrentRow(selected_row)
        self._items.blockSignals(False)

    def refresh(self) -> None:
        projection = self._projection()
        if self._summary is not None:
            self._summary.setText(self._summary_text())
        self._rebuild_catalog(projection)
        if self._details is not None:
            current = self._selected_item_id()
            self._details.setPlainText(_projection_detail_text(projection, current))
