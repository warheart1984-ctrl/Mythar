import { existsSync } from "fs";
import { readJson } from "./fs.js";
import type { ContinuityEvent } from "../types/ciems.js";

export interface LineageNode {
  id: string;
  type: string;
  timestamp: string;
}

export interface LineageEdge {
  from: string;
  to: string;
  type: string;
}

export interface LineageGraph {
  substrate_id: string;
  nodes: LineageNode[];
  edges: LineageEdge[];
}

export function generateLineageGraph(substrateId: string): LineageGraph {
  const continuity = readJson<{ timeline: ContinuityEvent[] }>(
    `constitutional/continuity/${substrateId}.continuity.json`
  );
  const nodes: LineageNode[] = continuity.timeline.map((event: ContinuityEvent, index: number) => ({
    id: `n-${index}`,
    type: event.type,
    timestamp: event.timestamp
  }));
  const edges: LineageEdge[] = [];
  for (let index = 1; index < nodes.length; index += 1) {
    edges.push({
      from: nodes[index - 1].id,
      to: nodes[index].id,
      type: "evolves_to"
    });
  }
  if (!existsSync(`substrates/${substrateId}/substrate.json`)) {
    return { substrate_id: substrateId, nodes: [], edges: [] };
  }
  return { substrate_id: substrateId, nodes, edges };
}
