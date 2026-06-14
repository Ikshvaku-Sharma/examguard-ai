import { Routes, Route, NavLink } from "react-router-dom";
import { Shield, LayoutDashboard, AlertTriangle, Users } from "lucide-react";
import Overview from "./pages/Overview";
import Sessions from "./pages/Sessions";
import Incidents from "./pages/Incidents";
import { useLiveFeed } from "./hooks/useLiveFeed";

export default function App() {
  const { connected } = useLiveFeed();

  const navItem =
    "flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors";
  const active   = "bg-midBlue text-accent";
  const inactive = "text-slate-300 hover:bg-cardBg2 hover:text-white";

  return (
    <div className="flex min-h-screen bg-navy text-white">
      {/* Sidebar */}
      <aside className="w-64 border-r border-cardBg2 p-5 flex flex-col gap-2">
        <div className="flex items-center gap-2 mb-8 px-2">
          <Shield className="text-accent" size={26} />
          <div>
            <h1 className="font-bold text-lg leading-tight">ExamGuard AI</h1>
            <p className="text-xs text-slate-400">Admin Dashboard</p>
          </div>
        </div>

        <NavLink to="/" className={({ isActive }) => `${navItem} ${isActive ? active : inactive}`}>
          <LayoutDashboard size={18} /> Overview
        </NavLink>
        <NavLink to="/sessions" className={({ isActive }) => `${navItem} ${isActive ? active : inactive}`}>
          <Users size={18} /> Sessions
        </NavLink>
        <NavLink to="/incidents" className={({ isActive }) => `${navItem} ${isActive ? active : inactive}`}>
          <AlertTriangle size={18} /> Incidents
        </NavLink>

        <div className="mt-auto px-2 py-3 flex items-center gap-2 text-xs">
          <span
            className={`w-2.5 h-2.5 rounded-full ${connected ? "bg-green-400" : "bg-red-400"}`}
          />
          <span className="text-slate-400">
            {connected ? "Live feed connected" : "Reconnecting…"}
          </span>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-6 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/sessions" element={<Sessions />} />
          <Route path="/incidents" element={<Incidents />} />
        </Routes>
      </main>
    </div>
  );
}
