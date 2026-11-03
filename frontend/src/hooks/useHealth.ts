import { useEffect, useState } from "react";
import { api, type ApiError } from "../services/api";
import type { HealthInfo } from "../types";

export function useHealth() {
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    let cancelled = false;
    api
      .health()
      .then((data) => !cancelled && setHealth(data))
      .catch((e) => !cancelled && setError(e as ApiError));
    return () => {
      cancelled = true;
    };
  }, []);

  return { health, error, loading: health === null && error === null };
}