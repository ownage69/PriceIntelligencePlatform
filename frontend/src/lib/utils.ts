import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatDate(value: string): string {
  return new Intl.DateTimeFormat("ru-RU", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatPrice(value: string | number): string {
  const price = Number(value);

  if (Number.isNaN(price)) {
    return String(value);
  }

  return new Intl.NumberFormat("ru-RU", {
    maximumFractionDigits: 2,
  }).format(price);
}

export function getDomain(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
}
