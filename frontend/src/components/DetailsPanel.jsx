export default function DetailsPanel({ node }) {
  return (
    <section className="panel p-4">
      <h2 className="font-semibold">Details</h2>
      {node ? (
        <div className="mt-4 space-y-3 text-sm">
          <div>
            <div className="text-ink/50 dark:text-white/50">Name</div>
            <div className="break-words font-medium">{node.name}</div>
          </div>
          <div>
            <div className="text-ink/50 dark:text-white/50">Type</div>
            <div>{node.type}</div>
          </div>
          <div>
            <div className="text-ink/50 dark:text-white/50">File</div>
            <div className="break-words">{node.file_path || "Global"}</div>
          </div>
          <pre className="max-h-72 overflow-auto rounded-md bg-black/5 p-3 text-xs dark:bg-white/10">
            {JSON.stringify(node.metadata ?? {}, null, 2)}
          </pre>
        </div>
      ) : (
        <p className="mt-4 text-sm text-ink/60 dark:text-white/60">Select a graph node to inspect metadata.</p>
      )}
    </section>
  );
}

