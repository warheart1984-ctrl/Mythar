# Mythar Transduction Contract Standard v1.0

**Status:** Normative  
**Applies to:** Every target-language contract consuming a ratified Mythar ISF version.

## Required contract fields

Each `transducers/<iso-code>.json` file MUST declare its ISO language code, supported ISF version, lifecycle status, evidence classification, review status, and a complete `mappings` object. Each ratified ISF root MUST provide `noun`, `verb`, and `adjective` forms or be explicitly excluded with an evidence-backed reason.

## Review and lifecycle

Contracts progress through `draft`, `review`, and `ratified` status. A language contract must record reviewer identity or `pending`, evidence classification, the ISF root set it covers, and executable examples before it is published as ratified. A contract update creates a new contract version; it MUST NOT alter a released ISF meaning.

## Evidence classification

- **Observed:** supported by cited external evidence.
- **Specified:** a Mythar design choice, clearly labeled as such.
- **Hypothesized:** a proposal requiring review; reconstructed or historical-language material defaults here unless independently evidenced.

## Compiler boundary

Transducers consume ISF and generate target-language output. They MUST NOT add compiler semantics, alter registry identity, or bypass ISF conformance. Source-language adapters are separately versioned semantic-input profiles and MUST state their scope.
