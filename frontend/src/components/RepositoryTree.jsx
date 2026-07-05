import { ChevronRight, File, Folder } from "lucide-react";
import { useMemo, useState } from "react";

function TreeNode({ node, query }) {
  const [open, setOpen] = useState(node.path === "");
  const children = node.children ?? [];
  const visible =
    !query ||
    node.name.toLowerCase().includes(query) ||
    children.some((child) => JSON.stringify(child).toLowerCase().includes(query));
  if (!visible) return null;

  return (
    <div>
      <button
        className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-sm hover:bg-black/5 dark:hover:bg-white/10"
        onClick={() => setOpen((value) => !value)}
      >
        {children.length > 0 ? (
          <ChevronRight size={14} className={`transition ${open ? "rotate-90" : ""}`} />
        ) : (
          <span className="w-3.5" />
        )}
        {node.type === "directory" ? <Folder size={15} className="text-coral" /> : <File size={15} />}
        <span className="truncate">{node.name || "repository"}</span>
      </button>
      {open && children.length > 0 && (
        <div className="ml-4 border-l border-line pl-2 dark:border-white/10">
          {children.map((child) => (
            <TreeNode key={child.path || child.name} node={child} query={query} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function RepositoryTree({ tree }) {
  const [query, setQuery] = useState("");
  const normalizedQuery = useMemo(() => query.trim().toLowerCase(), [query]);

  return (
    <section className="panel min-h-[360px] p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="font-semibold">Repository Tree</h2>
        <input
          className="field w-40"
          placeholder="Filter"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
      </div>
      <div className="max-h-[620px] overflow-auto pr-1">
        <TreeNode node={tree} query={normalizedQuery} />
      </div>
    </section>
  );
}

