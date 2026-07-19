import { ArrowRight, Package, Store, Tag, Workflow } from "lucide-react";
import { Link } from "react-router-dom";

import { DataTable, type DataTableColumn } from "@/components/common/data-table";
import { EmptyState } from "@/components/common/empty-state";
import { ErrorState } from "@/components/common/error-state";
import { PageHeader } from "@/components/common/page-header";
import { StatCard } from "@/components/common/stat-card";
import { TaskStatusBadge } from "@/components/common/task-status-badge";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button-variants";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useProducts } from "@/features/products/hooks/use-products";
import { useStores } from "@/features/stores/hooks/use-stores";
import { useTags } from "@/features/tags/hooks/use-tags";
import { useTrackedTasks } from "@/features/tasks/hooks/use-tasks";
import { formatDate, getDomain } from "@/lib/utils";
import type { Product } from "@/types/product";

const recentProductColumns: DataTableColumn<Product>[] = [
  {
    id: "name",
    header: "Product",
    cell: (product) => (
      <div>
        <p className="font-medium">{product.name}</p>
        <p className="text-xs text-zinc-500 dark:text-zinc-400">{getDomain(product.target_url)}</p>
      </div>
    ),
  },
  {
    id: "store",
    header: "Store",
    cell: (product) => product.store?.name ?? <span className="text-zinc-400">—</span>,
  },
  {
    id: "history",
    header: "",
    className: "text-right",
    cell: (product) => (
      <Link className="text-xs font-medium text-zinc-600 hover:text-zinc-950 dark:text-zinc-400 dark:hover:text-zinc-50" to={`/products/${product.id}/history`}>
        History
      </Link>
    ),
  },
];

export function DashboardPage() {
  const products = useProducts({ page: 1, size: 5 });
  const stores = useStores();
  const tags = useTags();
  const { trackedTasks } = useTrackedTasks();

  const hasDashboardError = products.isError || stores.isError || tags.isError;

  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description="A concise view of the monitored catalog and collection activity."
        actions={
          <Link className={buttonVariants()} to="/products">Open products <ArrowRight className="size-4" /></Link>
        }
      />

      <section className="grid gap-4 md:grid-cols-3">
        <StatCard icon={Package} isLoading={products.isLoading} label="Products" value={products.data?.total_items ?? 0} />
        <StatCard icon={Store} isLoading={stores.isLoading} label="Stores" value={stores.data?.length ?? 0} />
        <StatCard icon={Tag} isLoading={tags.isLoading} label="Tags" value={tags.data?.length ?? 0} />
      </section>

      {hasDashboardError ? (
        <ErrorState error={products.error ?? stores.error ?? tags.error} onRetry={() => void Promise.all([products.refetch(), stores.refetch(), tags.refetch()])} />
      ) : (
        <section className="grid gap-6 xl:grid-cols-[1.5fr_1fr]">
          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>Latest products</CardTitle>
              <Link className="text-sm text-zinc-500 hover:text-zinc-950 dark:text-zinc-400 dark:hover:text-zinc-50" to="/products">
                View all
              </Link>
            </CardHeader>
            <CardContent>
              {products.isLoading ? (
                <div className="h-48 animate-pulse rounded-lg bg-zinc-100 dark:bg-zinc-900" />
              ) : (
                <DataTable
                  columns={recentProductColumns}
                  data={products.data?.items ?? []}
                  emptyDescription="Add a product to begin monitoring prices."
                  emptyTitle="No products yet"
                  getRowKey={(product) => product.id}
                />
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex-row items-center justify-between">
              <CardTitle>Recent tasks</CardTitle>
              <Link className="text-sm text-zinc-500 hover:text-zinc-950 dark:text-zinc-400 dark:hover:text-zinc-50" to="/tasks">
                Monitor
              </Link>
            </CardHeader>
            <CardContent>
              {trackedTasks.length === 0 ? (
                <EmptyState description="Run a collection task to track its state here." icon={Workflow} title="No tasks started" />
              ) : (
                <div className="space-y-3">
                  {trackedTasks.slice(0, 4).map((task) => (
                    <div key={task.task_id} className="flex items-center justify-between gap-3 rounded-lg border border-zinc-200 p-3 dark:border-zinc-800">
                      <div className="min-w-0">
                        <p className="truncate font-mono text-xs">{task.task_id}</p>
                        <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">{formatDate(task.startedAt)}</p>
                      </div>
                      <TaskStatusBadge status={task.status} />
                    </div>
                  ))}
                </div>
              )}
              <div className="mt-4 rounded-lg bg-zinc-50 p-3 text-xs text-zinc-500 dark:bg-zinc-900 dark:text-zinc-400">
                <Badge className="mr-2 align-middle" variant="outline">Local</Badge>
                The backend has no task-list endpoint; this panel shows tasks started from this browser.
              </div>
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  );
}
