import { RefreshCw, TriangleAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { getErrorMessage } from "@/services/api-error";

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  return (
    <div className="flex min-h-56 flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50/50 px-6 py-10 text-center dark:border-red-950 dark:bg-red-950/20">
      <TriangleAlert className="size-5 text-red-600 dark:text-red-400" />
      <h3 className="mt-3 font-medium">Could not load this data</h3>
      <p className="mt-1 max-w-md text-sm text-zinc-500 dark:text-zinc-400">{getErrorMessage(error)}</p>
      {onRetry ? (
        <Button className="mt-5" variant="outline" onClick={onRetry}>
          <RefreshCw className="size-4" />
          Try again
        </Button>
      ) : null}
    </div>
  );
}
