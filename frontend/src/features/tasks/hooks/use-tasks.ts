import { useMutation, useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";

import { queryKeys } from "@/constants/query-keys";
import { tasksApi } from "@/services/tasks.api";
import type { TrackedTask } from "@/types/task";

const TASKS_STORAGE_KEY = "price-intelligence.tracked-tasks";
const TERMINAL_STATUSES = new Set(["SUCCESS", "FAILURE", "REVOKED", "IGNORED"]);

function readTrackedTasks(): TrackedTask[] {
  try {
    const stored = window.localStorage.getItem(TASKS_STORAGE_KEY);
    return stored ? (JSON.parse(stored) as TrackedTask[]) : [];
  } catch {
    return [];
  }
}

function saveTrackedTasks(tasks: TrackedTask[]): void {
  window.localStorage.setItem(TASKS_STORAGE_KEY, JSON.stringify(tasks.slice(0, 15)));
}

export function isTaskFinished(status: string): boolean {
  return TERMINAL_STATUSES.has(status);
}

export function useTrackedTasks() {
  const [trackedTasks, setTrackedTasks] = useState<TrackedTask[]>(readTrackedTasks);

  useEffect(() => {
    saveTrackedTasks(trackedTasks);
  }, [trackedTasks]);

  const addTask = useCallback((taskId: string, productName: string) => {
    setTrackedTasks((current) => [
      { task_id: taskId, status: "PENDING", startedAt: new Date().toISOString(), productName, message: null },
      ...current.filter((task) => task.task_id !== taskId),
    ]);
  }, []);

  const updateTask = useCallback((nextTask: TrackedTask) => {
    setTrackedTasks((current) => {
      const currentTask = current.find((task) => task.task_id === nextTask.task_id);
      if (currentTask?.status === nextTask.status && currentTask?.message === nextTask.message) {
        return current;
      }
      return current.map((task) => (task.task_id === nextTask.task_id ? nextTask : task));
    });
  }, []);

  const clearHistory = useCallback(() => {
    setTrackedTasks([]);
  }, []);

  return { trackedTasks, addTask, updateTask, clearHistory };
}

export function useStartCollection() {
  return useMutation({ mutationFn: (productId: number) => tasksApi.collect(productId) });
}

export function useRevokeTask() {
  return useMutation({ mutationFn: tasksApi.revoke });
}

export function useTaskStatus(taskId: string | null) {
  return useQuery({
    queryKey: queryKeys.task(taskId ?? "unknown"),
    queryFn: () => tasksApi.getStatus(taskId ?? ""),
    enabled: Boolean(taskId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status && isTaskFinished(status) ? false : 1_500;
    },
  });
}
