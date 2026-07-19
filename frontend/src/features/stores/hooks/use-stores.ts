import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/constants/query-keys";
import { storesApi } from "@/services/stores.api";
import type { StoreCreatePayload, StoreUpdatePayload } from "@/types/store";

export function useStores() {
  return useQuery({
    queryKey: queryKeys.stores,
    queryFn: storesApi.getList,
  });
}

function useInvalidateStores() {
  const queryClient = useQueryClient();

  return () =>
    Promise.all([
      queryClient.invalidateQueries({ queryKey: queryKeys.stores }),
      queryClient.invalidateQueries({ queryKey: ["products"] }),
    ]);
}

export function useCreateStore() {
  const invalidateStores = useInvalidateStores();

  return useMutation({
    mutationFn: (payload: StoreCreatePayload) => storesApi.create(payload),
    onSuccess: invalidateStores,
  });
}

export function useUpdateStore() {
  const invalidateStores = useInvalidateStores();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: StoreUpdatePayload }) =>
      storesApi.update(id, payload),
    onSuccess: invalidateStores,
  });
}

export function useDeleteStore() {
  const invalidateStores = useInvalidateStores();

  return useMutation({
    mutationFn: storesApi.remove,
    onSuccess: invalidateStores,
  });
}
