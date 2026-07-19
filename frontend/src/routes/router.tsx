import { createBrowserRouter } from "react-router-dom";

import { AppShell } from "@/components/layout/app-shell";

export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { index: true, lazy: async () => ({ Component: (await import("@/pages/dashboard-page")).DashboardPage }) },
      { path: "products", lazy: async () => ({ Component: (await import("@/pages/products-page")).ProductsPage }) },
      { path: "products/import", lazy: async () => ({ Component: (await import("@/pages/bulk-import-page")).BulkImportPage }) },
      { path: "products/:productId/history", lazy: async () => ({ Component: (await import("@/pages/price-history-page")).PriceHistoryPage }) },
      { path: "stores", lazy: async () => ({ Component: (await import("@/pages/stores-page")).StoresPage }) },
      { path: "tags", lazy: async () => ({ Component: (await import("@/pages/tags-page")).TagsPage }) },
      { path: "price-history", lazy: async () => ({ Component: (await import("@/pages/price-history-picker-page")).PriceHistoryPickerPage }) },
      { path: "tasks", lazy: async () => ({ Component: (await import("@/pages/task-monitor-page")).TaskMonitorPage }) },
      { path: "*", lazy: async () => ({ Component: (await import("@/pages/not-found-page")).NotFoundPage }) },
    ],
  },
]);
