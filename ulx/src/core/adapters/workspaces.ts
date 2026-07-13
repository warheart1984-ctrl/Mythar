import { existsSync, readFileSync } from "fs";

export interface WorkspaceAdapterEntry {
  id: string;
  root: string;
  projection: string;
  substrates: string[];
  aais?: string;
}

export interface WorkspaceAdapterManifest {
  version: string;
  steward: string;
  workspaces: WorkspaceAdapterEntry[];
}

const DEFAULT_MANIFEST: WorkspaceAdapterManifest = {
  version: "1.0.0",
  steward: "ULX Adapter Governance",
  workspaces: [
    {
      id: "project-infi",
      root: "E:/project-infi",
      projection: "ULX project-infi projection",
      substrates: ["sovereign-ide", "aais", "ulx"]
    },
    {
      id: "project-infinity-main",
      root: "E:/Project-Infinity-main",
      projection: "AAIS launch projection",
      substrates: ["aais"]
    }
  ]
};

function readManifestPath(path = "ulx/constitutional/workspace-adapters.json"): WorkspaceAdapterManifest {
  if (!existsSync(path)) {
    return DEFAULT_MANIFEST;
  }
  return JSON.parse(readFileSync(path, "utf8")) as WorkspaceAdapterManifest;
}

export function readWorkspaceAdapterManifest(path = "ulx/constitutional/workspace-adapters.json"): WorkspaceAdapterManifest {
  return readManifestPath(path);
}

export function listWorkspaceAdapters(path = "ulx/constitutional/workspace-adapters.json"): WorkspaceAdapterEntry[] {
  return readManifestPath(path).workspaces.slice().sort((left, right) => left.id.localeCompare(right.id));
}

export function getWorkspaceAdapter(
  workspaceId: string,
  path = "ulx/constitutional/workspace-adapters.json"
): WorkspaceAdapterEntry | null {
  return listWorkspaceAdapters(path).find((entry) => entry.id === workspaceId) ?? null;
}
