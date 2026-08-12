import { useEffect, useState } from "react";
import { wsClient, WSMessage } from "@/lib/websocket";

export function useWebSocket(onMessage?: (msg: WSMessage) => void) {
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(true);

  useEffect(() => {
    wsClient.connect();

    const unsubscribe = wsClient.subscribe((msg) => {
      setLastMessage(msg);
      if (onMessage) {
        onMessage(msg);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [onMessage]);

  return { lastMessage, isConnected, emitMockMessage: wsClient.emitMockMessage.bind(wsClient) };
}
