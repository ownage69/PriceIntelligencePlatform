import type { LucideIcon } from "lucide-react";
import type { ReactNode } from "react";

import { Inbox } from "lucide-react";

export function EmptyState({
  title,
  description,
  action,
  icon: Icon = Inbox,
}: {
  title: string;
  description: string;
  action?: ReactNode;
  icon?: LucideIcon;
}) {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center rounded-xl border border-dashed border-zinc-300 px-6 py-10 text-center dark:border-zinc-700">
      <div className="rounded-lg bg-zinc-100 p-3 text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
        <Icon className="size-5" />
      </div>
      <h3 className="mt-4 font-medium">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-zinc-500 dark:text-zinc-400">{description}</p>
      {action ? <div className="mt-5">{action}</div> : null}
    </div>
  );
}
