import { ExternalLink, FilePlus2, History, Plus, Search, SlidersHorizontal } from "lucide-react";
import { useDeferredValue, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { DataTable, type DataTableColumn } from "@/components/common/data-table";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { Pagination } from "@/components/common/pagination";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { buttonVariants } from "@/components/ui/button-variants";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { ProductCreateDialog } from "@/features/products/components/product-create-dialog";
import { useProducts } from "@/features/products/hooks/use-products";
import { getDomain } from "@/lib/utils";
import type { Product } from "@/types/product";

type SortMode = "name-asc" | "name-desc" | "store-asc";

export function ProductsPage() {
  const [page, setPage] = useState(1);
  const [size, setSize] = useState(10);
  const [storeName, setStoreName] = useState("");
  const [tagName, setTagName] = useState("");
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<SortMode>("name-asc");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const deferredStoreName = useDeferredValue(storeName.trim());
  const deferredTagName = useDeferredValue(tagName.trim());
  const deferredSearch = useDeferredValue(search.trim().toLowerCase());

  useEffect(() => {
    setPage(1);
  }, [deferredStoreName, deferredTagName, size]);

  const products = useProducts({
    page,
    size,
    ...(deferredStoreName ? { store_name: deferredStoreName } : {}),
    ...(deferredTagName ? { tag_name: deferredTagName } : {}),
  });

  const visibleProducts = useMemo(() => {
    const filtered = (products.data?.items ?? []).filter((product) =>
      [product.name, product.target_url, product.store?.name ?? "", ...product.tags.map((tag) => tag.name)]
        .join(" ")
        .toLowerCase()
        .includes(deferredSearch),
    );

    return [...filtered].sort((left, right) => {
      if (sort === "store-asc") {
        return (left.store?.name ?? "").localeCompare(right.store?.name ?? "");
      }

      const direction = sort === "name-asc" ? 1 : -1;
      return left.name.localeCompare(right.name) * direction;
    });
  }, [deferredSearch, products.data?.items, sort]);

  const columns: DataTableColumn<Product>[] = [
    {
      id: "name",
      header: "Name",
      cell: (product) => (
        <div>
          <p className="max-w-48 truncate font-medium" title={product.name}>{product.name}</p>
          <Badge className="mt-1" variant={product.is_active ? "success" : "secondary"}>{product.is_active ? "Active" : "Inactive"}</Badge>
        </div>
      ),
    },
    {
      id: "store",
      header: "Store",
      cell: (product) => product.store?.name ?? <span className="text-zinc-400">—</span>,
    },
    {
      id: "url",
      header: "URL",
      cell: (product) => (
        <a className="inline-flex max-w-48 items-center gap-1 truncate text-zinc-500 hover:text-zinc-950 dark:text-zinc-400 dark:hover:text-zinc-50" href={product.target_url} rel="noreferrer" target="_blank">
          <span className="truncate">{getDomain(product.target_url)}</span>
          <ExternalLink className="size-3 shrink-0" />
        </a>
      ),
    },
    {
      id: "tags",
      header: "Tags",
      cell: (product) => (
        <div className="flex max-w-48 flex-wrap gap-1">
          {product.tags.length ? product.tags.map((tag) => <Badge key={tag.id} variant="outline">{tag.name}</Badge>) : <span className="text-zinc-400">—</span>}
        </div>
      ),
    },
    {
      id: "created",
      header: "Created at",
      cell: () => <span className="text-zinc-400" title="The current API does not expose a product creation timestamp.">—</span>,
    },
    {
      id: "actions",
      header: "Actions",
      className: "text-right",
      cell: (product) => (
        <Link className="inline-flex items-center gap-1 text-xs font-medium text-zinc-600 hover:text-zinc-950 dark:text-zinc-400 dark:hover:text-zinc-50" to={`/products/${product.id}/history`}>
          <History className="size-3.5" />
          History
        </Link>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Products"
        description="Monitor product URLs, associations and price history."
        actions={
          <>
            <Link className={buttonVariants({ variant: "outline" })} to="/products/import"><FilePlus2 className="size-4" />Bulk import</Link>
            <Button onClick={() => setCreateDialogOpen(true)}><Plus className="size-4" />Add product</Button>
          </>
        }
      />

      <section className="grid gap-3 rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950 md:grid-cols-2 xl:grid-cols-[1.4fr_1fr_1fr_0.8fr]">
        <label className="relative block">
          <Search className="pointer-events-none absolute left-3 top-2.5 size-4 text-zinc-400" />
          <Input className="pl-9" placeholder="Search current page…" value={search} onChange={(event) => setSearch(event.target.value)} />
        </label>
        <Input placeholder="Filter by store name" value={storeName} onChange={(event) => setStoreName(event.target.value)} />
        <Input placeholder="Filter by tag name" value={tagName} onChange={(event) => setTagName(event.target.value)} />
        <label className="relative">
          <SlidersHorizontal className="pointer-events-none absolute left-3 top-2.5 size-4 text-zinc-400" />
          <select className="h-9 w-full appearance-none rounded-lg border border-zinc-200 bg-transparent pl-9 pr-3 text-sm outline-none focus-visible:border-zinc-400 dark:border-zinc-800 dark:focus-visible:border-zinc-600" value={sort} onChange={(event) => setSort(event.target.value as SortMode)}>
            <option value="name-asc">Name: A–Z</option>
            <option value="name-desc">Name: Z–A</option>
            <option value="store-asc">Store: A–Z</option>
          </select>
        </label>
      </section>

      {products.isLoading ? (
        <div className="space-y-2"><Skeleton className="h-12 w-full" /><Skeleton className="h-56 w-full" /></div>
      ) : products.isError ? (
        <ErrorState error={products.error} onRetry={() => void products.refetch()} />
      ) : (
        <>
          <DataTable
            columns={columns}
            data={visibleProducts}
            emptyDescription={deferredSearch ? "No product on this page matches the local search." : "Add a URL to start monitoring prices."}
            emptyTitle={deferredSearch ? "No matching products" : "No products yet"}
            getRowKey={(product) => product.id}
          />
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-xs text-zinc-500 dark:text-zinc-400">Text search and sorting apply to the loaded page; store and tag filters are sent to the API.</p>
            <label className="flex items-center gap-2 text-sm text-zinc-500 dark:text-zinc-400">
              Per page
              <select className="rounded-md border border-zinc-200 bg-transparent px-2 py-1 text-sm dark:border-zinc-800" value={size} onChange={(event) => setSize(Number(event.target.value))}>
                {[10, 25, 50].map((option) => <option key={option} value={option}>{option}</option>)}
              </select>
            </label>
          </div>
          <Pagination page={page} size={size} totalItems={products.data?.total_items ?? 0} totalPages={products.data?.total_pages ?? 0} onPageChange={setPage} />
        </>
      )}
      <ProductCreateDialog open={createDialogOpen} onOpenChange={setCreateDialogOpen} />
    </div>
  );
}
