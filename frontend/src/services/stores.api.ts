import { apiClient } from "@/services/api-client";
import type { Store, StoreCreatePayload, StoreUpdatePayload } from "@/types/store";

export const storesApi = {
  async getList(): Promise<Store[]> {
    const { data } = await apiClient.get<Store[]>("/stores/");
    return data;
  },

  async create(payload: StoreCreatePayload): Promise<Store> {
    const { data } = await apiClient.post<Store>("/stores/", payload);
    return data;
  },

  async update(id: number, payload: StoreUpdatePayload): Promise<Store> {
    const { data } = await apiClient.put<Store>(`/stores/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete(`/stores/${id}`);
  },
};
