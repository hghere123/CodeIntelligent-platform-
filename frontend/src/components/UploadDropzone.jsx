import { UploadCloud } from "lucide-react";
import { useCallback, useRef, useState } from "react";

const MAX_SIZE = 500 * 1024 * 1024;

export default function UploadDropzone({ onUpload, progress, isUploading }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const handleFile = useCallback(
    (file) => {
      if (!file) return;
      if (!file.name.toLowerCase().endsWith(".zip")) {
        onUpload(null, "Only ZIP files are supported.");
        return;
      }
      if (file.size > MAX_SIZE) {
        onUpload(null, "Repository archive must be 500MB or less.");
        return;
      }
      onUpload(file);
    },
    [onUpload]
  );

  return (
    <div
      className={`panel flex min-h-[320px] flex-col items-center justify-center border-dashed p-8 text-center transition ${
        dragging ? "border-accent bg-accent/5" : ""
      }`}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);
        handleFile(event.dataTransfer.files?.[0]);
      }}
    >
      <input
        ref={inputRef}
        className="hidden"
        type="file"
        accept=".zip"
        onChange={(event) => handleFile(event.target.files?.[0])}
      />
      <span className="mb-5 grid size-16 place-items-center rounded-lg bg-accent text-white">
        <UploadCloud size={28} />
      </span>
      <h1 className="text-2xl font-semibold">Analyze a repository ZIP</h1>
      <p className="mt-3 max-w-xl text-sm leading-6 text-ink/70 dark:text-white/70">
        Upload a source repository archive to extract entities, dependencies, metrics, APIs, containers, cloud,
        and AI components into an interactive graph.
      </p>
      <button
        className="mt-6 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white transition hover:bg-ink/90 disabled:opacity-60 dark:bg-white dark:text-ink"
        disabled={isUploading}
        onClick={() => inputRef.current?.click()}
      >
        {isUploading ? "Analyzing..." : "Choose ZIP"}
      </button>
      {isUploading && (
        <div className="mt-6 w-full max-w-md">
          <div className="h-2 overflow-hidden rounded-full bg-black/10 dark:bg-white/10">
            <div className="h-full rounded-full bg-accent transition-all" style={{ width: `${progress}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}

