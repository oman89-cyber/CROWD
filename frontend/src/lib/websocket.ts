export type WebSocketMessageType = "CROWD_STATE" | "BOTTLENECK_ALERT" | "ROUTE_UPDATE" | "SIMULATION_TICK";

export interface WSMessage<T = unknown> {
  type: WebSocketMessageType;
  payload: T;
}

type MessageHandler = (msg: WSMessage) => void;

class CrowdSenseWebSocket {
  private ws: WebSocket | null = null;
  private handlers: Set<MessageHandler> = new Set();
  private isConnected: boolean = false;
  private mockInterval: NodeJS.Timeout | null = null;

  connect() {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";
    const isMock = process.env.NEXT_PUBLIC_MOCK_MODE !== "false";

    if (isMock) {
      this.isConnected = true;
      console.log("[CrowdSense WS] Connected in MOCK mode");
      return;
    }

    try {
      this.ws = new WebSocket(wsUrl);
      this.ws.onopen = () => {
        this.isConnected = true;
        console.log("[CrowdSense WS] Real WebSocket connected");
      };
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyHandlers(data);
        } catch (e) {
          console.error("Failed to parse WS message", e);
        }
      };
      this.ws.onclose = () => {
        this.isConnected = false;
        console.log("[CrowdSense WS] Connection closed, attempting reconnect in 3s...");
        setTimeout(() => this.connect(), 3000);
      };
    } catch (e) {
      console.warn("WebSocket connection failed, falling back to mock mode", e);
      this.isConnected = true;
    }
  }

  subscribe(handler: MessageHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  emitMockMessage(msg: WSMessage) {
    this.notifyHandlers(msg);
  }

  private notifyHandlers(msg: WSMessage) {
    this.handlers.forEach((handler) => handler(msg));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    if (this.mockInterval) {
      clearInterval(this.mockInterval);
      this.mockInterval = null;
    }
    this.isConnected = false;
  }
}

export const wsClient = new CrowdSenseWebSocket();
