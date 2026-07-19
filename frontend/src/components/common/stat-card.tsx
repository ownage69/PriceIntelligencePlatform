import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

export function StatCard({
  label,
  value,
  icon: Icon,
  isLoading = false,
}: {
  label: string;
  value: number | string;
  icon: LucideIcon;
  isLoading?: boolean;
}) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between p-5">
        <div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight">
            {isLoading ? <span className="text-zinc-300 dark:text-zinc-700">—</span> : value}
          </p>
        </div>
        <div className="rounded-lg border border-zinc-200 p-2.5 text-zinc-600 dark:border-zinc-800 dark:text-zinc-400">
          <Icon className="size-4" />
        </div>
      </CardContent>
    </Card>
  );
}
