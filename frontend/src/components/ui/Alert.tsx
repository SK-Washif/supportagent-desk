import { AlertCircle, CheckCircle2, Info } from "lucide-react";
import type { ReactNode } from "react";
import { cx } from "../../utils/format";

const styles = {
  error: "border-danger/30 bg-danger-soft text-danger",
  info: "border-processing/30 bg-processing-soft text-processing",
  success: "border-success/30 bg-success-soft text-success",
} as const;

export function Alert({
  tone = "error",
  title,
  children,
}: {
  tone?: keyof typeof styles;
  title: string;
  children?: ReactNode;
}) {
  const Icon = tone === "error" ? AlertCircle : tone === "success" ? CheckCircle2 : Info;
  return (
    <div role={tone === "error" ? "alert" : "status"} className={cx("flex gap-3 rounded-md border p-3.5", styles[tone])}>
      <Icon size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
      <div className="min-w-0 text-sm">
        <p className="font-medium">{title}</p>
        {children && <div className="mt-0.5 break-words text-ink/80">{children}</div>}
      </div>
    </div>
  );
}
