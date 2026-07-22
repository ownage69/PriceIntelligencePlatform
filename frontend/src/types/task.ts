export interface TaskStartResponse {
  task_id: string;
  product_name: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
  message: string | null;
}

export interface TrackedTask extends TaskStatusResponse {
  startedAt: string;
  productName: string;
}
