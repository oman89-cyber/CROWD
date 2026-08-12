/**
 * Simple session storage for user authentication state
 * Uses localStorage for persistence across page refreshes
 */

import { User } from "@/types/user";

const SESSION_KEY = "crowdshield_session";
const USER_KEY = "crowdshield_user";

export interface SessionData {
  sessionId: string;
  ticketId: string;
  user: User;
  timestamp: number;
}

export function saveSession(user: User): void {
  if (typeof window === "undefined") return;

  const sessionData: SessionData = {
    sessionId: user.crowdId,
    ticketId: user.ticketId,
    user: user,
    timestamp: Date.now(),
  };

  try {
    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (error) {
    console.error("Failed to save session:", error);
  }
}

export function getSession(): SessionData | null {
  if (typeof window === "undefined") return null;

  try {
    const data = localStorage.getItem(SESSION_KEY);
    if (!data) return null;

    const session: SessionData = JSON.parse(data);

    // Check if session is less than 24 hours old
    const age = Date.now() - session.timestamp;
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours

    if (age > maxAge) {
      clearSession();
      return null;
    }

    return session;
  } catch (error) {
    console.error("Failed to get session:", error);
    return null;
  }
}

export function getUser(): User | null {
  if (typeof window === "undefined") return null;

  try {
    const data = localStorage.getItem(USER_KEY);
    if (!data) return null;

    return JSON.parse(data);
  } catch (error) {
    console.error("Failed to get user:", error);
    return null;
  }
}

export function getSessionId(): string | null {
  const session = getSession();
  return session?.sessionId || null;
}

export function clearSession(): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(USER_KEY);
  } catch (error) {
    console.error("Failed to clear session:", error);
  }
}

export function isSessionValid(): boolean {
  return getSession() !== null;
}
