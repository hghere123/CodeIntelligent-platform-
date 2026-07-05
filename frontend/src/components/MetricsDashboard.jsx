export default function MetricsDashboard({ metrics, detected }) {
  const languages = Object.entries(metrics.languages ?? {});
  const tech = Object.entries(detected ?? {});

  return (
    <section className="panel p-4">
      <h2 className="font-semibold">Metrics</h2>
      <div className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <Metric label="LOC" value={metrics.loc} />
        <Metric label="Functions" value={metrics.functions} />
        <Metric label="Classes" value={metrics.classes} />
        <Metric label="Complexity" value={metrics.cyclomatic_complexity} />
      </div>
      <div className="mt-5">
        <h3 className="text-sm font-semibold">Languages</h3>
        <div className="mt-2 space-y-2">
          {languages.map(([language, count]) => (
            <div key={language} className="flex items-center justify-between text-sm">
              <span>{language}</span>
              <span>{count}</span>
            </div>
          ))}
        </div>
      </div>
      <div className="mt-5">
        <h3 className="text-sm font-semibold">Detected Stack</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {tech.flatMap(([category, values]) =>
            values.map((value) => (
              <span key={`${category}-${value}`} className="rounded-md bg-accent/10 px-2 py-1 text-xs text-accent">
                {value}
              </span>
            ))
          )}
        </div>
      </div>
      {(metrics.dead_code?.length > 0 || metrics.circular_dependencies?.length > 0) && (
        <div className="mt-5 grid gap-4 text-sm md:grid-cols-2">
          <IssueList title="Dead Code" items={metrics.dead_code ?? []} />
          <IssueList title="Circular Dependencies" items={(metrics.circular_dependencies ?? []).map((cycle) => cycle.join(" -> "))} />
        </div>
      )}
    </section>
  );
}

function Metric({ label, value }) {
  return (
    <div className="rounded-md bg-black/5 p-3 dark:bg-white/10">
      <div className="text-ink/50 dark:text-white/50">{label}</div>
      <div className="mt-1 text-xl font-semibold">{value ?? 0}</div>
    </div>
  );
}

function IssueList({ title, items }) {
  return (
    <div>
      <h3 className="font-semibold">{title}</h3>
      <ul className="mt-2 max-h-40 overflow-auto rounded-md bg-black/5 p-3 dark:bg-white/10">
        {items.length ? items.slice(0, 20).map((item) => <li key={item}>{item}</li>) : <li>None detected</li>}
      </ul>
    </div>
  );
}

