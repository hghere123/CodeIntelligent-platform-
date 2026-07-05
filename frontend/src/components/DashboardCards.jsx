import { Blocks, Braces, FileCode2, Gauge } from "lucide-react";

const cardMeta = [
  ["Files", FileCode2, "files_count"],
  ["Languages", Braces, "languages"],
  ["Frameworks", Blocks, "frameworks"],
  ["Complexity", Gauge, "complexity"]
];

export default function DashboardCards({ analysis }) {
  const summary = analysis.summary ?? {};
  const values = {
    files_count: summary.files_count ?? analysis.files?.length ?? 0,
    languages: Object.keys(analysis.metrics?.languages ?? {}).length,
    frameworks: analysis.detected?.frameworks?.length ?? 0,
    complexity: analysis.metrics?.cyclomatic_complexity ?? 0
  };

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {cardMeta.map(([label, Icon, key]) => (
        <div key={label} className="panel p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-ink/60 dark:text-white/60">{label}</span>
            <Icon size={18} className="text-accent" />
          </div>
          <div className="mt-3 text-3xl font-semibold">{values[key]}</div>
        </div>
      ))}
    </div>
  );
}

