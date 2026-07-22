import { apiClient } from "@/services/api-client";
import type { TaskStartResponse, TaskStatusResponse } from "@/types/task";

export const tasksApi = {
  async collect(productId: number): Promise<TaskStartResponse> {
    const { data } = await apiClient.post<TaskStartResponse>(`/tasks/collect/${productId}`);
    return data;
  },

  async getStatus(taskId: string): Promise<TaskStatusResponse> {
    const { data } = await apiClient.get<TaskStatusResponse>(`/tasks/${taskId}`);
    return data;
  },

  async revoke(taskId: string): Promise<void> {
    await apiClient.delete(`/tasks/${taskId}`);
  }
};
