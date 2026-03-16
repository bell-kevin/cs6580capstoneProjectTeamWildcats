"use client";
import { useState, useEffect } from "react";

export type SpaceStatus = "online" | "warming" | "offline" | "unknown";

export function useSpaceStatus() {
  const [status, setStatus] = useState<SpaceStatus>("unknown");

  const check = async () => {
    try {
      const res = await fetch("/api/warmup", { method: "GET" });
      if (res.ok) {
        setStatus("online");
      } else if (res.status === 503) {
        setStatus("warming");
      } else {
        setStatus("offline");
      }
    } catch {
      setStatus("offline");
    }
  };

  useEffect(() => {
    check();
    const interval = setInterval(check, 5 * 60 * 1000); // every 5 min
    return () => clearInterval(interval);
  }, []);

  return { status, refresh: check };
}
