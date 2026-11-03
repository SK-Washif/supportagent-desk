import { Loader2 } from "lucide-react";
import { cx } from "../../utils/format";

export function Spinner({ size = 16 }: { size?: number }) {
  return <Loader2 size={size} className="spin" aria-hidden="true" />;
}

export function LoadingRow({ label = "Loading…" }: { label?: string }) {
  return (
    <div className={cx("flex items-center justify-center gap-2 py-10 text-sm text-muted")}>
      <Spinner /> {label}
    </div>
  );
}