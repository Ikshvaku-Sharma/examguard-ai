import axios from "axios";

export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const WS_URL  = import.meta.env.VITE_WS_URL  || "ws://localhost:8000";

export const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// ── Types ─────────────────────────────────────────────────────────

export interface SessionData {
  id: string;
  student_id: string;
  exam_id: string;
  started_at: string;
  ended_at: string | null;
  integrity_score: number;
  verdict: "CLEAR" | "SUSPICIOUS" | "COMPROMISED";
  is_active: boolean;
}

export interface IncidentData {
  id: number;
  session_id: string;
  timestamp: string;
  integrity_score: number;
  verdict: "CLEAR" | "SUSPICIOUS" | "COMPROMISED";
  reasoning: string;
  triggered_by: string[];
  report_url: string | null;
}

export interface DashboardStats {
  total_sessions: number;
  active_sessions: number;
  total_incidents: number;
  compromised_count: number;
  suspicious_count: number;
  avg_integrity: number;
}

// ── API calls ────────────────────────────────────────────────────

export const fetchStats     = () => api.get<DashboardStats>("/api/v1/stats/").then(r => r.data);
export const fetchSessions  = (activeOnly = false) =>
  api.get<SessionData[]>("/api/v1/sessions/", { params: { active_only: activeOnly } }).then(r => r.data);
export const fetchIncidents = (limit = 50) =>
  api.get<IncidentData[]>("/api/v1/incidents/", { params: { limit } }).then(r => r.data);
