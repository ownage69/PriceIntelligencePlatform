import type { ReactNode } from "react";

import { EmptyState } from "@/components/common/empty-state";
import { cn } from "@/lib/utils";

export interface DataTableColumn<T> {
  id: string;
  header: string;
  cell: (row: T) => ReactNode;
  className?: string;
}

export function DataTable<T>({
  data,
  columns,
  getRowKey,
  emptyTitle = "No results",
  emptyDescription = "There is nothing to display yet.",
}: {
  data: T[];
  columns: DataTableColumn<T>[];
  getRowKey: (row: T) => string | number;
  emptyTitle?: string;
  emptyDescription?: string;
}) {
  if (data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />;
  }

  return (
    <div className="overflow-hidden rounded-xl border border-zinc-200 dark:border-zinc-800">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[680px] text-left text-sm">
          <thead className="bg-zinc-50 text-xs uppercase tracking-wide text-zinc-500 dark:bg-zinc-900/50 dark:text-zinc-400">
            <tr>
              {columns.map((column) => (
                <th key={column.id} className={cn("px-4 py-3 font-medium", column.className)} scope="col">
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800">
            {data.map((row) => (
              <tr key={getRowKey(row)} className="transition-colors hover:bg-zinc-50/80 dark:hover:bg-zinc-900/50">
                {columns.map((column) => (
                  <td key={column.id} className={cn("px-4 py-3 align-middle", column.className)}>
                    {column.cell(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
