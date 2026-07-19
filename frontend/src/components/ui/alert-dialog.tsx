import type { ComponentPropsWithoutRef, ReactNode } from "react";

import * as AlertDialogPrimitive from "@radix-ui/react-alert-dialog";

import { buttonVariants } from "@/components/ui/button-variants";
import { cn } from "@/lib/utils";

export const AlertDialog = AlertDialogPrimitive.Root;
export const AlertDialogTrigger = AlertDialogPrimitive.Trigger;

export function AlertDialogContent({
  className,
  children,
  ...props
}: ComponentPropsWithoutRef<typeof AlertDialogPrimitive.Content>) {
  return (
    <AlertDialogPrimitive.Portal>
      <AlertDialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/40 backdrop-blur-[1px]" />
      <AlertDialogPrimitive.Content
        className={cn(
          "fixed left-1/2 top-1/2 z-50 grid w-[calc(100%-2rem)] max-w-md -translate-x-1/2 -translate-y-1/2 gap-4 rounded-xl border border-zinc-200 bg-white p-6 shadow-xl focus:outline-none dark:border-zinc-800 dark:bg-zinc-950",
          className,
        )}
        {...props}
      >
        {children}
      </AlertDialogPrimitive.Content>
    </AlertDialogPrimitive.Portal>
  );
}

export function AlertDialogHeader({ children }: { children: ReactNode }) {
  return <div className="space-y-1.5">{children}</div>;
}

export function AlertDialogTitle(props: ComponentPropsWithoutRef<typeof AlertDialogPrimitive.Title>) {
  return <AlertDialogPrimitive.Title className="text-lg font-semibold" {...props} />;
}

export function AlertDialogDescription(
  props: ComponentPropsWithoutRef<typeof AlertDialogPrimitive.Description>,
) {
  return <AlertDialogPrimitive.Description className="text-sm text-zinc-500 dark:text-zinc-400" {...props} />;
}

export function AlertDialogFooter({ children }: { children: ReactNode }) {
  return <div className="flex justify-end gap-2">{children}</div>;
}

export function AlertDialogCancel(props: ComponentPropsWithoutRef<typeof AlertDialogPrimitive.Cancel>) {
  return <AlertDialogPrimitive.Cancel className={buttonVariants({ variant: "outline" })} {...props} />;
}

export function AlertDialogAction({
  className,
  ...props
}: ComponentPropsWithoutRef<typeof AlertDialogPrimitive.Action>) {
  return <AlertDialogPrimitive.Action className={cn(buttonVariants({ variant: "destructive" }), className)} {...props} />;
}
