import type { WorkspaceAdapterEntry, WorkspaceAdapterManifest } from "./workspaces.js";
import { listWorkspaceAdapters, readWorkspaceAdapterManifest } from "./workspaces.js";

export interface SubstrateAdapterProjection {
  workspace: WorkspaceAdapterEntry;
  substrates: string[];
  ready: boolean;
}

export function listSubstrateAdapters(path = "ulx/constitutional/workspace-adapters.json"): WorkspaceAdapterEntry[] {
  return listWorkspaceAdapters(path);
}

export function projectSubstrateAdapters(path = "ulx/constitutional/workspace-adapters.json"): SubstrateAdapterProjection[] {
  const manifest: WorkspaceAdapterManifest = readWorkspaceAdapterManifest(path);
  return manifest.workspaces.map((workspace) => ({
    workspace,
    substrates: [...workspace.substrates],
    ready: workspace.substrates.length > 0
  }));
}
