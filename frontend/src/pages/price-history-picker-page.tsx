import { History } from "lucide-react";
import { Link } from "react-router-dom";

import { DataTable, type DataTableColumn } from "@/components/common/data-table";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { useProducts } from "@/features/products/hooks/use-products";
import type { Product } from "@/types/product";

const columns: DataTableColumn<Product>[] = [
  { id: "name", header: "Product", cell: (product) => <span className="font-medium">{product.name}</span> },
  { id: "store", header: "Store", cell: (product) => product.store?.name ?? <span className="text-zinc-400">—</span> },
  {
    id: "action",
    header: "",
    className: "text-right",
    cell: (product) => <Link className="inline-flex items-center gap-1 text-xs font-medium" to={`/products/${product.id}/history`}><History className="size-3.5" />View history</Link>,
  },
];

export function PriceHistoryPickerPage() {
  const products = useProducts({ page: 1, size: 50 });

  return (
    <div className="space-y-6">
      <PageHeader title="Price history" description="Choose a product to inspect its price changes." />
      {products.isError ? <ErrorState error={products.error} onRetry={() => void products.refetch()} /> : <DataTable columns={columns} data={products.data?.items ?? []} emptyDescription="Add a product first." emptyTitle="No products available" getRowKey={(product) => product.id} />}
    </div>
  );
}
