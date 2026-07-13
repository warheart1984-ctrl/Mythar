from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Any


class GovernanceDSLParseError(RuntimeError):
    pass


@dataclass(frozen=True)
class GovernanceDecisionSpec:
    decision_id: str
    substrate_id: str
    action: str
    target: str
    reason: str
    requires: tuple[str, ...]
    effects: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_DECISION_HEADER = re.compile(r"^decision\s+([a-zA-Z0-9_-]+)\s*\{$")
_SUBSTRATE = re.compile(r"^substrate\s+([a-z0-9]+(?:-[a-z0-9]+)*)$")
_ACTION = re.compile(r"^action\s+([a-zA-Z0-9_-]+)$")
_TARGET = re.compile(r"^target\s+([a-zA-Z0-9_-]+)$")
_REASON = re.compile(r'^reason\s+"(.*)"$')
_SECTION_HEADER = re.compile(r"^(requires|effects)\s*\{$")


def _clean_lines(source: str) -> list[str]:
    lines: list[str] = []
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        lines.append(line)
    return lines


def parse_governance_dsl(source: str) -> GovernanceDecisionSpec:
    lines = _clean_lines(source)
    if not lines:
        raise GovernanceDSLParseError("DSL program is empty")
    if len(lines) < 3:
        raise GovernanceDSLParseError("DSL program is incomplete")

    header = _DECISION_HEADER.match(lines[0])
    if not header:
        raise GovernanceDSLParseError("decision header is invalid")
    decision_id = header.group(1)

    substrate_id = ""
    action = ""
    target = ""
    reason = ""
    requires: list[str] = []
    effects: list[str] = []

    i = 1
    active_section: list[str] | None = None
    while i < len(lines):
        line = lines[i]
        if line == "}":
            break
        section = _SECTION_HEADER.match(line)
        if section:
            section_name = section.group(1)
            active_section = requires if section_name == "requires" else effects
            i += 1
            while i < len(lines) and lines[i] != "}":
                active_section.append(lines[i])
                i += 1
            if i >= len(lines):
                raise GovernanceDSLParseError(f"unterminated {section_name} block")
            active_section = None
            i += 1
            continue

        substrate_match = _SUBSTRATE.match(line)
        if substrate_match:
            substrate_id = substrate_match.group(1)
            i += 1
            continue
        action_match = _ACTION.match(line)
        if action_match:
            action = action_match.group(1)
            i += 1
            continue
        target_match = _TARGET.match(line)
        if target_match:
            target = target_match.group(1)
            i += 1
            continue
        reason_match = _REASON.match(line)
        if reason_match:
            reason = reason_match.group(1)
            i += 1
            continue
        raise GovernanceDSLParseError(f"unrecognized DSL line: {line!r}")

    if not substrate_id:
        raise GovernanceDSLParseError("substrate is required")
    if not action:
        raise GovernanceDSLParseError("action is required")
    if not target:
        raise GovernanceDSLParseError("target is required")
    if not reason:
        raise GovernanceDSLParseError("reason is required")

    return GovernanceDecisionSpec(
        decision_id=decision_id,
        substrate_id=substrate_id,
        action=action,
        target=target,
        reason=reason,
        requires=tuple(requires),
        effects=tuple(effects),
    )


def load_governance_dsl(path: Path) -> GovernanceDecisionSpec:
    return parse_governance_dsl(path.read_text(encoding="utf-8"))

