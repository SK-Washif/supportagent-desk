import type { ResolutionTag } from "../../types";
import { Badge } from "../ui/Badge";

export function ResolutionBadge({ tag }: { tag: ResolutionTag }) {
  return <Badge tone={tag === "Auto-Resolve" ? "success" : "processing"}>[{tag}]</Badge>;
}
