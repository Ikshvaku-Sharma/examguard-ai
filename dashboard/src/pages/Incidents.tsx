import { useEffect, useState } from "react";
import { Download, FileWarning } from "lucide-react";
import VerdictBadge from "../components/VerdictBadge";
import { fetchIncidents, IncidentData, API_URL } from "../api";

export default function Incidents() {
  const [incidents, setIncidents] = useState<IncidentData[]>([]);
  const [loading, setLoading]     = useState(true);

  useEffect(() => {
    fetchIncidents()
      .then(setIncidents)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-1">Incident Log</h1>
      <p className="text-slate-400 text-sm mb-6">
        Autonomous AI-generated incident reports with reasoning trace
      </p>

      {loading ? (
        <p className="text-slate-500 text-sm py-12 text-center">Loading…</p>
      ) : incidents.length === 0 ? (
        <div className="bg-cardBg2 rounded-xl border border-cardBg p-12 text-center">
          <FileWarning className="mx-auto mb-3 text-slate-500" size={36} />
          <p className="text-slate-400">No incidents recorded yet. ExamGuard AI is monitoring.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {incidents.map((inc) => (
            <div key={inc.id} className="bg-cardBg2 rounded-xl border border-cardBg p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs text-slate-400">{inc.session_id}</span>
                  <VerdictBadge verdict={inc.verdict} />
                  <span className="text-sm text-slate-400">
                    Score: <strong className="text-white">{inc.integrity_score}/100</strong>
                  </span>
                </div>
                <span className="text-xs text-slate-500">
                  {new Date(inc.timestamp).toLocaleString()}
                </span>
              </div>

              <p className="text-sm text-slate-300 bg-cardBg rounded-lg p-3 border-l-2 border-accent mb-3">
                {inc.reasoning}
              </p>

              <div className="flex items-center justify-between">
                <div className="flex gap-2 flex-wrap">
                  {inc.triggered_by.map((evt, i) => (
                    <span key={i} className="text-xs bg-midBlue/40 text-accent px-2 py-1 rounded-md">
                      {evt}
                    </span>
                  ))}
                </div>
                {inc.report_url && (
                  <a
                    href={`${API_URL}${inc.report_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1.5 text-xs text-accent hover:underline"
                  >
                    <Download size={14} /> PDF Report
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
