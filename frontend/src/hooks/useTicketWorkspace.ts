import { useCallback, useEffect, useRef, useState } from "react";
import { api, ApiError } from "../services/api";
import type { AgentRun, TicketDetail, TraceEvent } from "../types";

/** Everything the ticket detail view needs: ticket, run history, selected run + traces, triage. */
export function useTicketWorkspace(ticketId: string, onChanged: () => void) {
  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [traces, setTraces] = useState<TraceEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<ApiError | null>(null);
  const [triaging, setTriaging] = useState(false);
  const [triageError, setTriageError] = useState<ApiError | null>(null);
  const [tracesLoading, setTracesLoading] = useState(false);
  const [tracesError, setTracesError] = useState<ApiError | null>(null);
  const activeId = useRef(ticketId);
  const onChangedRef = useRef(onChanged);

  useEffect(() => {
    onChangedRef.current = onChanged;
  }, [onChanged]);

  const traceRequest = useRef(0);
  const loadTraces = useCallback(async (runId: number) => {
    const token = ++traceRequest.current;
    setTracesLoading(true);
    setTracesError(null);
    try {
      const data = await api.getRunTraces(runId);
      if (traceRequest.current === token) setTraces(data);
    } catch (e) {
      if (traceRequest.current === token) {
        setTracesError(e as ApiError);
        setTraces([]);
      }
    } finally {
      if (traceRequest.current === token) setTracesLoading(false);
    }
  }, []);

  const reload = useCallback(
    async (preferRunId?: number) => {
      const id = activeId.current;
      const [detail, history] = await Promise.all([api.getTicket(id), api.listTicketRuns(id)]);
      if (activeId.current !== id) return;
      setTicket(detail);
      setRuns(history);
      const nextRun = preferRunId ?? history[0]?.id ?? null;
      setSelectedRunId(nextRun);
      if (nextRun !== null) await loadTraces(nextRun);
      else setTraces([]);
    },
    [loadTraces],
  );

  useEffect(() => {
    activeId.current = ticketId;
    let cancelled = false;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setTicket(null);
    setRuns([]);
    setTraces([]);
    setSelectedRunId(null);
    setLoadError(null);
    setTriageError(null);
    reload()
      .catch((e) => !cancelled && setLoadError(e as ApiError))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [ticketId, reload]);

  // If the backend says this ticket is Processing (e.g. page reloaded mid-run), keep polling.
  const serverProcessing = ticket?.status === "Processing" && !triaging;
  useEffect(() => {
    if (!serverProcessing) return;
    const timer = window.setInterval(() => {
      reload().then(() => onChangedRef.current()).catch(() => undefined);
    }, 3000);
    return () => window.clearInterval(timer);
  }, [serverProcessing, reload]);

  const selectRun = useCallback(
    (runId: number) => {
      setSelectedRunId(runId);
      void loadTraces(runId);
    },
    [loadTraces],
  );

  const triage = useCallback(async () => {
    setTriaging(true);
    setTriageError(null);
    try {
      const outcome = await api.triage(activeId.current);
      await reload(outcome.run.id); // re-read from the backend: only its answer marks Resolved
    } catch (e) {
      const error = e as ApiError;
      setTriageError(error);
      const failedRunId = typeof error.details.run_id === "number" ? error.details.run_id : undefined;
      await reload(failedRunId).catch(() => undefined);
    } finally {
      setTriaging(false);
      onChangedRef.current();
    }
  }, [reload]);

  const selectedRun = runs.find((r) => r.id === selectedRunId) ?? null;

  return {
    ticket,
    runs,
    selectedRun,
    traces,
    loading,
    loadError,
    triaging,
    triageError,
    tracesLoading,
    tracesError,
    selectRun,
    triage,
  };
}
