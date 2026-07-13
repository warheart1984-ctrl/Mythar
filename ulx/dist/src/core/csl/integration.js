import { DefaultCslAdapter } from "./adapter.js";
import { FileCepArtifactStore, FileLineageStore, FileReplayStore } from "./store.js";
export class CIEMSIntegration {
    cep;
    lineage;
    replay;
    adapter;
    constructor(cep = new FileCepArtifactStore(), lineage = new FileLineageStore(), replay = new FileReplayStore(), adapter = new DefaultCslAdapter()) {
        this.cep = cep;
        this.lineage = lineage;
        this.replay = replay;
        this.adapter = adapter;
    }
    saveArtifact(artifact) {
        return this.cep.saveArtifact(artifact);
    }
    save_artifact(artifact) {
        return this.saveArtifact(artifact);
    }
    recordLineage(edge) {
        return this.lineage.record(edge);
    }
    record_lineage(edge) {
        return this.recordLineage(edge);
    }
    fetchArtifacts() {
        return this.cep.listArtifacts();
    }
    fetch_artifacts() {
        return this.fetchArtifacts();
    }
    fetchEvolutionGraph() {
        return this.lineage.buildEvolutionGraph(this.fetchArtifacts());
    }
    fetch_evolution_graph() {
        return this.fetchEvolutionGraph();
    }
    fetchGovernanceGraph() {
        return this.lineage.buildGovernanceGraph(this.fetchArtifacts());
    }
    fetch_governance_graph() {
        return this.fetchGovernanceGraph();
    }
    fetchReplayEvents() {
        return this.replay.getEvents();
    }
    fetch_replay_events() {
        return this.fetchReplayEvents();
    }
    fetchEvidence(promotionId) {
        return this.lineage.getPromotionEvidence(promotionId, this.fetchArtifacts(), this.fetchReplayEvents());
    }
    fetch_evidence(promotionId) {
        return this.fetchEvidence(promotionId);
    }
}
