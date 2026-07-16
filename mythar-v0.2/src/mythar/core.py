from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE = Path(r"G:\mythar-registry\registry-v0.1.json")
EXTENSION = Path(r"G:\mythar-registry\registry-v0.2.json")


class MytharCompiler:
    def __init__(self, base: Path = BASE, extension: Path = EXTENSION) -> None:
        self.base = json.loads(base.read_text(encoding="utf-8"))
        self.ext = json.loads(extension.read_text(encoding="utf-8"))
        self.roots = {entry["form"]: entry for entry in self.base["roots"]}
        self.particles = {entry["form"]: entry for entry in self.base["particles"]}
        self.prefixes = {entry["form"]: entry for entry in self.base["operators"]["prefixes"]}
        self.suffixes = {entry["form"]: entry for entry in self.base["operators"]["suffixes"]}
        self.lexemes = {entry["form"]: entry for entry in self.ext["grammar_lexemes"]}
        self.composites = {entry["form"]: entry for entry in self.ext["composites"]}
        self.experimental = {entry["form"]: entry for entry in self.ext["experimental_lexemes"]}

    def parse(self, expression: str, mode: str = "strict") -> dict[str, Any]:
        if mode not in {"strict", "lenient"}:
            raise ValueError("mode must be strict or lenient")
        tokens = expression.lower().strip().split()
        diagnostics: list[dict[str, Any]] = []
        index = 0
        particles = []
        while index < len(tokens) - 1 and tokens[index] in self.particles:
            particles.append(self._node("Particle", tokens[index], index, registry_ref=self.particles[tokens[index]]["id"]))
            index += 1
        terms = [self._term(token, position, mode, diagnostics) for position, token in enumerate(tokens[index:], index)]
        clause = self._node("Clause", None, None, particle_stack=particles, terms=terms)
        return self._node("Expression", expression, None, mode=mode, clauses=[clause])

    def compile(self, expression: str, mode: str = "strict") -> dict[str, Any]:
        ast = self.parse(expression, mode)
        diagnostics = self._collect_diagnostics(ast)
        if mode == "lenient":
            for diagnostic in diagnostics:
                if diagnostic["error_code"] == "NON_CANONICAL_EXPRESSION":
                    diagnostic["severity"] = "warning"
        clause = ast["clauses"][0]
        terms = clause["terms"]
        particles = clause["particle_stack"]
        if not expression.strip():
            diagnostics.append(self._diag("UNKNOWN_LEXEME", "Expression is empty.", None, None))
        if len(expression.split()) > 1 and not particles:
            diagnostics.append(self._diag("INVALID_STACK", "A sentence must begin with a particle stack.", 0, expression.split()[0]))
        self._validate_order(terms, diagnostics)
        refs = self._refs(ast)
        invariant_results = self._invariants(ast, diagnostics)
        valid = not any(item["severity"] == "error" for item in diagnostics)
        return {"ast": ast, "registry_refs": sorted(refs), "invariants": invariant_results, "diagnostics": diagnostics, "valid": valid}

    def _term(self, token: str, index: int, mode: str, diagnostics: list[dict[str, Any]]) -> dict[str, Any]:
        if token.endswith("-"):
            return self._node("Unknown", token, index, diagnostic="MISSING_TARGET")
        if "-" in token:
            parts = token.split("-")
            prefix = self.prefixes.get(parts[0]) if len(parts) > 2 or parts[-1] not in self.suffixes else None
            suffix = self.suffixes.get(parts[-1])
            core = parts[1 if prefix else 0:len(parts)-1 if suffix else len(parts)]
            if not core or any(part not in self.roots for part in core):
                return self._node("Unknown", token, index, diagnostic="UNKNOWN_LEXEME")
            target = self._composite_or_root(core, token, index)
            if prefix:
                target = self._node("OperatorApplication", token, index, operator_ref=prefix["id"], operator_form=prefix["form"], target=target)
            if suffix:
                target = self._node("OperatorApplication", token, index, operator_ref=suffix["id"], operator_form=suffix["form"], target=target)
            return target
        if token in self.roots:
            return self._node("Root", token, index, registry_ref=self.roots[token]["id"])
        if token in self.composites:
            item = self.composites[token]
            return self._node("Composite", token, index, registry_ref=item["id"], components=item["components"])
        if token in self.lexemes:
            item = self.lexemes[token]
            kind = {"tense":"TenseLexeme", "case":"CaseLexeme", "pronoun":"PronounLexeme"}[item["category"]]
            return self._node(kind, token, index, registry_ref=item["id"], features=item["features"])
        if token in self.experimental:
            item = self.experimental[token]
            severity = "error" if mode == "strict" else "warning"
            diagnostics.append(self._diag("NON_CANONICAL_EXPRESSION", item["reason"], index, token, severity))
            return self._node("Experimental", token, index, registry_ref=item["id"], canonical=False, diagnostic="NON_CANONICAL_EXPRESSION")
        return self._node("Unknown", token, index, diagnostic="UNKNOWN_LEXEME")

    def _validate_order(self, terms: list[dict[str, Any]], diagnostics: list[dict[str, Any]]) -> None:
        content = [term for term in terms if term["kind"] not in {"TenseLexeme", "CaseLexeme"}]
        for i, term in enumerate(terms):
            if term["kind"] == "TenseLexeme" and (i != 0 or not content):
                diagnostics.append(self._diag("INVALID_STACK", "Tense must occur after particles and before a verb.", term["token_index"], term["surface"]))
            if term["kind"] == "CaseLexeme" and (i == 0 or terms[i-1]["kind"] not in {"Root", "Composite", "PronounLexeme"}):
                diagnostics.append(self._diag("MISSING_TARGET", "Case requires a preceding nominal host.", term["token_index"], term["surface"]))

    def _collect_diagnostics(self, ast: dict[str, Any]) -> list[dict[str, Any]]:
        found: list[dict[str, Any]] = []
        def walk(value: Any) -> None:
            if isinstance(value, dict):
                if value.get("diagnostic"):
                    code = value["diagnostic"]
                    found.append(self._diag(code, "Operator requires a target." if code == "MISSING_TARGET" else "Unknown lexeme.", value.get("token_index"), value.get("surface")))
                for child in value.values(): walk(child)
            elif isinstance(value, list):
                for child in value: walk(child)
        walk(ast)
        return found

    def _invariants(self, ast: dict[str, Any], diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
        codes = {item["error_code"] for item in diagnostics}
        mapping = [("INV-001", "every_syllable_meaningful", "UNKNOWN_LEXEME" not in codes), ("INV-002", "no_silent_morphemes", "UNKNOWN_LEXEME" not in codes), ("INV-003", "no_meaningless_composites", "UNKNOWN_LEXEME" not in codes), ("INV-004", "operators_have_targets", "MISSING_TARGET" not in codes), ("INV-005", "particles_frame_expression", "INVALID_STACK" not in codes), ("INV-006", "lineage_preserved", "UNKNOWN_LEXEME" not in codes)]
        return [{"id": ident, "name": name, "passed": passed} for ident, name, passed in mapping]

    def _refs(self, value: Any) -> set[str]:
        if isinstance(value, dict):
            return ({value["registry_ref"]} if "registry_ref" in value else set()) | set().union(*(self._refs(item) for item in value.values()))
        if isinstance(value, list): return set().union(*(self._refs(item) for item in value)) if value else set()
        return set()

    def _composite_or_root(self, forms: list[str], surface: str, index: int) -> dict[str, Any]:
        if len(forms) == 1: return self._node("Root", forms[0], index, registry_ref=self.roots[forms[0]]["id"])
        return self._node("Composite", surface, index, components=[self.roots[form]["id"] for form in forms])

    @staticmethod
    def _node(kind: str, surface: str | None, token_index: int | None, **values: Any) -> dict[str, Any]:
        return {"kind": kind, "surface": surface, "token_index": token_index, **values}

    @staticmethod
    def _diag(code: str, message: str, token_index: int | None, token: str | None, severity: str = "error") -> dict[str, Any]:
        return {"error_code": code, "severity": severity, "message": message, "location": {"token_index": token_index, "span": token} if token is not None else None}
