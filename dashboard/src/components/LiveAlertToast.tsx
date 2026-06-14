import { useEffect, useState } from "react";
import { AlertTriangle, X } from "lucide-react";
import { WSMessage } from "../hooks/useLiveFeed";

interface ToastItem {
  id: number;
  message: string;
  severity: string;
}

let counter = 0;

export default function LiveAlertToast({ lastMessage }: { lastMessage: WSMessage | null }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  useEffect(() => {
    if (!lastMessage) return;
    if (lastMessage.channel === "alerts") {
      const id = ++counter;
      const data = lastMessage.data;
      setToasts((t) => [
        ...t,
        {
          id,
          message: `Session ${data.session_id}: ${data.verdict} (score ${data.integrity_score})`,
          severity: data.verdict,
        },
      ]);
      setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 8000);
    }
  }, [lastMessage]);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 w-80">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="bg-cardBg2 border border-red-500/40 rounded-lg p-3 shadow-xl flex items-start gap-3 animate-pulse"
        >
          <AlertTriangle size={20} className="text-red-400 mt-0.5 flex-shrink-0" />
          <p className="text-sm flex-1">{t.message}</p>
          <button onClick={() => setToasts((ts) => ts.filter((x) => x.id !== t.id))}>
            <X size={16} className="text-slate-400 hover:text-white" />
          </button>
        </div>
      ))}
    </div>
  );
}
