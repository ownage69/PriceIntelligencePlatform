import type { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "flex h-9 w-full rounded-lg border border-zinc-200 bg-transparent px-3 py-1 text-sm shadow-xs outline-none transition-colors placeholder:text-zinc-400 focus-visible:border-zinc-400 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-800 dark:placeholder:text-zinc-600 dark:focus-visible:border-zinc-600",
        className,
      )}
      {...props}
    />
  );
}
