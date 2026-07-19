import { apiClient } from "@/services/api-client";
import type { TaskStartResponse, TaskStatusResponse } from "@/types/task";

export const tasksApi = {
  async collect(): Promise<TaskStartResponse> {
    const { data } = await apiClient.post<TaskStartResponse>("/tasks/collect");
    return data;
  },

  async getStatus(taskId: string): Promise<TaskStatusResponse> {
    const { data } = await apiClient.get<TaskStatusResponse>(`/tasks/${taskId}`);
    return data;
  },
};
