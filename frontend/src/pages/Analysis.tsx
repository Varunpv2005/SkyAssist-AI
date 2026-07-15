import { useCallback, useEffect, useState } from "react";
import {
  Search,
  Loader2,
  AlertCircle,
  CheckCircle,
  Play,
  ChevronDown,
  ChevronUp,
  Target,
} from "lucide-react";
import { analysisApi, incidentsApi, ApiError } from "../services/api";
import type { Incident, RCAAnalysis } from "../types";

function ConfidenceBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color =
    pct >= 85 ? "bg-emerald-500" : pct >= 70 ? "bg-amber-500" : "bg-orange-500";

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-gray-400">Confidence Score</span>
        <span className="font-semibold text-gray-200">{pct}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-surface-hover">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export default function Analysis() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [analyses, setAnalyses] = useState<RCAAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const [incData, rcaData] = await Promise.all([
        incidentsApi.list(),
        analysisApi.list(),
      ]);
      setIncidents(incData.incidents);
      setAnalyses(rcaData.analyses);
    } catch {
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAnalyze = async (incidentId: string) => {
    setAnalyzingId(incidentId);
    setError("");
    try {
      await analysisApi.analyze(incidentId);
      await fetchData();
      setExpandedId(incidentId);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Analysis failed");
    } finally {
      setAnalyzingId(null);
    }
  };

  const getAnalysis = (incidentRef: string) =>
    analyses.find((a) => a.incident_ref === incidentRef);

  return (
    <div className="space-y-6">
      <div className="animate-fade-in">
        <h2 className="text-2xl font-bold text-gray-100">Root Cause Analysis</h2>
        <p className="mt-1 text-sm text-gray-400">
          Rule-based analysis with possible causes, recommended actions, and confidence scores.
        </p>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          <AlertCircle className="h-4 w-4" />
          {error}
        </div>
      )}

      {analyses.length > 0 && (
        <div className="card animate-fade-in">
          <div className="mb-4 flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            <h3 className="text-base font-semibold text-gray-100">Completed Analyses</h3>
            <span className="ml-auto text-xs text-gray-500">{analyses.length} total</span>
          </div>
          <div className="space-y-3">
            {analyses.map((rca) => (
              <div
                key={rca.id}
                className="rounded-lg border border-surface-border bg-surface p-4"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="font-mono text-sm font-semibold text-sky-400">
                    {rca.incident_ref}
                  </span>
                  <span className="text-sm font-medium text-gray-200">{rca.issue}</span>
                </div>
                <div className="mt-3 max-w-md">
                  <ConfidenceBar score={rca.confidence_score} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card animate-fade-in">
        <div className="mb-4 flex items-center gap-2">
          <Search className="h-4 w-4 text-sky-400" />
          <h3 className="text-base font-semibold text-gray-100">Analyze Incidents</h3>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-sky-400" />
          </div>
        ) : incidents.length === 0 ? (
          <div className="py-12 text-center">
            <Target className="mx-auto h-10 w-10 text-gray-600" />
            <p className="mt-3 text-sm text-gray-500">
              No incidents available. Upload and parse logs first.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {incidents.map((incident) => {
              const rca = getAnalysis(incident.incident_id);
              const isExpanded = expandedId === incident.incident_id;
              const isAnalyzing = analyzingId === incident.incident_id;

              return (
                <div
                  key={incident.incident_id}
                  className="rounded-lg border border-surface-border bg-surface transition-colors hover:border-sky-500/30"
                >
                  <div className="flex items-center gap-3 p-4">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-sm font-semibold text-sky-400">
                          {incident.incident_id}
                        </span>
                        <span className="text-sm text-gray-300">{incident.issue_type.replace(/_/g, " ")}</span>
                        {rca && (
                          <span className="rounded bg-emerald-500/15 px-2 py-0.5 text-xs text-emerald-400">
                            Analyzed
                          </span>
                        )}
                      </div>
                      <p className="mt-1 truncate text-sm text-gray-500">{incident.description}</p>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      {!rca && (
                        <button
                          onClick={() => handleAnalyze(incident.incident_id)}
                          disabled={isAnalyzing}
                          className="btn-primary px-3 py-1.5 text-xs"
                        >
                          {isAnalyzing ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Play className="h-3.5 w-3.5" />
                          )}
                          Analyze
                        </button>
                      )}
                      {rca && (
                        <button
                          onClick={() =>
                            setExpandedId(isExpanded ? null : incident.incident_id)
                          }
                          className="btn-secondary px-3 py-1.5 text-xs"
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-3.5 w-3.5" />
                          ) : (
                            <ChevronDown className="h-3.5 w-3.5" />
                          )}
                          Details
                        </button>
                      )}
                    </div>
                  </div>

                  {isExpanded && rca && (
                    <div className="border-t border-surface-border px-4 pb-4 pt-3">
                      <div className="mb-4 max-w-md">
                        <ConfidenceBar score={rca.confidence_score} />
                      </div>
                      <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                          <p className="text-xs font-medium uppercase text-gray-500">Issue</p>
                          <p className="mt-1 text-sm font-medium text-gray-200">{rca.issue}</p>
                        </div>
                        <div>
                          <p className="text-xs font-medium uppercase text-gray-500">
                            Recommended Action
                          </p>
                          <p className="mt-1 text-sm text-gray-300">{rca.recommended_action}</p>
                        </div>
                      </div>
                      <div className="mt-4">
                        <p className="text-xs font-medium uppercase text-gray-500">
                          Possible Causes
                        </p>
                        <ul className="mt-2 space-y-1.5">
                          {rca.possible_causes.map((cause, i) => (
                            <li
                              key={i}
                              className="flex items-start gap-2 text-sm text-gray-300"
                            >
                              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-sky-400" />
                              {cause}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
