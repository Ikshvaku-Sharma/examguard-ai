import { useEffect, useRef, useState } from "react";
import { WS_URL } from "../api";

export interface WSMessage {
  channel: "anomalies" | "alerts" | "reasoning_results";
  data: any;
}

/**
 * Connects to the backend WebSocket and returns the latest message.
 * Auto-reconnects on disconnect.
 */
export function useLiveFeed() {
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const [connected, setConnected]     = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let retryTimeout: number;

    const connect = () => {
      const ws = new WebSocket(`${WS_URL}/ws`);
      wsRef.current = ws;

      ws.onopen  = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        retryTimeout = window.setTimeout(connect, 2000);
      };
      ws.onerror = () => ws.close();
      ws.onmessage = (event) => {
        try {
          const parsed: WSMessage = JSON.parse(event.data);
          setLastMessage(parsed);
        } catch {
          /* ignore malformed messages */
        }
      };
    };

    connect();

    return () => {
      wsRef.current?.close();
      window.clearTimeout(retryTimeout);
    };
  }, []);

  return { lastMessage, connected };
}
