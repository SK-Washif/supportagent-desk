import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../services/api";
import type { TicketSummary } from "../types";

export function useTickets() {
  const [tickets, setTickets] = useState<TicketSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const refresh = useCallback(async () => {
    try {
      setTickets(await api.listTickets());
      setError(null);
    } catch (e) {
      setError(e as ApiError);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void refresh();
  }, [refresh]);

  return { tickets, loading, error, refresh };
}
