import { ExternalLink, PlugZap } from "lucide-react";
import { useState, type ReactNode } from "react";
import { PageHeader } from "../components/layout/AppShell";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card, CardHeader } from "../components/ui/Card";
import { LoadingRow } from "../components/ui/Spinner";
import { useHealth } from "../hooks/useHealth";
import { api, type ApiError } from "../services/api";
import type { LlmCheck } from "../types";

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 px-5 py-3.5">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className="text-sm font-semibold text-ink">{children}</dd>
    </div>
  );
}

function SetupGuide() {
  const steps: ReactNode[] = [
    <>
      Open{" "}
      <a
        className="inline-flex items-center gap-1 font-semibold text-primary underline underline-offset-2"
        href="https://console.groq.com/keys"
        target="_blank"
        rel="noreferrer"
      >
        console.groq.com/keys <ExternalLink size={12} aria-hidden="true" />
      </a>{" "}
      and sign in. The free plan needs no credit card.
    </>,
    <>
      Choose <strong>Create API Key</strong>, give it any name, and copy the key
      (it starts with <code className="font-mono text-xs">gsk_</code>).
    </>,
    <>
      Open <code className="font-mono text-xs">backend/.env</code> and set{" "}
      <code className="font-mono text-xs">GROQ_API_KEY=gsk_...</code>
    </>,
    <>
      Restart the backend, then come back here and press <strong>Test connection</strong>.
    </>,
  ];
  return (
    <Card>
      <CardHeader title="Connect Groq (free)" />
      <ol className="space-y-3 p-5 text-sm text-ink">
        {steps.map((step, i) => (
          <li key={i} className="flex gap-3">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-soft text-xs font-bold text-primary">
              {i + 1}
            </span>
            <span>{step}</span>
          </li>
        ))}
      </ol>
    </Card>
  );
}

export function SettingsPage() {
  const { health, error, loading } = useHealth();
  const [check, setCheck] = useState<LlmCheck | null>(null);
  const [checkError, setCheckError] = useState<ApiError | null>(null);
  const [checking, setChecking] = useState(false);

  const handleTest = async () => {
    setChecking(true);
    setCheckError(null);
    setCheck(null);
    try {
      const result = await api.checkLlm();
      setCheck(result);
    } catch (e) {
      setCheckError(e as ApiError);
    } finally {
      setChecking(false);
    }
  };

  return (
    <>
      <PageHeader
        title="Settings"
        description="Read-only view of the backend configuration. Change values in backend/.env."
      />

      {error ? (
        <Alert title="Backend unreachable">{error.message}</Alert>
      ) : loading || !health ? (
        <LoadingRow label="Checking backend…" />
      ) : (
        <div className="space-y-4">
          {!health.llm_configured && (
            <Alert title="Groq API key is not configured">
              Tickets are viewable, but the triage agent cannot run. Set{" "}
              <code className="font-mono text-xs">GROQ_API_KEY</code> in{" "}
              <code className="font-mono text-xs">backend/.env</code> and restart the backend.
            </Alert>
          )}

          <Card>
            <CardHeader
              title="AI provider"
              action={
                <Button
                  variant="secondary"
                  size="sm"
                  icon={<PlugZap size={14} />}
                  loading={checking}
                  onClick={handleTest}
                  disabled={!health.llm_configured}
                >
                  Test connection
                </Button>
              }
            />
            <dl className="divide-y divide-line">
              <Row label="Provider">
                <Badge tone="processing">{health.llm_provider}</Badge>
              </Row>
              <Row label="API key">
                <Badge tone={health.llm_configured ? "success" : "warning"}>
                  {health.llm_configured ? "Configured" : "Not configured"}
                </Badge>
              </Row>
              <Row label="Main model">
                <code className="font-mono text-xs">{health.llm_model}</code>
              </Row>
              <Row label="Fallback model">
                <code className="font-mono text-xs">
                  {health.llm_fallback_model ?? "—"}
                </code>
              </Row>
              <Row label="Max agent iterations">{health.max_agent_iterations}</Row>
            </dl>
            {check && (
              <div className="border-t border-line p-5">
                <Alert tone="success" title="The API key works">
                  <p className="text-sm">
                    Main model:{" "}
                    <strong>
                      {check.models[health.llm_model] ? "✅ available" : "❌ unavailable"}
                    </strong>
                  </p>
                  {health.llm_fallback_model && (
                    <p className="text-sm">
                      Fallback:{" "}
                      <strong>
                        {check.models[health.llm_fallback_model]
                          ? "✅ available"
                          : "❌ unavailable"}
                      </strong>
                    </p>
                  )}
                </Alert>
              </div>
            )}
            {checkError && (
              <div className="border-t border-line p-5">
                <Alert title="Connection test failed">{checkError.message}</Alert>
              </div>
            )}
          </Card>

          <Card>
            <CardHeader title="Backend" />
            <dl className="divide-y divide-line">
              <Row label="API status">
                <Badge tone="success">{health.status}</Badge>
              </Row>
              <Row label="Database">
                <Badge tone={health.database === "ok" ? "success" : "danger"}>
                  {health.database}
                </Badge>
              </Row>
            </dl>
          </Card>

          {!health.llm_configured && <SetupGuide />}
        </div>
      )}
    </>
  );
}