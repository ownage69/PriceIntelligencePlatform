import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";

export function Pagination({
  page,
  totalPages,
  totalItems,
  size,
  onPageChange,
}: {
  page: number;
  totalPages: number;
  totalItems: number;
  size: number;
  onPageChange: (nextPage: number) => void;
}) {
  if (totalItems === 0) {
    return null;
  }

  const resolvedTotalPages = Math.max(totalPages, 1);
  const start = (page - 1) * size + 1;
  const end = Math.min(page * size, totalItems);

  return (
    <div className="flex flex-col gap-3 text-sm text-zinc-500 dark:text-zinc-400 sm:flex-row sm:items-center sm:justify-between">
      <span>
        {start}–{end} of {totalItems}
      </span>
      <div className="flex items-center gap-2">
        <Button
          aria-label="Previous page"
          disabled={page <= 1}
          size="icon"
          variant="outline"
          onClick={() => onPageChange(page - 1)}
        >
          <ChevronLeft className="size-4" />
        </Button>
        <span className="min-w-20 text-center text-xs">
          Page {page} / {resolvedTotalPages}
        </span>
        <Button
          aria-label="Next page"
          disabled={page >= resolvedTotalPages}
          size="icon"
          variant="outline"
          onClick={() => onPageChange(page + 1)}
        >
          <ChevronRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}
