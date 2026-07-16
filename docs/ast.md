# AST and Invariants

AST node kinds include Root, Composite, Particle, OperatorApplication, TenseLexeme, CaseLexeme, PronounLexeme, Clause, and Expression.

The compiler checks: meaningful syllables, no silent morphemes, meaningful composites, valid operator targets, whole-expression particle framing, and preserved lineage.

Strict mode rejects unresolved/non-canonical material. Lenient mode retains it with diagnostics while continuing to enforce structural invariants.
