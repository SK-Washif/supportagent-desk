import { useEffect, useState } from "react";
import { api, type ApiError } from "../services/api";
import type { HealthInfo } from "../types";

export function useHealth() {
  const [health, setHealth] = useState<HealthInfo | null>(null);
  const [error, setError] = useState<ApiError | null>(null);

  

  return { health, error, loading: health === null && error === null };
}