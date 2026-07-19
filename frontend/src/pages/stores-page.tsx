import { zodResolver } from "@hookform/resolvers/zod";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { ConfirmDialog } from "@/components/common/confirm-dialog";
import { DataTable, type DataTableColumn } from "@/components/common/data-table";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { useCreateStore, useDeleteStore, useStores, useUpdateStore } from "@/features/stores/hooks/use-stores";
import { getErrorMessage } from "@/services/api-error";
import type { Store } from "@/types/store";

const storeSchema = z.object({
  name: z.string().trim().min(1, "Name is required.").max(255, "Maximum 255 characters."),
  domain: z.string().trim().min(1, "Domain is required.").max(255, "Maximum 255 characters."),
});

type StoreFormValues = z.infer<typeof storeSchema>;

export function StoresPage() {
  const stores = useStores();
  const deleteStore = useDeleteStore();
  const [formStore, setFormStore] = useState<Store | null | undefined>(undefined);
  const [storeToDelete, setStoreToDelete] = useState<Store | null>(null);

  const columns: DataTableColumn<Store>[] = [
    { id: "name", header: "Name", cell: (store) => <span className="font-medium">{store.name}</span> },
    { id: "domain", header: "Domain", cell: (store) => <span className="font-mono text-xs text-zinc-600 dark:text-zinc-400">{store.domain}</span> },
    {
      id: "actions",
      header: "Actions",
      className: "text-right",
      cell: (store) => (
        <div className="flex justify-end gap-1">
          <Button aria-label={`Edit ${store.name}`} size="icon" variant="ghost" onClick={() => setFormStore(store)}><Pencil className="size-4" /></Button>
          <Button aria-label={`Delete ${store.name}`} size="icon" variant="ghost" onClick={() => setStoreToDelete(store)}><Trash2 className="size-4 text-red-600 dark:text-red-400" /></Button>
        </div>
      ),
    },
  ];

  const confirmDelete = () => {
    if (!storeToDelete) return;
    deleteStore.mutate(storeToDelete.id, {
      onSuccess: () => { toast.success("Store deleted."); setStoreToDelete(null); },
      onError: (error) => toast.error(getErrorMessage(error)),
    });
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Stores" description="Manage the shops that products can be grouped under." actions={<Button onClick={() => setFormStore(null)}><Plus className="size-4" />Add store</Button>} />
      {stores.isLoading ? <Skeleton className="h-64 w-full" /> : stores.isError ? <ErrorState error={stores.error} onRetry={() => void stores.refetch()} /> : <DataTable columns={columns} data={stores.data ?? []} emptyDescription="Create a store before assigning it to products." emptyTitle="No stores yet" getRowKey={(store) => store.id} />}
      <StoreDialog open={formStore !== undefined} store={formStore ?? null} onOpenChange={(open) => !open && setFormStore(undefined)} />
      <ConfirmDialog description={`The store “${storeToDelete?.name ?? ""}” will be permanently deleted.`} isPending={deleteStore.isPending} open={storeToDelete !== null} title="Delete store?" onConfirm={confirmDelete} onOpenChange={(open) => !open && setStoreToDelete(null)} />
    </div>
  );
}

function StoreDialog({ open, store, onOpenChange }: { open: boolean; store: Store | null; onOpenChange: (open: boolean) => void }) {
  const createStore = useCreateStore();
  const updateStore = useUpdateStore();
  const form = useForm<StoreFormValues>({ resolver: zodResolver(storeSchema), defaultValues: { name: "", domain: "" } });

  useEffect(() => { form.reset({ name: store?.name ?? "", domain: store?.domain ?? "" }); }, [form, store, open]);

  const onSuccess = () => {
    toast.success(store ? "Store updated." : "Store created.");
    onOpenChange(false);
  };
  const onError = (error: unknown) => toast.error(getErrorMessage(error));

  const submit = (values: StoreFormValues) => {
    if (store) {
      updateStore.mutate({ id: store.id, payload: values }, { onSuccess, onError });
      return;
    }

    createStore.mutate(values, {
      onSuccess: () => { toast.success(store ? "Store updated." : "Store created."); onOpenChange(false); },
      onError,
    });
  };

  const isPending = createStore.isPending || updateStore.isPending;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader><DialogTitle>{store ? "Edit store" : "Add store"}</DialogTitle><DialogDescription>Use a recognizable name and the shop domain.</DialogDescription></DialogHeader>
        <form className="space-y-4" onSubmit={form.handleSubmit(submit)}>
          <StoreField error={form.formState.errors.name?.message} label="Name"><Input disabled={isPending} placeholder="Books to Scrape" {...form.register("name")} /></StoreField>
          <StoreField error={form.formState.errors.domain?.message} label="Domain"><Input disabled={isPending} placeholder="books.toscrape.com" {...form.register("domain")} /></StoreField>
          <Button className="w-full" disabled={isPending} type="submit">{isPending ? <Spinner /> : null}{store ? "Save changes" : "Create store"}</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function StoreField({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return <label className="block space-y-1.5"><span className="text-sm font-medium">{label}</span>{children}{error ? <span className="block text-xs text-red-600 dark:text-red-400">{error}</span> : null}</label>;
}
