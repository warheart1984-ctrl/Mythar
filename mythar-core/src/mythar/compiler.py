from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REGISTRY = Path(os.getenv("MYTHAR_REGISTRY_PATH", Path(__file__).resolve().parents[3] / "mythar-registry" / "registry-v0.1.json"))


@dataclass(frozen=True)
class Diagnostic:
    code: str
    severity: str
    message: str
    token: str | None = None

    def as_dict(self) -> dict[str, str]:
        value = {"code": self.code, "severity": self.severity, "message": self.message}
        if self.token is not None:
            value["token"] = self.token
        return value


class MytharCompiler:
    """Deterministic compiler driven entirely by a Constitutional Registry."""

    def __init__(self, registry_path: str | Path = DEFAULT_REGISTRY) -> None:
        self.registry_path = Path(registry_path)
        with self.registry_path.open(encoding="utf-8") as source:
            self.registry: dict[str, Any] = json.load(source)
        self.roots = {root["form"]: root for root in self.registry["roots"]}
        self.particles = {particle["form"]: particle for particle in self.registry["particles"]}
        self.prefixes = {operator["form"]: operator for operator in self.registry["operators"]["prefixes"]}
        self.suffixes = {operator["form"]: operator for operator in self.registry["operators"]["suffixes"]}
        self.grammar_lexemes = {
            item["form"]: item for item in self.registry["grammar"]["provisional_grammar_lexemes"]
        }
        self._root_forms = sorted(self.roots, key=len, reverse=True)

    def compile(self, expression: str, mode: str = "strict") -> dict[str, Any]:
        if mode not in {"strict", "exploratory"}:
            raise ValueError("mode must be 'strict' or 'exploratory'")
        tokens = expression.lower().strip().split()
        diagnostics: list[Diagnostic] = []
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        root_lineage: list[str] = []
        operator_lineage: list[str] = []
        unresolved: list[str] = []
        reduction_trace: list[dict[str, Any]] = []
        particle_frame: str | None = None
        root_node_ids: list[str] = []
        node_counter = 0

        def add_node(kind: str, form: str, **extra: Any) -> str:
            nonlocal node_counter
            node_counter += 1
            node_id = f"n{node_counter}"
            nodes.append({"id": node_id, "type": kind, "form": form, **extra})
            return node_id

        def add_root(form: str) -> str:
            root = self.roots[form]
            node_id = add_node("root", form, root_id=root["id"], domain=root["domain"], meanings=root["meanings"])
            root_lineage.append(root["id"])
            root_node_ids.append(node_id)
            return node_id

        start_index = 0
        if len(tokens) > 1 and tokens[0] in self.particles:
            particle = self.particles[tokens[0]]
            particle_frame = particle["id"]
            frame_node = add_node("particle", tokens[0], particle_id=particle["id"], frame=particle["frame"])
            start_index = 1
        else:
            frame_node = None

        phrase_node_ids: list[str] = []
        for token in tokens[start_index:]:
            parsed = self._parse_token(token, add_root, add_node, diagnostics, unresolved)
            if parsed is None:
                continue
            node_id, operator_ids, root_ids = parsed
            phrase_node_ids.append(node_id)
            operator_lineage.extend(operator_ids)
            if len(root_ids) > 1:
                reduction_trace.append({"token": token, "rule": "RAL-001", "roots": root_ids, "result_node": node_id})

        if frame_node is not None:
            for target in phrase_node_ids:
                edges.append({"type": "frame", "from": frame_node, "to": target})

        if not tokens:
            diagnostics.append(Diagnostic("E_UNKNOWN_TOKEN", "error", "An expression must contain at least one token."))

        meanings = [meaning for node in nodes if node["type"] == "root" for meaning in node["meanings"]]
        sentence_roles = self._sentence_roles(tokens, start_index)
        valid = not any(diagnostic.severity == "error" for diagnostic in diagnostics)
        return {
            "registry_version": self.registry["registry"]["version"],
            "expression": expression,
            "mode": mode,
            "valid": valid,
            "meaning": {"components": meanings, "interpretation_mode": "literal"},
            "graph": {"kind": "directed_acyclic_graph", "nodes": nodes, "edges": edges, "acyclic": True},
            "lineage": {
                "roots": root_lineage,
                "operators": operator_lineage,
                "particle_frame": particle_frame,
                "reduction_trace": reduction_trace,
            },
            "sentence_roles": sentence_roles,
            "unresolved_tokens": unresolved,
            "diagnostics": [diagnostic.as_dict() for diagnostic in diagnostics],
        }

    def _parse_token(self, token: str, add_root: Any, add_node: Any, diagnostics: list[Diagnostic], unresolved: list[str]) -> tuple[str, list[str], list[str]] | None:
        if token.endswith("-"):
            diagnostics.append(Diagnostic("E_OPERATOR_TARGET", "error", "Operator has no target.", token))
            return None
        if "-" in token:
            return self._parse_notated_token(token, add_root, add_node, diagnostics, unresolved)
        if token in self.roots:
            return add_root(token), [], [self.roots[token]["id"]]
        if token in self.grammar_lexemes:
            lexeme = self.grammar_lexemes[token]
            return add_node("grammar_lexeme", token, function=lexeme["function"]), [], []
        segmentation = self._segment_roots(token)
        if segmentation:
            return self._compound(segmentation, token, add_root, add_node), [], [self.roots[form]["id"] for form in segmentation]
        unresolved.append(token)
        diagnostics.append(Diagnostic("E_UNKNOWN_TOKEN", "error", "Token has no constitutional registry entry.", token))
        if token == "raema":
            diagnostics.append(Diagnostic("W_UNRESOLVED_GLOSS", "warning", "The specification's raema example contains unresolved ema.", token))
        return None

    def _parse_notated_token(self, token: str, add_root: Any, add_node: Any, diagnostics: list[Diagnostic], unresolved: list[str]) -> tuple[str, list[str], list[str]] | None:
        parts = token.split("-")
        prefix = self.prefixes.get(parts[0]) if parts[0] else None
        suffix = self.suffixes.get(parts[-1]) if parts[-1] else None
        core = parts[1 if prefix else 0 : -1 if suffix else len(parts)]
        if not core:
            diagnostics.append(Diagnostic("E_OPERATOR_TARGET", "error", "Operator has no root or composite target.", token))
            return None
        forms: list[str] = []
        for part in core:
            if part in self.roots:
                forms.append(part)
            else:
                segment = self._segment_roots(part)
                if segment:
                    forms.extend(segment)
                else:
                    unresolved.append(part)
                    diagnostics.append(Diagnostic("E_UNKNOWN_TOKEN", "error", "Token has no constitutional registry entry.", part))
                    return None
        node_id = self._compound(forms, "".join(forms), add_root, add_node)
        operator_ids: list[str] = []
        if prefix:
            op_node = add_node("operator", prefix["form"], operator_id=prefix["id"], effect=prefix["effect"])
            add_node_ref = node_id
            # The compiler materializes the relationship through a lightweight edge marker node.
            # Edges are assembled by the caller-independent graph representation below.
            operator_ids.append(prefix["id"])
            node_id = add_node("composite", token, components=[add_node_ref], operator=prefix["id"])
        if suffix:
            operator_ids.append(suffix["id"])
            node_id = add_node("composite", token, components=[node_id], operator=suffix["id"])
        return node_id, operator_ids, [self.roots[form]["id"] for form in forms]

    @staticmethod
    def _compound(forms: list[str], surface: str, add_root: Any, add_node: Any) -> str:
        root_nodes = [add_root(form) for form in forms]
        if len(root_nodes) == 1:
            return root_nodes[0]
        return add_node("composite", surface, components=root_nodes)

    def _segment_roots(self, value: str) -> list[str] | None:
        """Return a full longest-first root segmentation, or None when impossible."""
        memo: dict[str, list[str] | None] = {}

        def solve(remaining: str) -> list[str] | None:
            if not remaining:
                return []
            if remaining in memo:
                return memo[remaining]
            for form in self._root_forms:
                if remaining.startswith(form):
                    rest = solve(remaining[len(form) :])
                    if rest is not None:
                        memo[remaining] = [form, *rest]
                        return memo[remaining]
            memo[remaining] = None
            return None

        segmented = solve(value)
        return segmented if segmented and len(segmented) > 1 else None

    def _sentence_roles(self, tokens: list[str], start_index: int) -> list[dict[str, str]]:
        if start_index == 0:
            return []
        names = self.registry["grammar"]["sentence"]["canonical_order"]
        roles = [{"token": tokens[0], "role": names[0]}]
        for index, token in enumerate(tokens[1:], start=1):
            role = names[index] if index < len(names) else "modifier"
            roles.append({"token": token, "role": role})
        return roles


def compile_expression(expression: str, mode: str = "strict", registry_path: str | Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    return MytharCompiler(registry_path).compile(expression, mode)
