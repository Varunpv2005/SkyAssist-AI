import type { EntrySeverity, ParsedEntry } from "../../types";

const SEVERITY_STYLES: Record<EntrySeverity, string> = {
  CRITICAL: "bg-red-500/20 text-red-400 border-red-500/40",
  ERROR: "bg-orange-500/15 text-orange-400 border-orange-500/30",
  WARNING: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  INFO: "bg-sky-500/15 text-sky-400 border-sky-500/30",
  DEBUG: "bg-gray-500/15 text-gray-400 border-gray-500/30",
  UNKNOWN: "bg-gray-500/15 text-gray-500 border-gray-500/30",
};

interface ParsedEntriesPanelProps {
  filename: string;
  entries: ParsedEntry[];
  severitySummary: Record<string, number>;
  onClose: () => void;
}

export default function ParsedEntriesPanel({
  filename,
  entries,
  severitySummary,
  onClose,
}: ParsedEntriesPanelProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative flex max-h-[85vh] w-full max-w-4xl flex-col rounded-xl border border-surface-border bg-surface-card shadow-2xl">
        <div className="flex items-center justify-between border-b border-surface-border px-6 py-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-100">Parsed Entries</h3>
            <p className="text-sm text-gray-400">{filename} — {entries.length} entries</p>
          </div>
          <button onClick={onClose} className="btn-secondary text-xs">
            Close
          </button>
        </div>

        <div className="flex flex-wrap gap-2 border-b border-surface-border px-6 py-3">
          {Object.entries(severitySummary).map(([severity, count]) => (
            <span
              key={severity}
              className={`rounded border px-2.5 py-1 text-xs font-semibold ${SEVERITY_STYLES[severity as EntrySeverity] || SEVERITY_STYLES.UNKNOWN}`}
            >
              {severity}: {count}
            </span>
          ))}
        </div>

        <div className="overflow-y-auto p-4">
          <div className="space-y-2">
            {entries.map((entry) => (
              <div
                key={entry.id}
                className="rounded-lg border border-surface-border bg-surface p-3 transition-colors hover:border-sky-500/30"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={`rounded border px-1.5 py-0.5 text-[10px] font-bold uppercase ${SEVERITY_STYLES[entry.severity]}`}
                  >
                    {entry.severity}
                  </span>
                  {entry.timestamp && (
                    <span className="font-mono text-xs text-gray-500">{entry.timestamp}</span>
                  )}
                  {entry.source && (
                    <span className="rounded bg-surface-hover px-1.5 py-0.5 text-xs text-gray-400">
                      {entry.source}
                    </span>
                  )}
                  <span className="text-xs text-gray-600">L{entry.line_number}</span>
                </div>
                <p className="mt-1.5 text-sm text-gray-300">{entry.message}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
