import type { ReactNode } from "react";
import { cx } from "../../utils/format";

export type Tone = "neutral" | "success" | "warning" | "danger" | "processing";

const tones: Record<Tone, string> = {
  neutral: "bg-subtle text-muted",
  success: "bg-success-soft text-success",
  warning: "bg-warning-soft text-warning",
  danger: "bg-danger-soft text-danger",
  processing: "bg-processing-soft text-processing",
};

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span className={cx("inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium", tones[tone])}>
      {children}
    </span>
  );
}
