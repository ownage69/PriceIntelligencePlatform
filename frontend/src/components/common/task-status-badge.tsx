import { CircleDashed, CircleX, Clock3, RotateCw, Sparkles } from "lucide-react";

import { Badge, type BadgeProps } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const statusOptions: Record<string, { variant: NonNullable<BadgeProps["variant"]>; icon: typeof Clock3 }> = {
  PENDING: { variant: "warning", icon: Clock3 },
  STARTED: { variant: "secondary", icon: RotateCw },
  SUCCESS: { variant: "success", icon: Sparkles },
  FAILURE: { variant: "danger", icon: CircleX },
  REVOKED: { variant: "danger", icon: CircleX },
};

export function TaskStatusBadge({ status }: { status: string }) {
  const option = statusOptions[status] ?? { variant: "outline" as const, icon: CircleDashed };
  const Icon = option.icon;

  return (
    <Badge variant={option.variant}>
      <Icon className={cn("mr-1 size-3", status === "STARTED" && "animate-spin")} />
      {status}
    </Badge>
  );
}
