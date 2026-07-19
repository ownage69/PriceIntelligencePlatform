import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "@/constants/query-keys";
import { productsApi } from "@/services/products.api";
import type {
  ProductBulkCreatePayload,
  ProductCreatePayload,
  ProductUpdatePayload,
  ProductsQuery,
  ProductWithRelationsPayload,
} from "@/types/product";

export function useProducts(params: ProductsQuery) {
  return useQuery({
    queryKey: queryKeys.products(params),
    queryFn: () => productsApi.getList(params),
    placeholderData: (previousData) => previousData,
  });
}

export function usePriceHistory(productId: number) {
  return useQuery({
    queryKey: queryKeys.productPrices(productId),
    queryFn: () => productsApi.getPriceHistory(productId),
    enabled: Number.isInteger(productId) && productId > 0,
  });
}

function useInvalidateProducts() {
  const queryClient = useQueryClient();

  return () => queryClient.invalidateQueries({ queryKey: ["products"] });
}

export function useCreateProduct() {
  const invalidateProducts = useInvalidateProducts();

  return useMutation({
    mutationFn: (payload: ProductCreatePayload) => productsApi.create(payload),
    onSuccess: invalidateProducts,
  });
}

export function useCreateProductWithRelations() {
  const invalidateProducts = useInvalidateProducts();

  return useMutation({
    mutationFn: (payload: ProductWithRelationsPayload) => productsApi.createWithRelations(payload),
    onSuccess: invalidateProducts,
  });
}

export function useBulkCreateProducts() {
  const invalidateProducts = useInvalidateProducts();

  return useMutation({
    mutationFn: (payload: ProductBulkCreatePayload) => productsApi.bulkCreate(payload),
    onSuccess: invalidateProducts,
  });
}

export function useUpdateProduct() {
  const invalidateProducts = useInvalidateProducts();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: ProductUpdatePayload }) =>
      productsApi.update(id, payload),
    onSuccess: invalidateProducts,
  });
}

export function useDeleteProduct() {
  const invalidateProducts = useInvalidateProducts();

  return useMutation({
    mutationFn: productsApi.remove,
    onSuccess: invalidateProducts,
  });
}
