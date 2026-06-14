import { useEffect, useState } from "react";
import VerdictBadge from "../components/VerdictBadge";
import { fetchSessions, SessionData } from "../api";

export default function Sessions() {
  const [sessions, setSessions] = useState<SessionData[]>([]);
  const [activeOnly, setActiveOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchSessions(activeOnly)
      .then(setSessions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [activeOnly]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-1">Exam Sessions</h1>
          <p className="text-slate-400 text-sm">All monitored sessions and their current integrity status</p>
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
          <input
            type="checkbox"
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
            className="accent-accent"
          />
          Active only
        </label>
      </div>

      <div className="bg-cardBg2 rounded-xl border border-cardBg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-cardBg text-slate-400 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">Session ID</th>
              <th className="px-4 py-3 text-left">Student</th>
              <th className="px-4 py-3 text-left">Exam</th>
              <th className="px-4 py-3 text-left">Started</th>
              <th className="px-4 py-3 text-left">Integrity Score</th>
              <th className="px-4 py-3 text-left">Verdict</th>
              <th className="px-4 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="text-center py-8 text-slate-500">Loading…</td></tr>
            ) : sessions.length === 0 ? (
              <tr><td colSpan={7} className="text-center py-8 text-slate-500">No sessions found</td></tr>
            ) : (
              sessions.map((s) => (
                <tr key={s.id} className="border-t border-cardBg hover:bg-cardBg/50">
                  <td className="px-4 py-3 font-mono text-xs">{s.id}</td>
                  <td className="px-4 py-3">{s.student_id}</td>
                  <td className="px-4 py-3">{s.exam_id}</td>
                  <td className="px-4 py-3 text-slate-400">{new Date(s.started_at).toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        s.integrity_score >= 75 ? "text-green-400" :
                        s.integrity_score >= 50 ? "text-orange-400" : "text-red-400"
                      }
                    >
                      {s.integrity_score}/100
                    </span>
                  </td>
                  <td className="px-4 py-3"><VerdictBadge verdict={s.verdict} /></td>
                  <td className="px-4 py-3">
                    {s.is_active ? (
                      <span className="text-green-400">● Live</span>
                    ) : (
                      <span className="text-slate-500">○ Ended</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
