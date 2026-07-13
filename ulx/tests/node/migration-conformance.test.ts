import assert from "node:assert/strict";
import { readFileSync } from "fs";
import { test } from "node:test";

test("migration conformance manifests are present and well-formed", () => {
  const bundle = [
    "constitutional/migration.schema.json",
    "constitutional/migration.conformance.json",
    "constitutional/migration.replay.conformance.json",
    "constitutional/migration.restore.conformance.json",
    "constitutional/migration.timeline.conformance.json"
  ].map((path) => JSON.parse(readFileSync(path, "utf8")) as Record<string, unknown>);

  assert.equal(bundle.length, 5);
  assert.equal((bundle[0] as { title?: string }).title, "ULX Migration Runtime Artifact");
  assert.equal((bundle[1] as { id?: string }).id, "migration.conformance");
  assert.equal((bundle[2] as { id?: string }).id, "migration.replay.conformance");
  assert.equal((bundle[3] as { id?: string }).id, "migration.restore.conformance");
  assert.equal((bundle[4] as { id?: string }).id, "migration.timeline.conformance");
});
