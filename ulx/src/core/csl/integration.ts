import type {
  CslAdapter,
  CslArtifactRecord,
  CslEvidenceBundle,
  CslGraph,
  CslLineageEdge,
  CslReplayRecord
} from "../../types/csl.js";
import { DefaultCslAdapter } from "./adapter.js";
import { FileCepArtifactStore, FileLineageStore, FileReplayStore, type CepArtifactStore, type CiemsLineageStore, type CslReplayStore } from "./store.js";

export class CIEMSIntegration {
  constructor(
    public readonly cep: CepArtifactStore = new FileCepArtifactStore(),
    public readonly lineage: CiemsLineageStore = new FileLineageStore(),
    public readonly replay: CslReplayStore = new FileReplayStore(),
    public readonly adapter: CslAdapter = new DefaultCslAdapter()
  ) {}

  saveArtifact<T extends CslArtifactRecord>(artifact: T): T {
    return this.cep.saveArtifact(artifact);
  }

  save_artifact<T extends CslArtifactRecord>(artifact: T): T {
    return this.saveArtifact(artifact);
  }

  recordLineage(edge: CslLineageEdge): CslLineageEdge {
    return this.lineage.record(edge);
  }

  record_lineage(edge: CslLineageEdge): CslLineageEdge {
    return this.recordLineage(edge);
  }

  fetchArtifacts(): CslArtifactRecord[] {
    return this.cep.listArtifacts();
  }

  fetch_artifacts(): CslArtifactRecord[] {
    return this.fetchArtifacts();
  }

  fetchEvolutionGraph(): CslGraph {
    return this.lineage.buildEvolutionGraph(this.fetchArtifacts());
  }

  fetch_evolution_graph(): CslGraph {
    return this.fetchEvolutionGraph();
  }

  fetchGovernanceGraph(): CslGraph {
    return this.lineage.buildGovernanceGraph(this.fetchArtifacts());
  }

  fetch_governance_graph(): CslGraph {
    return this.fetchGovernanceGraph();
  }

  fetchReplayEvents(): CslReplayRecord[] {
    return this.replay.getEvents();
  }

  fetch_replay_events(): CslReplayRecord[] {
    return this.fetchReplayEvents();
  }

  fetchEvidence(promotionId: string): CslEvidenceBundle {
    return this.lineage.getPromotionEvidence(promotionId, this.fetchArtifacts(), this.fetchReplayEvents());
  }

  fetch_evidence(promotionId: string): CslEvidenceBundle {
    return this.fetchEvidence(promotionId);
  }
}
