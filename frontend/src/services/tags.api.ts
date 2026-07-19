import { apiClient } from "@/services/api-client";
import type { Tag, TagCreatePayload, TagUpdatePayload } from "@/types/tag";

export const tagsApi = {
  async getList(): Promise<Tag[]> {
    const { data } = await apiClient.get<Tag[]>("/tags/");
    return data;
  },

  async create(payload: TagCreatePayload): Promise<Tag> {
    const { data } = await apiClient.post<Tag>("/tags/", payload);
    return data;
  },

  async update(id: number, payload: TagUpdatePayload): Promise<Tag> {
    const { data } = await apiClient.put<Tag>(`/tags/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete(`/tags/${id}`);
  },
};
