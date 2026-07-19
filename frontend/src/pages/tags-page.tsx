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
import { useCreateTag, useDeleteTag, useTags, useUpdateTag } from "@/features/tags/hooks/use-tags";
import { getErrorMessage } from "@/services/api-error";
import type { Tag } from "@/types/tag";

const tagSchema = z.object({ name: z.string().trim().min(1, "Name is required.").max(100, "Maximum 100 characters.") });
type TagFormValues = z.infer<typeof tagSchema>;

export function TagsPage() {
  const tags = useTags();
  const deleteTag = useDeleteTag();
  const [formTag, setFormTag] = useState<Tag | null | undefined>(undefined);
  const [tagToDelete, setTagToDelete] = useState<Tag | null>(null);
  const columns: DataTableColumn<Tag>[] = [
    { id: "name", header: "Name", cell: (tag) => <span className="font-medium">{tag.name}</span> },
    {
      id: "actions", header: "Actions", className: "text-right", cell: (tag) => <div className="flex justify-end gap-1">
        <Button aria-label={`Edit ${tag.name}`} size="icon" variant="ghost" onClick={() => setFormTag(tag)}><Pencil className="size-4" /></Button>
        <Button aria-label={`Delete ${tag.name}`} size="icon" variant="ghost" onClick={() => setTagToDelete(tag)}><Trash2 className="size-4 text-red-600 dark:text-red-400" /></Button>
      </div>,
    },
  ];
  const confirmDelete = () => {
    if (!tagToDelete) return;
    deleteTag.mutate(tagToDelete.id, {
      onSuccess: () => { toast.success("Tag deleted."); setTagToDelete(null); },
      onError: (error) => toast.error(getErrorMessage(error)),
    });
  };
  return (
    <div className="space-y-6">
      <PageHeader title="Tags" description="Use tags to classify products and apply server-side filtering." actions={<Button onClick={() => setFormTag(null)}><Plus className="size-4" />Add tag</Button>} />
      {tags.isLoading ? <Skeleton className="h-64 w-full" /> : tags.isError ? <ErrorState error={tags.error} onRetry={() => void tags.refetch()} /> : <DataTable columns={columns} data={tags.data ?? []} emptyDescription="Create tags to organize products." emptyTitle="No tags yet" getRowKey={(tag) => tag.id} />}
      <TagDialog open={formTag !== undefined} tag={formTag ?? null} onOpenChange={(open) => !open && setFormTag(undefined)} />
      <ConfirmDialog description={`The tag “${tagToDelete?.name ?? ""}” will be permanently deleted.`} isPending={deleteTag.isPending} open={tagToDelete !== null} title="Delete tag?" onConfirm={confirmDelete} onOpenChange={(open) => !open && setTagToDelete(null)} />
    </div>
  );
}

function TagDialog({ open, tag, onOpenChange }: { open: boolean; tag: Tag | null; onOpenChange: (open: boolean) => void }) {
  const createTag = useCreateTag();
  const updateTag = useUpdateTag();
  const form = useForm<TagFormValues>({ resolver: zodResolver(tagSchema), defaultValues: { name: "" } });
  useEffect(() => { form.reset({ name: tag?.name ?? "" }); }, [form, tag, open]);
  const onSuccess = () => { toast.success(tag ? "Tag updated." : "Tag created."); onOpenChange(false); };
  const onError = (error: unknown) => toast.error(getErrorMessage(error));
  const submit = (values: TagFormValues) => {
    if (tag) {
      updateTag.mutate({ id: tag.id, payload: values }, { onSuccess, onError });
      return;
    }

    createTag.mutate(values, { onSuccess, onError });
  };
  const isPending = createTag.isPending || updateTag.isPending;
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent><DialogHeader><DialogTitle>{tag ? "Edit tag" : "Add tag"}</DialogTitle><DialogDescription>Tags stay short and are reusable across products.</DialogDescription></DialogHeader>
        <form className="space-y-4" onSubmit={form.handleSubmit(submit)}>
          <label className="block space-y-1.5"><span className="text-sm font-medium">Name</span><Input disabled={isPending} placeholder="electronics" {...form.register("name")} />{form.formState.errors.name?.message ? <span className="block text-xs text-red-600 dark:text-red-400">{form.formState.errors.name.message}</span> : null}</label>
          <Button className="w-full" disabled={isPending} type="submit">{isPending ? <Spinner /> : null}{tag ? "Save changes" : "Create tag"}</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
