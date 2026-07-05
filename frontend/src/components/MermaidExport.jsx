import { Copy, FileText } from "lucide-react";
import toast from "react-hot-toast";

export default function MermaidExport({ mermaid }) {
  return (
    <section className="panel p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 font-semibold">
          <FileText size={17} className="text-accent" />
          Mermaid Export
        </div>
        <button
          className="icon-button"
          title="Copy Mermaid"
          onClick={() => {
            navigator.clipboard.writeText(mermaid ?? "");
            toast.success("Copied Mermaid diagram");
          }}
        >
          <Copy size={16} />
        </button>
      </div>
      <pre className="max-h-72 overflow-auto rounded-md bg-black/5 p-3 text-xs dark:bg-white/10">{mermaid}</pre>
    </section>
  );
}

