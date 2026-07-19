export interface PaginatedResponse<T> {
  total_items: number;
  page: number;
  size: number;
  total_pages: number;
  items: T[];
}

export interface ErrorPayload {
  success?: false;
  error?: {
    type: string;
    message: string;
    details: unknown | null;
  };
  detail?: unknown;
}
