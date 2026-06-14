interface VerdictBadgeProps {
  verdict: "CLEAR" | "SUSPICIOUS" | "COMPROMISED";
}

const STYLES: Record<string, string> = {
  CLEAR:       "bg-green-500/20 text-green-400 border-green-500/40",
  SUSPICIOUS:  "bg-orange-500/20 text-orange-400 border-orange-500/40",
  COMPROMISED: "bg-red-500/20 text-red-400 border-red-500/40",
};

export default function VerdictBadge({ verdict }: VerdictBadgeProps) {
  return (
    <span
      className={`px-3 py-1 rounded-full text-xs font-bold border ${STYLES[verdict] ?? STYLES.SUSPICIOUS}`}
    >
      {verdict}
    </span>
  );
}
