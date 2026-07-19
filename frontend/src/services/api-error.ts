import { AxiosError } from "axios";

import type { ErrorPayload } from "@/types/api";

export class ApiError extends Error {
  readonly status: number;
  readonly type: string;
  readonly details: unknown | null;

  constructor({
    message,
    status,
    type,
    details = null,
  }: {
    message: string;
    status: number;
    type: string;
    details?: unknown | null;
  }) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.type = type;
    this.details = details;
  }
}

function getDetailMessage(detail: unknown): string | null {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return "Request validation failed.";
  }

  return null;
}

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) {
    return error;
  }

  if (error instanceof AxiosError) {
    const status = error.response?.status ?? 0;
    const payload = error.response?.data as ErrorPayload | undefined;
    const message =
      payload?.error?.message ?? getDetailMessage(payload?.detail) ?? error.message ?? "Request failed.";

    return new ApiError({
      message,
      status,
      type: payload?.error?.type ?? "RequestError",
      details: payload?.error?.details ?? payload?.detail ?? null,
    });
  }

  return new ApiError({
    message: "An unexpected error occurred.",
    status: 0,
    type: "UnknownError",
  });
}

export function getErrorMessage(error: unknown): string {
  return toApiError(error).message;
}
