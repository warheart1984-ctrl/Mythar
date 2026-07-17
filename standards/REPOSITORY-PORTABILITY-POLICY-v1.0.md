# Repository Portability Policy v1.0

**Status:** Repository law — constitutional
**Applies to:** Every artifact published from this repository

## Constitutional rule

1. Published repositories MUST declare their supported platforms.
2. Public releases MUST include portability evidence for every declared supported platform.
3. Developer-specific paths, machine assumptions, user profiles, local secrets, and undisclosed host dependencies are prohibited in published artifacts.

## Scope and evolution

This policy governs the durable portability obligation, not a particular programming language, runtime, filesystem API, CI provider, or test command. Technical mechanisms are governed by the versioned [Portability Implementation Specification](PORTABILITY-IMPLEMENTATION-SPEC-v1.0.md), which may evolve without amending this repository law.

## Exceptions

An exception requires a ratification record that states its scope, rationale, affected platforms, alternative access path, owner, and review or expiry date. An exception does not silently narrow a published support claim.
