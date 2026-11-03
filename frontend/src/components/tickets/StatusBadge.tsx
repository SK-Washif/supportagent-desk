import type { TicketStatus } from "../../types";
import { Badge, type Tone } from "../ui/Badge";

const tone: Record<TicketStatus, Tone> = { Pending: "warning", Processing: "processing", Resolved: "success" };

export function StatusBadge({ status }: { status: TicketStatus }) {
  return <Badge tone={tone[status]}>{status}</Badge>;
}
