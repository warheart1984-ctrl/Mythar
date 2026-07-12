from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from PyQt6.QtCore import QFileSystemWatcher, Qt
    from PyQt6.QtWidgets import (
        QApplication,
        QDockWidget,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QPushButton,
        QSplitter,
        QStackedWidget,
        QTextEdit,
        QTreeWidget,
        QTreeWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover
    QApplication = None
    QFileSystemWatcher = object
    Qt = None
    QDockWidget = object
    QFrame = object
    QHBoxLayout = object
    QLabel = object
    QMainWindow = object
    QPushButton = object
    QSplitter = object
    QStackedWidget = object
    QTextEdit = object
    QTreeWidget = object
    QTreeWidgetItem = object
    QVBoxLayout = object
    QWidget = object

from sovereign_ide.widgets import (
    AAISProjectionPanel,
    CEPPipelineView,
    ConstitutionEditor,
    DetailPanel,
    GovernanceBrowserWidget,
    PrimeArchitectPanel,
    RoutingBrainView,
    TimelineWidget,
)
from sovereign_ide import governed_artifacts


def _load_aais_projection_from_env() -> dict[str, object] | None:
    projection_path = os.environ.get("ULX_AAIS_PROJECTION_PATH", "").strip()
    if not projection_path:
        return None
    path = Path(projection_path)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(payload, dict):
        return payload
    return None


class SovereignIDEWindow(QMainWindow):
    def __init__(self, ctx):
        if QApplication is None:
            self.ctx = ctx
            self.visible = False
            return

        app = QApplication.instance() or QApplication([])
        self._app = app
        super().__init__()
        self.ctx = ctx
        self._stack = None
        self._nav = None
        self._detail_panel = None
        self._aais_panel = None
        self._governance_browser = None
        self._governance_watcher = None
        self._console = None
        self._summary_label = None
        self._pages: dict[str, QWidget] = {}
        self.setWindowTitle("Sovereign IDE")
        self.resize(1760, 1080)
        self._build_ui()
        self._install_governance_watcher()

    def _ctx_value(self, name: str, default=None):
        getter = getattr(self.ctx, "get", None)
        if callable(getter):
            return getter(name, default)
        return getattr(self.ctx, name, default)

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        header = QFrame()
        header.setObjectName("sovereignHeader")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(8)
        eyebrow = QLabel("Sovereign IDE")
        eyebrow.setObjectName("sovereignEyebrow")
        title = QLabel("Constitutional multi-agent workspace with CEP, routing, and replay")
        title.setObjectName("sovereignTitle")
        title.setWordWrap(True)
        self._summary_label = QLabel("\n".join(self._summary_lines()))
        self._summary_label.setObjectName("sovereignSummary")
        self._summary_label.setWordWrap(True)
        controls = self._build_controls()
        header_layout.addWidget(eyebrow)
        header_layout.addWidget(title)
        header_layout.addWidget(self._summary_label)
        header_layout.addLayout(controls)
        root_layout.addWidget(header)

        stack = QStackedWidget()
        self._stack = stack
        timeline_page = TimelineWidget(self.ctx)
        routing_page = RoutingBrainView(self.ctx)
        cep_page = CEPPipelineView(self.ctx)
        constitution_page = QWidget()
        constitution_layout = QVBoxLayout(constitution_page)
        constitution_layout.setContentsMargins(0, 0, 0, 0)
        constitution_layout.setSpacing(12)
        constitution_editor = ConstitutionEditor(self.ctx)
        architect_panel = PrimeArchitectPanel(self.ctx)
        constitution_layout.addWidget(constitution_editor, 1)
        constitution_layout.addWidget(architect_panel, 1)
        constitution_page.refresh = lambda: (constitution_editor.refresh(), architect_panel.refresh())  # type: ignore[attr-defined]

        governance_page = GovernanceBrowserWidget(self.ctx)
        self._governance_browser = governance_page

        self._pages = {
            "timeline": timeline_page,
            "routing": routing_page,
            "cep": cep_page,
            "constitution": constitution_page,
            "governance": governance_page,
        }
        for page in self._pages.values():
            stack.addWidget(page)
        root_layout.addWidget(stack, 1)
        self.setCentralWidget(root)

        nav = QTreeWidget()
        nav.setHeaderHidden(True)
        self._nav = nav
        self._populate_nav()
        nav.itemClicked.connect(self._on_nav_clicked)
        nav_dock = QDockWidget("Navigation", self)
        nav_dock.setWidget(nav)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, nav_dock)

        detail_panel = DetailPanel(self.ctx)
        self._detail_panel = detail_panel
        detail_dock = QDockWidget("Details", self)
        detail_dock.setWidget(detail_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, detail_dock)

        aais_panel = AAISProjectionPanel(self.ctx)
        self._aais_panel = aais_panel
        aais_dock = QDockWidget("AAIS", self)
        aais_dock.setWidget(aais_panel)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, aais_dock)
        self.tabifyDockWidget(detail_dock, aais_dock)
        aais_dock.raise_()

        console = QTextEdit()
        console.setReadOnly(True)
        self._console = console
        console_dock = QDockWidget("Console", self)
        console_dock.setWidget(console)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, console_dock)

        self._select_page("timeline")
        self.sync_runtime()

    def _build_controls(self):
        row = QHBoxLayout()
        row.setSpacing(8)
        for label, page_key in [
            ("Timeline Mode", "timeline"),
            ("Graph Mode", "routing"),
            ("CEP Pipeline", "cep"),
            ("Constitution Editor", "constitution"),
            ("Governance Browser", "governance"),
        ]:
            button = QPushButton(label)
            button.clicked.connect(lambda _checked=False, key=page_key: self._select_page(key))
            row.addWidget(button)
        step_button = QPushButton("Advance loop")
        step_button.clicked.connect(self.advance_loop)
        row.addWidget(step_button)
        sync_button = QPushButton("Sync runtime")
        sync_button.clicked.connect(self.sync_runtime)
        row.addWidget(sync_button)
        row.addStretch(1)
        return row

    def _summary_lines(self) -> list[str]:
        if hasattr(self.ctx, "summary_lines"):
            return list(self.ctx.summary_lines())
        codex = self._ctx_value("codex")
        federation = self._ctx_value("federation")
        return [
            f"codex.base={getattr(codex, 'base', None)}",
            f"codex.constitution_loaded={bool(getattr(codex, 'constitution', {}))}",
            f"federation.bootstrapped={getattr(federation, 'bootstrapped', False)}",
        ]

    def _populate_nav(self) -> None:
        if self._nav is None:
            return
        structure = {
            "Constitutional Spine": ["Constitution", "Invariants", "Evidence Layer", "Lineage Layer", "Drift Gates", "Conformance Suites"],
            "CEP": ["Promotion Requests", "Replay Jobs", "Conformance Jobs", "Decisions Ledger", "CEP Audit Stream"],
            "Sovereign Layer": ["Sovereigns", "Agents", "Routing Brain", "Audit Surfaces", "Treasury"],
            "Temporal Layer": ["Timelines", "Replay Windows", "Temporal Promotion"],
            "Governed Modules": [
                "Governance Browser",
                "Specification Registry",
                "Specification Dependency Graph",
                "Launch Readiness",
                "Standards Traceability",
                "Knowledge Store",
                "Kernel Spec",
            ],
            "Cosmology Layer": ["Singularity Field", "Multiversal Registry", "Fractal Constitution"],
        }
        for root_label, children in structure.items():
            root_item = QTreeWidgetItem([root_label])
            for child in children:
                root_item.addChild(QTreeWidgetItem([child]))
            self._nav.addTopLevelItem(root_item)
        self._nav.expandAll()

    def _page_for_label(self, label: str) -> str:
        governance_labels = {
            "Governance Browser",
            "Specification Registry",
            "Specification Dependency Graph",
            "Launch Readiness",
            "Standards Traceability",
            "Knowledge Store",
            "Kernel Spec",
        }
        constitution_labels = {
            "Constitution",
            "Invariants",
            "Evidence Layer",
            "Lineage Layer",
            "Drift Gates",
            "Conformance Suites",
            "Cosmology Layer",
            "Singularity Field",
            "Multiversal Registry",
            "Fractal Constitution",
        }
        if label in governance_labels:
            return "governance"
        if label in constitution_labels:
            return "constitution"
        if label in {"Promotion Requests", "Replay Jobs", "Conformance Jobs", "Decisions Ledger", "CEP Audit Stream", "CEP"}:
            return "cep"
        if label in {"Sovereigns", "Agents", "Routing Brain", "Audit Surfaces", "Treasury"}:
            return "routing"
        return "timeline"

    def _select_page(self, key: str) -> None:
        if self._stack is None or key not in self._pages:
            return
        self._stack.setCurrentWidget(self._pages[key])
        if self._detail_panel is not None:
            self._detail_panel.refresh()

    def _on_nav_clicked(self, item, _column) -> None:  # noqa: ANN001
        if item is None:
            return
        self._select_page(self._page_for_label(item.text(0)))
        if self._detail_panel is not None:
            self._detail_panel.refresh()

    def _refresh_aais_projection(self) -> None:
        projection_path = os.environ.get("ULX_AAIS_PROJECTION_PATH", "").strip()
        if not projection_path:
            return
        setattr(self.ctx, "aais_projection", _load_aais_projection_from_env())

    def _install_governance_watcher(self) -> None:
        if QFileSystemWatcher is object:
            return
        watcher = QFileSystemWatcher(self)
        watched_paths: list[str] = []
        if governed_artifacts.CONSTITUTIONAL_ROOT.exists():
            watched_paths.append(str(governed_artifacts.CONSTITUTIONAL_ROOT))
        aais_projection_path = os.environ.get("ULX_AAIS_PROJECTION_PATH", "").strip()
        if aais_projection_path and Path(aais_projection_path).exists():
            watched_paths.append(aais_projection_path)
        if not watched_paths:
            return
        watcher.addPaths(watched_paths)
        watcher.directoryChanged.connect(self._on_governance_source_changed)
        watcher.fileChanged.connect(self._on_governance_source_changed)
        self._governance_watcher = watcher

    def _on_governance_source_changed(self, _path: str) -> None:
        if self._governance_watcher is not None:
            watched_paths = list(self._governance_watcher.files()) + list(self._governance_watcher.directories())
            if watched_paths:
                self._governance_watcher.addPaths([path for path in watched_paths if path not in self._governance_watcher.files() and path not in self._governance_watcher.directories()])
        self.sync_runtime()

    def sync_runtime(self) -> None:
        self._refresh_aais_projection()
        if self._summary_label is not None:
            self._summary_label.setText("\n".join(self._summary_lines()))
        for widget in self._pages.values():
            refresh = getattr(widget, "refresh", None)
            if callable(refresh):
                refresh()
        if self._detail_panel is not None:
            self._detail_panel.refresh()
        if self._aais_panel is not None:
            refresh = getattr(self._aais_panel, "refresh", None)
            if callable(refresh):
                refresh()
        if self._console is not None:
            lines = list(self._summary_lines())
            cep = self._ctx_value("cep")
            agent_loop = self._ctx_value("agent_loop")
        if cep is not None:
            lines.append(f"cep.pending_proposals={len(getattr(cep, 'pending_proposals', []))}")
            lines.append(f"cep.decisions={len(getattr(cep, 'decision_log', []))}")
        cep_client = self._ctx_value("cep_client")
        temporal_api = self._ctx_value("temporal_api")
        if cep_client is not None:
            lines.append(f"cep.client_loaded={True}")
        if temporal_api is not None:
            lines.append(f"temporal.replay_store={len(getattr(getattr(temporal_api, 'replay_store', None), '_frames', {}))}")
        if agent_loop is not None:
            lines.append(f"agents={len(getattr(agent_loop, 'agents', []))}")
            lines.append(f"time={getattr(agent_loop, 'time', 0)}")
            self._console.setPlainText("\n".join(lines))

    def advance_loop(self) -> None:
        agent_loop = self._ctx_value("agent_loop")
        if agent_loop is None:
            return
        agent_loop.step()
        self.sync_runtime()

    def show(self):  # type: ignore[override]
        if QApplication is None:
            self.visible = True
            print("[SovereignIDEWindow] PyQt6 unavailable; shell shown in fallback mode.")
            return None
        super().show()
        self.raise_()
        self.activateWindow()
        return self
