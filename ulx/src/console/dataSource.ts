import type { CIEMSIntegration } from "../core/csl/integration.js";
import type { CslEvidenceBundle, CslGraph, CslReplayRecord, CslArtifactRecord } from "../types/csl.js";
import type {
  AaisCapabilityDescriptor,
  AaisCodingCapability,
  AaisCodingProvenanceGraph,
  AaisConsoleProjection,
  AaisConsoleProvider
} from "../types/aais.js";
import type {
  KnowledgeGraph,
  KnowledgePublicProjection,
  KnowledgeStore
} from "../types/knowledge.js";

export class ConsoleDataSource {
  constructor(
    private readonly ciems: CIEMSIntegration,
    private readonly knowledgeStore: KnowledgeStore | null = null,
    private readonly aaisStore: AaisConsoleProvider | null = null
  ) {}

  fetchArtifacts(): CslArtifactRecord[] {
    return this.ciems.fetch_artifacts();
  }

  fetch_artifacts(): CslArtifactRecord[] {
    return this.fetchArtifacts();
  }

  fetchEvolutionGraph(): CslGraph {
    return this.ciems.fetch_evolution_graph();
  }

  fetch_evolution_graph(): CslGraph {
    return this.fetchEvolutionGraph();
  }

  fetchGovernanceGraph(): CslGraph {
    return this.ciems.fetch_governance_graph();
  }

  fetch_governance_graph(): CslGraph {
    return this.fetchGovernanceGraph();
  }

  fetchReplayEvents(): CslReplayRecord[] {
    return this.ciems.fetch_replay_events();
  }

  fetch_replay_events(): CslReplayRecord[] {
    return this.fetchReplayEvents();
  }

  fetchEvidence(promotionId: string): CslEvidenceBundle {
    return this.ciems.fetch_evidence(promotionId);
  }

  fetch_evidence(promotionId: string): CslEvidenceBundle {
    return this.fetchEvidence(promotionId);
  }

  fetchKnowledgeProjection(): KnowledgePublicProjection {
    if (!this.knowledgeStore) {
      return { entities: [], documents: [], claims: [] };
    }
    return this.knowledgeStore.projection();
  }

  fetch_knowledge_projection(): KnowledgePublicProjection {
    return this.fetchKnowledgeProjection();
  }

  fetchKnowledgeGraph(): KnowledgeGraph {
    if (!this.knowledgeStore) {
      return { nodes: [], edges: [] };
    }
    return this.knowledgeStore.graph();
  }

  fetch_knowledge_graph(): KnowledgeGraph {
    return this.fetchKnowledgeGraph();
  }

  fetchAaisCapabilities(): AaisCapabilityDescriptor[] {
    return this.aaisStore ? this.aaisStore.listCapabilities().map((capability) => ({ ...capability })) : [];
  }

  fetch_aais_capabilities(): AaisCapabilityDescriptor[] {
    return this.fetchAaisCapabilities();
  }

  fetchAaisCodingCapabilities(): AaisCodingCapability[] {
    return this.aaisStore
      ? this.aaisStore.listCodingCapabilities().map((capability) => ({
          ...capability,
          inputs: [...capability.inputs],
          governanceConstraints: [...capability.governanceConstraints],
          routing: Object.fromEntries(
            Object.entries(capability.routing).map(([key, value]) => [key, value ? { ...value } : value]),
          ),
        }))
      : [];
  }

  fetch_aais_coding_capabilities(): AaisCodingCapability[] {
    return this.fetchAaisCodingCapabilities();
  }

  fetchAaisProvenanceGraph(): AaisCodingProvenanceGraph {
    return this.aaisStore
      ? {
          records: this.aaisStore.listProvenanceRecords().map((record) => ({
            ...record,
            filesChanged: [...record.filesChanged],
            testsRan: [...record.testsRan],
            constraintsApplied: [...record.constraintsApplied],
            evidence: [...record.evidence],
          })),
        }
      : { records: [] };
  }

  fetch_aais_provenance_graph(): AaisCodingProvenanceGraph {
    return this.fetchAaisProvenanceGraph();
  }

  fetchAaisProjection(): AaisConsoleProjection {
    return {
      capabilities: this.fetchAaisCapabilities(),
      codingCapabilities: this.fetchAaisCodingCapabilities(),
      provenance: this.fetchAaisProvenanceGraph(),
    };
  }

  fetch_aais_projection(): AaisConsoleProjection {
    return this.fetchAaisProjection();
  }
}
