import cytoscape from "cytoscape";
import { Download, Network, RefreshCw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

const layouts = {
  force: { name: "cose", animate: true, nodeRepulsion: 8000, idealEdgeLength: 140, gravity: 0.3 },
  hierarchy: { name: "breadthfirst", directed: true, padding: 30, spacingFactor: 1.7 },
  circular: { name: "circle", padding: 30 }
};

const colors = {
  file: "#64748b",
  class: "#0f766e",
  interface: "#0891b2",
  function: "#c2410c",
  method: "#c2410c",
  package: "#7c3aed",
  framework: "#2563eb",
  database: "#16a34a",
  cloud: "#db2777",
  container: "#475569",
  ai_component: "#9333ea",
  api: "#ea580c",
  queue: "#ca8a04",
  config: "#525252"
};

const shapes = {
  file: "roundrectangle",
  class: "roundrectangle",
  interface: "ellipse",
  function: "rectangle",
  method: "rectangle",
  package: "hexagon",
  framework: "diamond",
  database: "database",
  cloud: "ellipse",
  container: "roundrectangle",
  ai_component: "pentagon",
  api: "vee",
  queue: "triangle",
  config: "roundrectangle"
};

export default function GraphView({ graph, onSelect }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [layoutName, setLayoutName] = useState("force");
  const elements = useMemo(
    () => [
      ...(graph.nodes ?? []).map((node) => ({
        data: { id: node.id, label: node.name, type: node.type, node }
      })),
      ...(graph.edges ?? []).map((edge, index) => ({
        data: { id: `${edge.source}-${edge.target}-${index}`, source: edge.source, target: edge.target, label: edge.type }
      }))
    ],
    [graph]
  );

  useEffect(() => {
    if (!containerRef.current) return;
    cyRef.current?.destroy();
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: "node",
          style: {
            "background-color": (node) => colors[node.data("type")] ?? "#525252",
            "shape": (node) => shapes[node.data("type")] ?? "roundrectangle",
            label: "data(label)",
            color: "#ffffff",
            "font-size": 12,
            "text-wrap": "wrap",
            "text-max-width": 100,
            "text-outline-color": "#111827",
            "text-outline-width": 4,
            "border-width": 2,
            "border-color": "#ffffff",
            width: 50,
            height: 50,
            "padding": 10,
            "shadow-blur": 18,
            "shadow-color": "rgba(15, 23, 42, 0.2)",
            "shadow-offset-x": 0,
            "shadow-offset-y": 6,
            "shadow-opacity": 0.4
          }
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#cbd5e1",
            "target-arrow-color": "#cbd5e1",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "opacity": 0.85,
            "arrow-scale": 1.2,
            "label": "data(label)",
            "font-size": 10,
            "text-rotation": "autorotate",
            "text-margin-x": 0,
            "text-margin-y": -6,
            "edge-text-rotation": "autorotate"
          }
        },
        {
          selector: ":selected",
          style: {
            "border-width": 4,
            "border-color": "#fde047",
            "background-color": "#facc15",
            "transition-property": "border-color, background-color",
            "transition-duration": "200ms"
          }
        },
        {
          selector: ".faded",
          style: {
            opacity: 0.25
          }
        }
      ],
      layout: layouts[layoutName],
      wheelSensitivity: 0.2,
      userZoomingEnabled: true,
      userPanningEnabled: true
    });
    cy.on("tap", "node", (event) => onSelect?.(event.target.data("node")));
    cy.on("mouseover", "node", (event) => {
      const node = event.target;
      node.addClass("hovered");
      node.style("text-outline-color", "#ffffff");
      node.style("text-outline-width", 6);
    });
    cy.on("mouseout", "node", (event) => {
      const node = event.target;
      node.removeClass("hovered");
      node.style("text-outline-color", "#111827");
      node.style("text-outline-width", 4);
    });
    cyRef.current = cy;
    return () => cy.destroy();
  }, [elements, layoutName, onSelect]);

  const exportImage = (type) => {
    const dataUrl = type === "svg" ? cyRef.current?.svg?.() : cyRef.current?.png({ full: true, scale: 2 });
    if (!dataUrl) return;
    const link = document.createElement("a");
    link.href = type === "svg" ? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(dataUrl)}` : dataUrl;
    link.download = `knowledge-graph.${type}`;
    link.click();
  };

  return (
    <section className="panel min-h-[520px] overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line p-4 dark:border-white/10">
        <div className="flex items-center gap-2 font-semibold">
          <Network size={18} className="text-accent" />
          Knowledge Graph
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select className="field" value={layoutName} onChange={(event) => setLayoutName(event.target.value)}>
            <option value="force">Force</option>
            <option value="hierarchy">Hierarchy</option>
            <option value="circular">Circular</option>
          </select>
          <button className="icon-button" title="Run layout" onClick={() => cyRef.current?.layout(layouts[layoutName]).run()}>
            <RefreshCw size={16} />
          </button>
          <button className="icon-button" title="Export PNG" onClick={() => exportImage("png")}>
            <Download size={16} />
          </button>
        </div>
      </div>
      <div className="grid gap-3 border-b border-line p-4 text-sm text-ink/60 dark:text-white/60 sm:grid-cols-[1fr_auto]">
        <div>Click nodes to inspect details and use layout selection for better view organization.</div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700 dark:bg-white/5 dark:text-white/80">Files</span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700 dark:bg-white/5 dark:text-white/80">Frameworks</span>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-700 dark:bg-white/5 dark:text-white/80">AI</span>
        </div>
      </div>
      <div ref={containerRef} className="h-[620px] w-full bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-[#111827] dark:via-[#111827] dark:to-[#13171e]" />
    </section>
  );
}

