export interface Store {
  id: number;
  name: string;
  domain: string;
}

export interface StoreCreatePayload {
  name: string;
  domain: string;
}

export type StoreUpdatePayload = Partial<StoreCreatePayload>;
