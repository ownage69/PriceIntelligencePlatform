import { zodResolver } from "@hookform/resolvers/zod";
import { Check, Link2, Plus, Tags } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Spinner } from "@/components/ui/spinner";
import { useCreateProduct, useCreateProductWithRelations } from "@/features/products/hooks/use-products";
import { useStores } from "@/features/stores/hooks/use-stores";
import { useTags } from "@/features/tags/hooks/use-tags";
import { getErrorMessage } from "@/services/api-error";

const productSchema = z.object({
  name: z.string().trim().min(1, "Name is required.").max(255, "Maximum 255 characters."),
  target_url: z.string().trim().url("Enter a valid URL."),
});

type ProductFormValues = z.infer<typeof productSchema>;

const relationProductSchema = productSchema.extend({
  store_id: z.string(),
  tag_ids: z.array(z.number()),
});

type RelationProductFormValues = z.infer<typeof relationProductSchema>;

export function ProductCreateDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [mode, setMode] = useState<"basic" | "relations">("basic");

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add product</DialogTitle>
          <DialogDescription>Create a standalone product or immediately connect it to a store and tags.</DialogDescription>
        </DialogHeader>
        <div className="grid grid-cols-2 rounded-lg bg-zinc-100 p-1 dark:bg-zinc-900">
          <Button
            className="justify-center"
            size="sm"
            variant={mode === "basic" ? "default" : "ghost"}
            onClick={() => setMode("basic")}
          >
            <Link2 className="size-3.5" />
            Basic
          </Button>
          <Button
            className="justify-center"
            size="sm"
            variant={mode === "relations" ? "default" : "ghost"}
            onClick={() => setMode("relations")}
          >
            <Tags className="size-3.5" />
            With relations
          </Button>
        </div>
        {mode === "basic" ? (
          <BasicProductForm onSuccess={() => onOpenChange(false)} />
        ) : (
          <RelatedProductForm onSuccess={() => onOpenChange(false)} />
        )}
      </DialogContent>
    </Dialog>
  );
}

function BasicProductForm({ onSuccess }: { onSuccess: () => void }) {
  const createProduct = useCreateProduct();
  const form = useForm<ProductFormValues>({
    resolver: zodResolver(productSchema),
    defaultValues: { name: "", target_url: "" },
  });

  const submit = (values: ProductFormValues) => {
    createProduct.mutate(values, {
      onSuccess: () => {
        toast.success("Product created.");
        form.reset();
        onSuccess();
      },
      onError: (error) => toast.error(getErrorMessage(error)),
    });
  };

  return (
    <form className="space-y-4" onSubmit={form.handleSubmit(submit)}>
      <Field label="Name" error={form.formState.errors.name?.message}>
        <Input placeholder="Wireless mechanical keyboard" disabled={createProduct.isPending} {...form.register("name")} />
      </Field>
      <Field label="Product URL" error={form.formState.errors.target_url?.message} hint="The URL will be monitored by the parser.">
        <Input placeholder="https://example.com/product" disabled={createProduct.isPending} {...form.register("target_url")} />
      </Field>
      <Button className="w-full" disabled={createProduct.isPending} type="submit">
        {createProduct.isPending ? <Spinner /> : <Plus className="size-4" />}
        Add product
      </Button>
    </form>
  );
}

function RelatedProductForm({ onSuccess }: { onSuccess: () => void }) {
  const { data: stores = [], isLoading: storesLoading } = useStores();
  const { data: tags = [], isLoading: tagsLoading } = useTags();
  const createProduct = useCreateProductWithRelations();
  const form = useForm<RelationProductFormValues>({
    resolver: zodResolver(relationProductSchema),
    defaultValues: { name: "", target_url: "", store_id: "", tag_ids: [] },
  });

  useEffect(() => {
    if (!storesLoading && !tagsLoading) {
      form.setFocus("name");
    }
  }, [form, storesLoading, tagsLoading]);

  const toggleTag = (tagId: number) => {
    const selected = form.getValues("tag_ids");
    form.setValue(
      "tag_ids",
      selected.includes(tagId) ? selected.filter((id) => id !== tagId) : [...selected, tagId],
      { shouldDirty: true },
    );
  };

  const submit = (values: RelationProductFormValues) => {
    createProduct.mutate(
      {
        name: values.name,
        target_url: values.target_url,
        store_id: values.store_id === "" ? null : Number(values.store_id),
        tag_ids: values.tag_ids,
      },
      {
        onSuccess: () => {
          toast.success("Product created with relations.");
          form.reset();
          onSuccess();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  const selectedTagIds = form.watch("tag_ids");
  const isBusy = createProduct.isPending || storesLoading || tagsLoading;

  return (
    <form className="space-y-4" onSubmit={form.handleSubmit(submit)}>
      <Field label="Name" error={form.formState.errors.name?.message}>
        <Input placeholder="Wireless mechanical keyboard" disabled={isBusy} {...form.register("name")} />
      </Field>
      <Field label="Product URL" error={form.formState.errors.target_url?.message}>
        <Input placeholder="https://example.com/product" disabled={isBusy} {...form.register("target_url")} />
      </Field>
      <Field label="Store" hint="Optional. You can associate it later in the backend.">
        <select
          className="h-9 w-full rounded-lg border border-zinc-200 bg-transparent px-3 text-sm outline-none focus-visible:border-zinc-400 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-800 dark:focus-visible:border-zinc-600"
          disabled={isBusy}
          {...form.register("store_id")}
        >
          <option value="">No store</option>
          {stores.map((store) => (
            <option key={store.id} value={store.id}>
              {store.name} · {store.domain}
            </option>
          ))}
        </select>
      </Field>
      <Field label="Tags" hint="Select any number of existing tags.">
        <div className="max-h-32 space-y-1 overflow-y-auto rounded-lg border border-zinc-200 p-2 dark:border-zinc-800">
          {tags.length === 0 ? (
            <p className="px-1 py-2 text-sm text-zinc-500">No tags yet.</p>
          ) : (
            tags.map((tag) => {
              const checked = selectedTagIds.includes(tag.id);
              return (
                <label
                  key={tag.id}
                  className="flex cursor-pointer items-center justify-between rounded-md px-2 py-1.5 text-sm hover:bg-zinc-100 dark:hover:bg-zinc-900"
                >
                  <span>{tag.name}</span>
                  <input
                    checked={checked}
                    className="size-4 accent-zinc-950 dark:accent-zinc-50"
                    disabled={isBusy}
                    type="checkbox"
                    onChange={() => toggleTag(tag.id)}
                  />
                  <span className="sr-only">Select {tag.name}</span>
                </label>
              );
            })
          )}
        </div>
      </Field>
      <Button className="w-full" disabled={isBusy} type="submit">
        {createProduct.isPending ? <Spinner /> : <Check className="size-4" />}
        Create with relations
      </Button>
    </form>
  );
}

function Field({
  label,
  error,
  hint,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block space-y-1.5">
      <span className="text-sm font-medium">{label}</span>
      {children}
      {error ? <span className="block text-xs text-red-600 dark:text-red-400">{error}</span> : null}
      {!error && hint ? <span className="block text-xs text-zinc-500 dark:text-zinc-400">{hint}</span> : null}
    </label>
  );
}
