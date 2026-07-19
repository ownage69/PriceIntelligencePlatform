export interface TaskStartResponse {
  task_id: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
}

export interface TrackedTask extends TaskStatusResponse {
  startedAt: string;
}
