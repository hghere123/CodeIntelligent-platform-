import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import DashboardCards from "../components/DashboardCards.jsx";
import DetailsPanel from "../components/DetailsPanel.jsx";
import GraphView from "../components/GraphView.jsx";
import MermaidExport from "../components/MermaidExport.jsx";
import MetricsDashboard from "../components/MetricsDashboard.jsx";
import RepositoryTree from "../components/RepositoryTree.jsx";
import SearchPanel from "../components/SearchPanel.jsx";
import { exportMermaid, getAnalysis } from "../services/api.js";

const GRAPH_NODE_LIMIT = 2000;

export default function AnalysisPage() {
  const { analysisId } = useParams();
  const [selectedNode, setSelectedNode] = useState(null);
  const [showGraph, setShowGraph] = useState(false);
  const analysisQuery = useQuery({
    queryKey: ["analysis", analysisId],
    queryFn: () => getAnalysis(analysisId),
    enabled: analysisId !== "demo"
  });
  const mermaidQuery = useQuery({
    queryKey: ["mermaid", analysisId],
    queryFn: () => exportMermaid(analysisId),
    enabled: analysisId !== "demo"
  });
  const analysis = analysisId === "demo" ? demoAnalysis : analysisQuery.data;
  const mermaid = analysisId === "demo" ? demoMermaid : mermaidQuery.data;
  const nodeCounts = useMemo(() => analysis?.graph?.nodes ?? [], [analysis]);
  const graphSize = analysis?.graph?.nodes?.length ?? 0;
  const edgeCount = analysis?.graph?.edges?.length ?? 0;
  const graphTooLarge = graphSize > GRAPH_NODE_LIMIT;

  if (analysisQuery.isLoading) {
    return <main className="mx-auto max-w-7xl px-4 py-8">Loading analysis...</main>;
  }
  if (analysisQuery.error) {
    return <main className="mx-auto max-w-7xl px-4 py-8 text-coral">{analysisQuery.error.message}</main>;
  }
  if (!analysis) return null;

  return (
    <main className="mx-auto max-w-7xl space-y-5 px-4 py-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{analysis.repository_name}</h1>
          <p className="text-sm text-ink/60 dark:text-white/60">{analysis.analysis_id}</p>
        </div>
      </div>
      <DashboardCards analysis={analysis} />
      <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
        <div className="space-y-5">
          <RepositoryTree tree={analysis.tree} />
          <SearchPanel nodes={nodeCounts} onSelect={setSelectedNode} />
          <DetailsPanel node={selectedNode} />
        </div>
        <div className="space-y-5">
          {graphTooLarge && !showGraph ? (
            <section className="panel min-h-[520px] flex flex-col items-center justify-center gap-4 p-6 text-center">
              <div className="text-xl font-semibold">Large graph detected</div>
              <p className="max-w-xl text-sm text-ink/70 dark:text-white/70">
                This repository contains {graphSize} entities and {edgeCount} relationships. Rendering this full graph may be slow in the browser.
              </p>
              <button
                className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white hover:bg-accent-dark"
                onClick={() => setShowGraph(true)}
              >
                Load graph anyway
              </button>
            </section>
          ) : (
            <GraphView graph={analysis.graph} onSelect={setSelectedNode} />
          )}
          <div className="grid gap-5 xl:grid-cols-2">
            <MetricsDashboard metrics={analysis.metrics} detected={analysis.detected} />
            <MermaidExport mermaid={mermaid} />
          </div>
        </div>
      </div>
    </main>
  );
}

const demoAnalysis = {
  analysis_id: "demo",
  repository_name: "sample-repo",
  tree: {
    name: "sample-repo",
    path: "",
    type: "directory",
    children: [
      { name: "backend", path: "backend", type: "directory", children: [{ name: "app.py", path: "backend/app.py", type: "file" }] },
      { name: "frontend", path: "frontend", type: "directory", children: [{ name: "App.jsx", path: "frontend/src/App.jsx", type: "file" }] }
    ]
  },
  graph: {
    nodes: [
      { id: "file:backend/app.py", type: "file", name: "app.py", file_path: "backend/app.py", metadata: { language: "python" } },
      { id: "backend/app.py:class:Assistant:4", type: "class", name: "Assistant", file_path: "backend/app.py", metadata: {} },
      { id: "backend/app.py:function:chat:10", type: "function", name: "chat", file_path: "backend/app.py", metadata: {} },
      { id: "framework:FastAPI", type: "framework", name: "FastAPI", file_path: "", metadata: {} },
      { id: "ai_ml:OpenAI", type: "ai_component", name: "OpenAI", file_path: "", metadata: {} }
    ],
    edges: [
      { source: "file:backend/app.py", target: "backend/app.py:class:Assistant:4", type: "contains", metadata: {} },
      { source: "file:backend/app.py", target: "backend/app.py:function:chat:10", type: "contains", metadata: {} },
      { source: "file:backend/app.py", target: "framework:FastAPI", type: "uses", metadata: {} },
      { source: "file:backend/app.py", target: "ai_ml:OpenAI", type: "uses", metadata: {} }
    ]
  },
  metrics: {
    loc: 182,
    source_files: 6,
    cyclomatic_complexity: 11,
    functions: 9,
    classes: 2,
    dead_code: ["unused_helper"],
    circular_dependencies: [],
    languages: { python: 3, javascript: 2, config: 5 }
  },
  detected: { frameworks: ["FastAPI", "React"], databases: ["Redis"], cloud: [], containers: ["Docker", "Kubernetes"], ai_ml: ["OpenAI"], apis: ["REST routes"], queues: [] },
  files: []
};

const demoMermaid = `graph TD
  backend["app.py (file)"]
  assistant["Assistant (class)"]
  chat["chat (function)"]
  fastapi["FastAPI (framework)"]
  openai["OpenAI (ai_component)"]
  backend -->|contains| assistant
  backend -->|contains| chat
  backend -->|uses| fastapi
  backend -->|uses| openai`;
