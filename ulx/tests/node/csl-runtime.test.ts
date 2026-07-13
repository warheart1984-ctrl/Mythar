import assert from "node:assert/strict";
import { mkdtempSync } from "fs";
import { tmpdir } from "os";
import { join } from "path";
import { test } from "node:test";
import { ConsoleDataSource } from "../../src/console/dataSource.js";
import { renderLibraryOverlay, renderLibrarySummary } from "../../src/console/index.js";
import { CIEMSIntegration } from "../../src/core/csl/integration.js";
import { DefaultCslAdapter } from "../../src/core/csl/adapter.js";
import { FileCepArtifactStore, FileLineageStore, FileReplayStore } from "../../src/core/csl/store.js";
import { GovernanceSimulator } from "../../src/core/csl/simulator.js";
import { RuntimeEngine } from "../../src/core/csl/runtime.js";
import type { AaisConsoleProvider } from "../../src/types/aais.js";

function withWorkingDirectory<T>(root: string, fn: () => T): T {
  const previous = process.cwd();
  process.chdir(root);
  try {
    return fn();
  } finally {
    process.chdir(previous);
  }
}

test("CSL runtime stores artifacts, lineage, and replay evidence", () => {
  const root = mkdtempSync(join(tmpdir(), "ulx-csl-"));
  const integration = new CIEMSIntegration(
    new FileCepArtifactStore("constitutional/cep"),
    new FileLineageStore("constitutional/cep"),
    new FileReplayStore("constitutional/cep"),
    new DefaultCslAdapter()
  );
  const runtime = new RuntimeEngine(integration, {
    agents: [{ id: "agent-a", role: "operator", capabilities: ["compose"] }],
    policies: [
      {
        id: "policy-a",
        name: "Policy Alpha",
        version: "PolicyV0",
        rules: ["allow:task.create"],
        enabled: true,
        tier: 0,
        promotes_to: "PolicyV1"
      }
    ]
  });

  withWorkingDirectory(root, () => {
    const result = runtime.runOnce("agent-a", "task.create", { target: "deal" });
    const dataSource = new ConsoleDataSource(integration);

    assert.equal(result.decision.outcome, "accepted");
    assert.equal(dataSource.fetchArtifacts().length, 5);
    assert.equal(dataSource.fetchEvolutionGraph().nodes.length, 5);
    assert.ok(dataSource.fetchGovernanceGraph().edges.length >= 5);
    assert.ok(dataSource.fetchReplayEvents().length >= 1);

    const evidence = dataSource.fetchEvidence("Policy:policy-a");
    assert.ok(evidence.artifact);
    assert.equal(evidence.artifact?.artifact_type, "Policy");
    assert.equal(evidence.lineage.length >= 1, true);
  });
});

test("CSL simulator compares policy versions deterministically", () => {
  const root = mkdtempSync(join(tmpdir(), "ulx-csl-sim-"));
  const integration = new CIEMSIntegration(
    new FileCepArtifactStore("constitutional/cep"),
    new FileLineageStore("constitutional/cep"),
    new FileReplayStore("constitutional/cep"),
    new DefaultCslAdapter()
  );
  const runtime = new RuntimeEngine(integration, {
    agents: [{ id: "agent-a", role: "operator", capabilities: ["compose"] }]
  });
  const simulator = new GovernanceSimulator(runtime);
  const intent = runtime.generateIntent("agent-a", "task.create", { target: "deal" });
  const policies = [
    {
      id: "policy-v0",
      name: "Policy v0",
      version: "PolicyV0",
      rules: ["allow:task.create"],
      enabled: true
    },
    {
      id: "policy-v1",
      name: "Policy v1",
      version: "PolicyV1",
      rules: ["block:task.create"],
      enabled: true
    }
  ];

  withWorkingDirectory(root, () => {
    const results = simulator.simulate([intent], policies);
    const comparison = simulator.compare(results);

    assert.equal(results.PolicyV0.decisions[0]?.outcome, "accepted");
    assert.equal(results.PolicyV1.decisions[0]?.outcome, "blocked");
    assert.equal(comparison.length, 1);
    assert.equal(comparison[0]?.changed, true);
    assert.deepEqual(Object.keys(comparison[0]?.outcomes ?? {}).sort(), ["PolicyV0", "PolicyV1"]);
  });
});

test("ConsoleDataSource exposes AAIS capability and provenance projections", () => {
  const integration = new CIEMSIntegration(
    new FileCepArtifactStore("constitutional/cep"),
    new FileLineageStore("constitutional/cep"),
    new FileReplayStore("constitutional/cep"),
    new DefaultCslAdapter()
  );
  const aaisStore: AaisConsoleProvider = {
    listCapabilities: () => [
      {
        id: "capability-discovery-engine",
        name: "Capability Discovery Engine",
        kind: "engine" as const,
        summary: "Finds the best approved capability for a task.",
      },
    ],
    listCodingCapabilities: () => [
      {
        id: "RefactorCode",
        name: "RefactorCode",
        description: "Refactors existing code while preserving behavior and guarded logic.",
        inputs: ["target files", "repo context"],
        governanceConstraints: ["must preserve tests passing"],
        routing: {
          fastIteration: {
            preferredModel: "qwen-3b" as const,
            reason: "small diffs",
          },
        },
      },
    ],
    listProvenanceRecords: () => [
      {
        capabilityName: "Capability Discovery Engine",
        filesChanged: ["packages/aais/src/capabilities.ts"],
        testsRan: ["packages/aais/src/AAISRuntime.test.ts"],
        model: "qwen-7b" as const,
        constraintsApplied: ["must preserve behavior"],
        evidence: ["routing catalog", "provenance graph"],
      },
    ],
  };
  const dataSource = new ConsoleDataSource(integration, null, aaisStore);

  assert.deepEqual(dataSource.fetchAaisCapabilities(), [
    {
      id: "capability-discovery-engine",
      name: "Capability Discovery Engine",
      kind: "engine",
      summary: "Finds the best approved capability for a task.",
    },
  ]);
  assert.deepEqual(dataSource.fetch_aais_coding_capabilities(), [
    {
      id: "RefactorCode",
      name: "RefactorCode",
      description: "Refactors existing code while preserving behavior and guarded logic.",
      inputs: ["target files", "repo context"],
      governanceConstraints: ["must preserve tests passing"],
      routing: {
        fastIteration: {
          preferredModel: "qwen-3b",
          reason: "small diffs",
        },
      },
    },
  ]);
  assert.deepEqual(dataSource.fetchAaisProvenanceGraph(), {
    records: [
      {
        capabilityName: "Capability Discovery Engine",
        filesChanged: ["packages/aais/src/capabilities.ts"],
        testsRan: ["packages/aais/src/AAISRuntime.test.ts"],
        model: "qwen-7b",
        constraintsApplied: ["must preserve behavior"],
        evidence: ["routing catalog", "provenance graph"],
      },
    ],
  });
  assert.deepEqual(dataSource.fetchAaisProjection(), {
    capabilities: [
      {
        id: "capability-discovery-engine",
        name: "Capability Discovery Engine",
        kind: "engine",
        summary: "Finds the best approved capability for a task.",
      },
    ],
    codingCapabilities: [
      {
        id: "RefactorCode",
        name: "RefactorCode",
        description: "Refactors existing code while preserving behavior and guarded logic.",
        inputs: ["target files", "repo context"],
        governanceConstraints: ["must preserve tests passing"],
        routing: {
          fastIteration: {
            preferredModel: "qwen-3b",
            reason: "small diffs",
          },
        },
      },
    ],
    provenance: {
      records: [
        {
          capabilityName: "Capability Discovery Engine",
          filesChanged: ["packages/aais/src/capabilities.ts"],
          testsRan: ["packages/aais/src/AAISRuntime.test.ts"],
          model: "qwen-7b",
          constraintsApplied: ["must preserve behavior"],
          evidence: ["routing catalog", "provenance graph"],
        },
      ],
    },
  });
});

test("Library console renders AAIS projection content when supplied", () => {
  const lines = renderLibrarySummary(
    "sovereign-os",
    {
      governanceLog: true,
      continuityLog: true,
      snapshotLog: false,
      journalLog: true,
    },
    3,
    7,
    {
      capabilities: [
        {
          id: "capability-discovery-engine",
          name: "Capability Discovery Engine",
          kind: "engine",
          summary: "Finds the best approved capability for a task.",
        },
      ],
      codingCapabilities: [
        {
          id: "RefactorCode",
          name: "RefactorCode",
          description: "Refactors existing code while preserving behavior and guarded logic.",
          inputs: ["target files"],
          governanceConstraints: ["must preserve tests passing"],
          routing: {},
        },
      ],
      provenance: {
        records: [
          {
            capabilityName: "Capability Discovery Engine",
            filesChanged: ["packages/aais/src/capabilities.ts"],
            testsRan: ["packages/aais/src/AAISRuntime.test.ts"],
            model: "qwen-7b",
            constraintsApplied: ["must preserve behavior"],
            evidence: ["routing catalog"],
          },
        ],
      },
    }
  );

  const overlay = renderLibraryOverlay(
    "sovereign-os",
    {
      governanceLog: true,
      continuityLog: true,
      snapshotLog: false,
      journalLog: true,
    },
    {
      capabilities: [
        {
          id: "capability-discovery-engine",
          name: "Capability Discovery Engine",
          kind: "engine",
          summary: "Finds the best approved capability for a task.",
        },
      ],
      codingCapabilities: [
        {
          id: "RefactorCode",
          name: "RefactorCode",
          description: "Refactors existing code while preserving behavior and guarded logic.",
          inputs: ["target files"],
          governanceConstraints: ["must preserve tests passing"],
          routing: {},
        },
      ],
      provenance: {
        records: [
          {
            capabilityName: "Capability Discovery Engine",
            filesChanged: ["packages/aais/src/capabilities.ts"],
            testsRan: ["packages/aais/src/AAISRuntime.test.ts"],
            model: "qwen-7b",
            constraintsApplied: ["must preserve behavior"],
            evidence: ["routing catalog"],
          },
        ],
      },
    }
  );

  assert.ok(lines.includes("AAIS capabilities: 1"));
  assert.ok(lines.includes("AAIS coding: 1"));
  assert.ok(lines.includes("AAIS provenance: 1"));
  assert.ok(overlay.some((line) => line.includes("AAIS projection: present")));
  assert.ok(overlay.some((line) => line.includes("Capability Discovery Engine")));
  assert.ok(overlay.some((line) => line.includes("RefactorCode")));
});
