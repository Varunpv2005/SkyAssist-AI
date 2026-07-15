import { useCallback, useEffect, useRef, useState } from "react";
import {
  Bot,
  Send,
  Loader2,
  AlertCircle,
  Sparkles,
  ChevronDown,
  Wrench,
} from "lucide-react";
import { aiApi, incidentsApi, ApiError } from "../services/api";
import type { AIResponse, Incident, Remediation } from "../types";

const QUICK_PROMPTS = [
  "Why did this error occur?",
  "Suggest a fix for this issue.",
  "How can I resolve this issue?",
];

export default function AIAssistant() {
  const [mode, setMode] = useState<"chat" | "remediation">("chat");
  const [question, setQuestion] = useState("");
  const [logSnippet, setLogSnippet] = useState("");
  const [severity, setSeverity] = useState("High");
  const [incidentId, setIncidentId] = useState("");
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [responses, setResponses] = useState<AIResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [ollamaStatus, setOllamaStatus] = useState<{
    available: boolean;
    model: string;
    message?: string;
  } | null>(null);
  const [error, setError] = useState("");
  const [remediations, setRemediations] = useState<Remediation[]>([]);
  const [remLoading, setRemLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const fetchInitial = useCallback(async () => {
    try {
      const [history, status, incData, remData] = await Promise.all([
        aiApi.history(),
        aiApi.status(),
        incidentsApi.list(),
        aiApi.remediations(),
      ]);
      setResponses([...history.history].reverse());
      setOllamaStatus(status);
      setIncidents(incData.incidents);
      setRemediations(remData.remediations);
    } catch {
      setError("Failed to load AI assistant data");
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitial();
  }, [fetchInitial]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [responses, loading]);

  const handleAsk = async (q?: string) => {
    const finalQuestion = q || question;
    if (!finalQuestion.trim()) return;

    setLoading(true);
    setError("");

    try {
      const result = await aiApi.ask({
        question: finalQuestion,
        log_snippet: logSnippet || undefined,
        incident_id: incidentId || undefined,
        severity: severity || undefined,
      });
      setResponses((prev) => [...prev, result]);
      if (!q) setQuestion("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "AI request failed");
    } finally {
      setLoading(false);
    }
  };

  const handleRemediate = async () => {
    if (!incidentId) {
      setError("Select an incident for remediation");
      return;
    }
    setRemLoading(true);
    setError("");
    try {
      const result = await aiApi.remediate({
        incident_id: incidentId,
        log_snippet: logSnippet || undefined,
      });
      setRemediations((prev) => [result, ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Remediation failed");
    } finally {
      setRemLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-col gap-4">
      <div className="animate-fade-in flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-100">AI Troubleshooting Assistant</h2>
          <p className="mt-1 text-sm text-gray-400">
            Ask questions about logs and incidents — powered by Ollama + Llama 3.2
          </p>
        </div>
        {ollamaStatus && (
          <div
            className={`flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs ${
              ollamaStatus.available
                ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                : "border-amber-500/30 bg-amber-500/10 text-amber-400"
            }`}
          >
            <Sparkles className="h-3.5 w-3.5" />
            {ollamaStatus.available
              ? `Ollama · ${ollamaStatus.model}`
              : "Fallback mode (Ollama offline)"}
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setMode("chat")}
          className={`rounded-lg px-4 py-1.5 text-sm font-medium ${
            mode === "chat" ? "bg-sky-500/20 text-sky-400" : "text-gray-400 hover:text-gray-200"
          }`}
        >
          <Bot className="mr-1.5 inline h-4 w-4" /> Chat
        </button>
        <button
          onClick={() => setMode("remediation")}
          className={`rounded-lg px-4 py-1.5 text-sm font-medium ${
            mode === "remediation" ? "bg-sky-500/20 text-sky-400" : "text-gray-400 hover:text-gray-200"
          }`}
        >
          <Wrench className="mr-1.5 inline h-4 w-4" /> Remediation
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      <div className="card flex flex-1 flex-col overflow-hidden p-0">
        {mode === "remediation" ? (
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs text-gray-500">Incident (required)</label>
                <select value={incidentId} onChange={(e) => setIncidentId(e.target.value)} className="input-field text-xs">
                  <option value="">Select incident</option>
                  {incidents.map((inc) => (
                    <option key={inc.incident_id} value={inc.incident_id}>
                      {inc.incident_id} — {inc.issue_type.replace(/_/g, " ")}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex items-end">
                <button onClick={handleRemediate} disabled={remLoading || !incidentId} className="btn-primary w-full">
                  {remLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <><Wrench className="h-4 w-4" /> Generate Remediation</>}
                </button>
              </div>
            </div>
            {remediations.length === 0 ? (
              <p className="py-12 text-center text-sm text-gray-500">No remediation history yet</p>
            ) : (
              remediations.map((rem) => (
                <div key={rem.remediation_id} className="rounded-lg border border-surface-border p-4">
                  <div className="mb-2 flex items-center gap-2">
                    <span className="font-mono text-sm text-sky-400">{rem.remediation_id}</span>
                    {rem.incident_ref && <span className="text-xs text-gray-500">{rem.incident_ref}</span>}
                    <span className="ml-auto text-xs text-gray-500">{Math.round(rem.confidence_score * 100)}% confidence</span>
                  </div>
                  <p className="text-xs font-medium uppercase text-gray-500">Recommended Fixes</p>
                  <ul className="mt-1 list-inside list-disc space-y-1">
                    {rem.recommended_fixes.map((f, i) => <li key={i} className="text-sm text-gray-300">{f}</li>)}
                  </ul>
                  <p className="mt-3 text-xs font-medium uppercase text-gray-500">Troubleshooting Steps</p>
                  <ol className="mt-1 list-inside list-decimal space-y-1">
                    {rem.troubleshooting_steps.map((s, i) => <li key={i} className="text-sm text-gray-300">{s}</li>)}
                  </ol>
                </div>
              ))
            )}
          </div>
        ) : (
        <>
        <div className="flex-1 overflow-y-auto p-4">
          {historyLoading ? (
            <div className="flex h-full items-center justify-center">
              <Loader2 className="h-6 w-6 animate-spin text-sky-400" />
            </div>
          ) : responses.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-sky-500/10">
                <Bot className="h-8 w-8 text-sky-400" />
              </div>
              <p className="text-base font-medium text-gray-300">
                Ask me about security issues
              </p>
              <p className="mt-1 max-w-sm text-sm text-gray-500">
                Paste a log snippet or link an incident, then ask a troubleshooting question.
              </p>
              <div className="mt-4 flex flex-wrap justify-center gap-2">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => handleAsk(prompt)}
                    className="btn-secondary text-xs"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {responses.map((resp) => (
                <div key={resp.id} className="space-y-3">
                  <div className="flex justify-end">
                    <div className="max-w-lg rounded-xl rounded-br-sm bg-sky-600 px-4 py-2.5 text-sm text-white">
                      {resp.question}
                    </div>
                  </div>
                  <div className="flex gap-3">
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-sky-500/15">
                      <Bot className="h-4 w-4 text-sky-400" />
                    </div>
                    <div className="min-w-0 flex-1 rounded-xl rounded-tl-sm border border-surface-border bg-surface p-4">
                      <div className="mb-2 flex flex-wrap items-center gap-2">
                        <span
                          className={`rounded px-2 py-0.5 text-[10px] font-semibold uppercase ${
                            resp.source === "ollama"
                              ? "bg-emerald-500/15 text-emerald-400"
                              : "bg-amber-500/15 text-amber-400"
                          }`}
                        >
                          {resp.source === "ollama" ? "AI" : "Rule-based"}
                        </span>
                        <span className="text-xs text-gray-500">
                          {Math.round(resp.confidence_score * 100)}% confidence
                        </span>
                      </div>
                      <p className="text-sm font-semibold text-gray-200">
                        {resp.root_cause}
                      </p>
                      <p className="mt-2 text-sm text-gray-400">{resp.explanation}</p>
                      <div className="mt-3">
                        <p className="text-xs font-medium uppercase text-gray-500">
                          Resolution Steps
                        </p>
                        <ol className="mt-1.5 list-inside list-decimal space-y-1">
                          {resp.resolution_steps.map((step, i) => (
                            <li key={i} className="text-sm text-gray-300">
                              {step}
                            </li>
                          ))}
                        </ol>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </div>

        <div className="border-t border-surface-border p-4">
          <div className="mb-3 grid gap-2 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs text-gray-500">Log Snippet (optional)</label>
              <textarea
                value={logSnippet}
                onChange={(e) => setLogSnippet(e.target.value)}
                placeholder="Paste error log lines here..."
                rows={2}
                className="input-field resize-none text-xs"
              />
            </div>
            <div className="space-y-2">
              <div>
                <label className="mb-1 block text-xs text-gray-500">Link Incident (optional)</label>
                <div className="relative">
                  <select
                    value={incidentId}
                    onChange={(e) => setIncidentId(e.target.value)}
                    className="input-field appearance-none pr-8 text-xs"
                  >
                    <option value="">None</option>
                    {incidents.map((inc) => (
                      <option key={inc.incident_id} value={inc.incident_id}>
                        {inc.incident_id} — {inc.issue_type.replace(/_/g, " ")}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
                </div>
              </div>
              <div>
                <label className="mb-1 block text-xs text-gray-500">Severity</label>
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="input-field text-xs"
                >
                  <option value="Critical">Critical</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !loading && handleAsk()}
              placeholder="Ask a troubleshooting question..."
              className="input-field flex-1"
            />
            <button
              onClick={() => handleAsk()}
              disabled={loading || !question.trim()}
              className="btn-primary px-4"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </button>
          </div>

          <div className="mt-2 flex flex-wrap gap-2">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleAsk(prompt)}
                disabled={loading}
                className="rounded-full border border-surface-border px-3 py-1 text-xs text-gray-400 transition-colors hover:border-sky-500/40 hover:text-sky-400"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
        </>
        )}
      </div>
    </div>
  );
}
