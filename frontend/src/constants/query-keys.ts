import type { ProductsQuery } from "@/types/product";

export const queryKeys = {
  products: (params: ProductsQuery) => ["products", params] as const,
  productPrices: (productId: number) => ["products", productId, "prices"] as const,
  stores: ["stores"] as const,
  tags: ["tags"] as const,
  task: (taskId: string) => ["tasks", taskId] as const,
};
