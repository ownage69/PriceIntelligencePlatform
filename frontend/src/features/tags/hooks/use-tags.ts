import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/constants/query-keys";
import { tagsApi } from "@/services/tags.api";
import type { TagCreatePayload, TagUpdatePayload } from "@/types/tag";

export function useTags() {
  return useQuery({
    queryKey: queryKeys.tags,
    queryFn: tagsApi.getList,
  });
}

function useInvalidateTags() {
  const queryClient = useQueryClient();

  return () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.tags }),
      queryClient.invalidateQueries({ queryKey: ["products"] }),
    ]);
}

export function useCreateTag() {
  const invalidateTags = useInvalidateTags();

  return useMutation({
    mutationFn: (payload: TagCreatePayload) => tagsApi.create(payload),
    onSuccess: invalidateTags,
  });
}

export function useUpdateTag() {
  const invalidateTags = useInvalidateTags();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: TagUpdatePayload }) =>
      tagsApi.update(id, payload),
    onSuccess: invalidateTags,
  });
}

export function useDeleteTag() {
  const invalidateTags = useInvalidateTags();

  return useMutation({
    mutationFn: tagsApi.remove,
    onSuccess: invalidateTags,
  });
}
