# Mythar v0.3: A Versioned Constitutional Semantic Language

**Author:** Jon Halstead  
**Version:** 0.3.0  
**Date:** July 16, 2026

## Abstract

Mythar v0.3 presents a versioned semantic-language system in which lexical roles, grammar, semantic lineage, and invariants are represented as executable constitutional artifacts. The release ratifies three previously unresolved lexemes—`ema` as a root, `fak` as a stackable particle, and `tila` as a postfix meta-operator—while preserving API and grammar compatibility with Mythar Core v0.2.

## Constitutional Model

Mythar expressions compile to structured ASTs and registry references. The compiler enforces meaningful morphemes, valid operator targets, particle framing, composite lineage, and acyclic semantic construction. Strict mode admits canonical registry material; lenient mode permits experimental material with diagnostics.

## v0.3 Ratifications

`ema` denotes beautiful existence and participates in `raema`. `fak` supplies a craft/making semantic frame within a particle stack. `tila` transforms the immediately preceding root, composite, or operator application by purity/refinement; `maia tila` is its canonical example.

## Runtime and API

The Cloud Run service exposes `/v1/compile` for v0.2 and `/v2/compile` for v0.3. Each result provides an AST, registry references, invariant outcomes, and diagnostics. This preserves client stability while enabling constitutional evolution.

## Reproducibility

The authoritative registry, ratification record, conformance cases, OpenAPI contract, and implementation are released in the Mythar GitHub repository under tag `v0.3.0`.
