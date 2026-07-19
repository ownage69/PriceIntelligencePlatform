export interface Tag {
  id: number;
  name: string;
}

export interface TagCreatePayload {
  name: string;
}

export type TagUpdatePayload = Partial<TagCreatePayload>;
