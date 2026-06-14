import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
}

export default function StatCard({ label, value, icon: Icon, color = "#00C6FF" }: StatCardProps) {
  return (
    <div className="bg-cardBg2 rounded-xl p-5 shadow-lg border border-cardBg flex items-center gap-4">
      <div
        className="w-12 h-12 rounded-full flex items-center justify-center"
        style={{ backgroundColor: `${color}22` }}
      >
        <Icon size={22} color={color} />
      </div>
      <div>
        <p className="text-2xl font-bold leading-tight" style={{ color }}>
          {value}
        </p>
        <p className="text-sm text-slate-400">{label}</p>
      </div>
    </div>
  );
}
