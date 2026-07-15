import { useCallback, useEffect, useRef, useState } from "react";
import {
  Upload,
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2,
  X,
  Play,
  Eye,
} from "lucide-react";
import { logsApi, ApiError } from "../services/api";
import type { LogFile, LogStatus, ParseLogResponse } from "../types";
import ParsedEntriesPanel from "../components/logs/ParsedEntriesPanel";

const ACCEPTED_TYPES = ".log,.txt,.csv";
const STATUS_CONFIG: Record<
  LogStatus,
  { label: string; color: string; icon: typeof CheckCircle }
> = {
  uploaded: {
    label: "Uploaded",
    color: "bg-sky-500/15 text-sky-400 border-sky-500/30",
    icon: CheckCircle,
  },
  processing: {
    label: "Processing",
    color: "bg-amber-500/15 text-amber-400 border-amber-500/30",
    icon: Clock,
  },
  parsed: {
    label: "Parsed",
    color: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
    icon: CheckCircle,
  },
  failed: {
    label: "Failed",
    color: "bg-red-500/15 text-red-400 border-red-500/30",
    icon: AlertCircle,
  },
};

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString();
}

export default function Logs() {
  const [logs, setLogs] = useState<LogFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [parsingId, setParsingId] = useState<number | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [parsedData, setParsedData] = useState<ParseLogResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchLogs = useCallback(async () => {
    try {
      const data = await logsApi.list();
      setLogs(data.logs);
    } catch {
      setError("Failed to load log files");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    setError("");
    setSuccess("");
    setUploading(true);

    try {
      const result = await logsApi.upload(file);
      setSuccess(result.message);
      await fetchLogs();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Upload failed");
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleParse = async (logId: number) => {
    setParsingId(logId);
    setError("");
    try {
      const result = await logsApi.parse(logId);
      setParsedData(result);
      setSuccess(`Parsed ${result.total_entries} entries from ${result.filename}`);
      await fetchLogs();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Parse failed");
    } finally {
      setParsingId(null);
    }
  };

  const handleViewEntries = async (logId: number) => {
    setError("");
    try {
      const result = await logsApi.getEntries(logId);
      setParsedData(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load entries");
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleUpload(e.dataTransfer.files);
  };

  return (
    <div className="space-y-6">
      {parsedData && (
        <ParsedEntriesPanel
          filename={parsedData.filename}
          entries={parsedData.entries}
          severitySummary={parsedData.severity_summary}
          onClose={() => setParsedData(null)}
        />
      )}

      <div className="animate-fade-in">
        <h2 className="text-2xl font-bold text-gray-100">Log Upload & Parser</h2>
        <p className="mt-1 text-sm text-gray-400">
          Upload security logs, then parse to extract timestamp, severity, message, and source.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
          <button onClick={() => setError("")} className="ml-auto">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">
          <CheckCircle className="h-4 w-4 shrink-0" />
          {success}
          <button onClick={() => setSuccess("")} className="ml-auto">
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`card-hover animate-fade-in cursor-pointer border-2 border-dashed p-10 text-center transition-colors ${
          dragOver
            ? "border-sky-500 bg-sky-500/5"
            : "border-surface-border hover:border-sky-500/40"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_TYPES}
          className="hidden"
          onChange={(e) => handleUpload(e.target.files)}
        />

        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-500/10">
          {uploading ? (
            <Loader2 className="h-7 w-7 animate-spin text-sky-400" />
          ) : (
            <Upload className="h-7 w-7 text-sky-400" />
          )}
        </div>

        <p className="text-base font-medium text-gray-200">
          {uploading ? "Uploading..." : "Drag & drop a log file here"}
        </p>
        <p className="mt-1 text-sm text-gray-500">
          or click to browse — max 10 MB
        </p>
      </div>

      <div className="card animate-fade-in" style={{ animationDelay: "150ms" }}>
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-sky-400" />
            <h3 className="text-base font-semibold text-gray-100">Uploaded Logs</h3>
          </div>
          <span className="text-xs text-gray-500">{logs.length} files</span>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-sky-400" />
          </div>
        ) : logs.length === 0 ? (
          <div className="py-12 text-center">
            <FileText className="mx-auto h-10 w-10 text-gray-600" />
            <p className="mt-3 text-sm text-gray-500">No logs uploaded yet</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-surface-border text-xs uppercase tracking-wider text-gray-500">
                  <th className="pb-3 pr-4 font-medium">File Name</th>
                  <th className="pb-3 pr-4 font-medium">Type</th>
                  <th className="pb-3 pr-4 font-medium">Size</th>
                  <th className="pb-3 pr-4 font-medium">Status</th>
                  <th className="pb-3 pr-4 font-medium">Uploaded</th>
                  <th className="pb-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {logs.map((log) => {
                  const statusCfg = STATUS_CONFIG[log.status];
                  const StatusIcon = statusCfg.icon;
                  const isParsing = parsingId === log.id;

                  return (
                    <tr
                      key={log.id}
                      className="transition-colors hover:bg-surface-hover/50"
                    >
                      <td className="py-3 pr-4">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 shrink-0 text-gray-500" />
                          <span className="font-medium text-gray-200">{log.filename}</span>
                        </div>
                      </td>
                      <td className="py-3 pr-4">
                        <span className="rounded bg-surface-hover px-2 py-0.5 text-xs font-mono text-gray-400">
                          .{log.file_type}
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-gray-400">
                        {formatFileSize(log.file_size)}
                      </td>
                      <td className="py-3 pr-4">
                        <span
                          className={`inline-flex items-center gap-1 rounded border px-2 py-0.5 text-xs font-medium ${statusCfg.color}`}
                        >
                          <StatusIcon className="h-3 w-3" />
                          {statusCfg.label}
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-gray-500">
                        {formatDate(log.created_at)}
                      </td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          {log.status !== "parsed" && (
                            <button
                              onClick={() => handleParse(log.id)}
                              disabled={isParsing}
                              className="btn-primary px-2.5 py-1.5 text-xs"
                            >
                              {isParsing ? (
                                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                              ) : (
                                <Play className="h-3.5 w-3.5" />
                              )}
                              Parse
                            </button>
                          )}
                          {log.status === "parsed" && (
                            <button
                              onClick={() => handleViewEntries(log.id)}
                              className="btn-secondary px-2.5 py-1.5 text-xs"
                            >
                              <Eye className="h-3.5 w-3.5" />
                              View
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
