import { ArrowLeft, ChartNoAxesCombined, TrendingDown, TrendingUp, WalletCards } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { DataTable, type DataTableColumn } from "@/components/common/data-table";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { buttonVariants } from "@/components/ui/button-variants";
import { Skeleton } from "@/components/ui/skeleton";
import { PriceChart } from "@/features/prices/components/price-chart";
import { usePriceHistory } from "@/features/products/hooks/use-products";
import { formatDate, formatPrice } from "@/lib/utils";
import type { PriceHistoryItem } from "@/types/product";

const historyColumns: DataTableColumn<PriceHistoryItem>[] = [
  { id: "price", header: "Price", cell: (item) => <span className="font-medium">{formatPrice(item.price)}</span> },
  { id: "collected", header: "Collected at", cell: (item) => formatDate(item.collected_at) },
];

export function PriceHistoryPage() {
  const productId = Number(useParams().productId);
  const priceHistory = usePriceHistory(productId);
  const history = priceHistory.data ?? [];
  const numericPrices = history.map((item) => Number(item.price)).filter(Number.isFinite);
  const latest = history[0]?.price;

  if (!Number.isInteger(productId) || productId <= 0) {
    return <EmptyState description="Open the history page from an existing product." title="Invalid product ID" />;
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Price history · #${productId}`}
        description="Collected price points, ordered from newest to oldest by the API."
        actions={<Link className={buttonVariants({ variant: "outline" })} to="/products"><ArrowLeft className="size-4" />Back to products</Link>}
      />
      {priceHistory.isLoading ? (
        <div className="space-y-4"><div className="grid gap-4 md:grid-cols-3"><Skeleton className="h-32" /><Skeleton className="h-32" /><Skeleton className="h-32" /></div><Skeleton className="h-80" /></div>
      ) : priceHistory.isError ? (
        <ErrorState error={priceHistory.error} onRetry={() => void priceHistory.refetch()} />
      ) : history.length === 0 ? (
        <EmptyState description="Run a collection task after adding the product, then return here." icon={ChartNoAxesCombined} title="No prices collected yet" />
      ) : (
        <>
          <section className="grid gap-4 md:grid-cols-3">
            <StatCard icon={WalletCards} label="Latest price" value={latest === undefined ? "—" : formatPrice(latest)} />
            <StatCard icon={TrendingDown} label="Minimum price" value={formatPrice(Math.min(...numericPrices))} />
            <StatCard icon={TrendingUp} label="Maximum price" value={formatPrice(Math.max(...numericPrices))} />
          </section>
          <PriceChart history={history} />
          <section className="space-y-3">
            <h2 className="text-lg font-semibold">All collected prices</h2>
            <DataTable columns={historyColumns} data={history} getRowKey={(item) => item.id} />
          </section>
        </>
      )}
    </div>
  );
}
