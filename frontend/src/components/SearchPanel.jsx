import { Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

export default function SearchPanel({ nodes = [], onSelect }) {
  const [query, setQuery] = useState("");
  const [type, setType] = useState("all");
  const [debounced, setDebounced] = useState("");

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(query), 250);
    return () => clearTimeout(timer);
  }, [query]);

  const types = useMemo(() => ["all", ...Array.from(new Set(nodes.map((node) => node.type))).sort()], [nodes]);
  const results = useMemo(() => {
    const needle = debounced.toLowerCase();
    return nodes
      .filter((node) => type === "all" || node.type === type)
      .filter((node) => !needle || `${node.name} ${node.file_path} ${node.type}`.toLowerCase().includes(needle))
      .slice(0, 30);
  }, [debounced, nodes, type]);

  return (
    <section className="panel p-4">
      <div className="mb-3 flex items-center gap-2 font-semibold">
        <Search size={17} className="text-accent" />
        Search
      </div>
      <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
        <input className="field" placeholder="Search entities" value={query} onChange={(event) => setQuery(event.target.value)} />
        <select className="field" value={type} onChange={(event) => setType(event.target.value)}>
          {types.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>
      <div className="mt-3 max-h-80 overflow-auto">
        {results.map((node) => (
          <button
            key={node.id}
            className="flex w-full items-center justify-between gap-3 rounded-md px-2 py-2 text-left text-sm hover:bg-black/5 dark:hover:bg-white/10"
            onClick={() => onSelect?.(node)}
          >
            <span className="truncate">{node.name}</span>
            <span className="rounded bg-black/5 px-2 py-0.5 text-xs dark:bg-white/10">{node.type}</span>
          </button>
        ))}
      </div>
    </section>
  );
}

