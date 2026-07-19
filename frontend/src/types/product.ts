import type { Store } from "@/types/store";
import type { Tag } from "@/types/tag";

export interface Product {
  id: number;
  name: string;
  target_url: string;
  is_active: boolean;
  created_at: string;
  scrape_interval_minutes: number;
  store: Store | null;
  tags: Tag[];
}

export interface PriceHistoryItem {
  id: number;
  product_id: number;
  price: string | number;
  collected_at: string;
}

export interface ProductCreatePayload {
  name: string;
  target_url: string;
  scrape_interval_minutes: number;
}

export interface ProductWithRelationsPayload extends ProductCreatePayload {
  store_id: number | null;
  tag_ids: number[];
}

export interface ProductUpdatePayload {
  name?: string;
  target_url?: string;
  is_active?: boolean;
  scrape_interval_minutes?: number;
  store_id?: number | null;
  tag_ids?: number[];
}

export interface ProductBulkCreatePayload {
  target_urls: string[];
}

export interface BulkCreateResponse {
  added_count: number;
}

export interface ProductsQuery {
  page?: number;
  size?: number;
  store_name?: string;
  tag_name?: string;
}
