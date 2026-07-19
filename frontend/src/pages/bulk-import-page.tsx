import { zodResolver } from "@hookform/resolvers/zod";
import { ArrowLeft, FileUp, Link2 } from "lucide-react";
import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

import { PageHeader } from "@/components/common/page-header";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { Textarea } from "@/components/ui/textarea";
import { useBulkCreateProducts } from "@/features/products/hooks/use-products";
import { getErrorMessage } from "@/services/api-error";

const bulkImportSchema = z.object({
  urls: z.string().trim().min(1, "Add at least one URL."),
});

type BulkImportValues = z.infer<typeof bulkImportSchema>;

function splitUrls(value: string): string[] {
  return value.split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
}

export function BulkImportPage() {
  const importProducts = useBulkCreateProducts();
  const form = useForm<BulkImportValues>({
    resolver: zodResolver(bulkImportSchema),
    defaultValues: { urls: "" },
  });
  const input = form.watch("urls");
  const parsedUrls = useMemo(() => splitUrls(input), [input]);

  const submit = (values: BulkImportValues) => {
    const targetUrls = splitUrls(values.urls);
    const invalidUrl = targetUrls.find((url) => {
      try { new URL(url); return false; } catch { return true; }
    });

    if (invalidUrl) {
      form.setError("urls", { message: `Invalid URL: ${invalidUrl}` });
      return;
    }

    importProducts.mutate(
      { target_urls: targetUrls },
      {
        onSuccess: ({ added_count }) => {
          toast.success(`${added_count} product${added_count === 1 ? "" : "s"} added.`);
          form.reset();
        },
        onError: (error) => toast.error(getErrorMessage(error)),
      },
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Bulk import"
        description="Paste one product URL per line. The existing API creates all valid records in a single request."
        actions={<Link className={buttonVariants({ variant: "outline" })} to="/products"><ArrowLeft className="size-4" />Back to products</Link>}
      />
      <Card className="max-w-3xl">
        <CardHeader><CardTitle>Product URLs</CardTitle></CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={form.handleSubmit(submit)}>
            <Textarea className="min-h-72 font-mono text-sm" disabled={importProducts.isPending} placeholder={"https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html\nhttps://example.com/product"} {...form.register("urls")} />
            <div className="flex flex-col gap-3 text-sm text-zinc-500 dark:text-zinc-400 sm:flex-row sm:items-center sm:justify-between">
              <span className="inline-flex items-center gap-1.5"><Link2 className="size-4" />{parsedUrls.length} URL{parsedUrls.length === 1 ? "" : "s"} detected</span>
              {form.formState.errors.urls ? <span className="text-red-600 dark:text-red-400">{form.formState.errors.urls.message}</span> : null}
            </div>
            <Button disabled={importProducts.isPending || parsedUrls.length === 0} type="submit">
              {importProducts.isPending ? <Spinner /> : <FileUp className="size-4" />}
              Import URLs
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
