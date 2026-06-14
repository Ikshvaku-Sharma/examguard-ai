import { useEffect, useState } from "react";
import { Users, AlertTriangle, ShieldAlert, Activity } from "lucide-react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import StatCard from "../components/StatCard";
import LiveAlertToast from "../components/LiveAlertToast";
import { fetchStats, DashboardStats } from "../api";
import { useLiveFeed } from "../hooks/useLiveFeed";

export default function Overview() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const { lastMessage } = useLiveFeed();
  const [scoreHistory, setScoreHistory] = useState<{ time: string; score: number }[]>([]);

  useEffect(() => {
    fetchStats().then(setStats).catch(console.error);
    const interval = setInterval(() => fetchStats().then(setStats).catch(() => {}), 10000);
    return () => clearInterval(interval);
  }, []);

  // Update live score history chart from reasoning_results
  useEffect(() => {
    if (lastMessage?.channel === "reasoning_results") {
      const { integrity_score, timestamp } = lastMessage.data;
      setScoreHistory((h) => [
        ...h.slice(-19),
        { time: new Date(timestamp).toLocaleTimeString(), score: integrity_score },
      ]);
    }
  }, [lastMessage]);

  return (
    <div>
      <LiveAlertToast lastMessage={lastMessage} />

      <h1 className="text-2xl font-bold mb-1">Overview</h1>
      <p className="text-slate-400 text-sm mb-6">
        Real-time monitoring across all active exam sessions
      </p>

      {/* Stat cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Active Sessions" value={stats?.active_sessions ?? "—"} icon={Users} color="#00C6FF" />
        <StatCard label="Total Incidents" value={stats?.total_incidents ?? "—"} icon={AlertTriangle} color="#F59E0B" />
        <StatCard label="Compromised" value={stats?.compromised_count ?? "—"} icon={ShieldAlert} color="#EF4444" />
        <StatCard label="Avg Integrity Score" value={stats?.avg_integrity ?? "—"} icon={Activity} color="#10B981" />
      </div>

      {/* Live score chart */}
      <div className="bg-cardBg2 rounded-xl p-5 border border-cardBg">
        <h2 className="text-sm font-bold text-slate-300 mb-4 uppercase tracking-wide">
          Live Integrity Score Feed
        </h2>
        {scoreHistory.length === 0 ? (
          <p className="text-slate-500 text-sm py-12 text-center">
            Waiting for live data from agent pipeline…
          </p>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={scoreHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1A3A6B" />
              <XAxis dataKey="time" stroke="#94A3B8" fontSize={11} />
              <YAxis domain={[0, 100]} stroke="#94A3B8" fontSize={11} />
              <Tooltip
                contentStyle={{ background: "#132040", border: "1px solid #1A3A6B", borderRadius: 8 }}
              />
              <Line type="monotone" dataKey="score" stroke="#00C6FF" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
