import { apiClient } from "@/services/api-client";
import type {
  BulkCreateResponse,
  PriceHistoryItem,
  Product,
  ProductBulkCreatePayload,
  ProductCreatePayload,
  ProductUpdatePayload,
  ProductsQuery,
  ProductWithRelationsPayload,
} from "@/types/product";
import type { PaginatedResponse } from "@/types/api";

export const productsApi = {
  async getList(params: ProductsQuery): Promise<PaginatedResponse<Product>> {
    const { data } = await apiClient.get<PaginatedResponse<Product>>("/products/", { params });
    return data;
  },

  async create(payload: ProductCreatePayload): Promise<Product> {
    const { data } = await apiClient.post<Product>("/products/", payload);
    return data;
  },

  async createWithRelations(payload: ProductWithRelationsPayload): Promise<Product> {
    const { data } = await apiClient.post<Product>("/products/with-relations", payload);
    return data;
  },

  async bulkCreate(payload: ProductBulkCreatePayload): Promise<BulkCreateResponse> {
    const { data } = await apiClient.post<BulkCreateResponse>("/products/bulk", payload);
    return data;
  },

  async update(id: number, payload: ProductUpdatePayload): Promise<Product> {
    const { data } = await apiClient.put<Product>(`/products/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete(`/products/${id}`);
  },

  async getPriceHistory(productId: number): Promise<PriceHistoryItem[]> {
    const { data } = await apiClient.get<PriceHistoryItem[]>(`/products/${productId}/prices`);
    return data;
  },
};
