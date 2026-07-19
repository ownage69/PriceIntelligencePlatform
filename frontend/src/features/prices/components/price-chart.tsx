import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDate, formatPrice } from "@/lib/utils";
import type { PriceHistoryItem } from "@/types/product";

interface ChartPoint {
  collectedAt: string;
  price: number;
}

export function PriceChart({ history }: { history: PriceHistoryItem[] }) {
  const data: ChartPoint[] = [...history]
    .reverse()
    .map((item) => ({ collectedAt: item.collected_at, price: Number(item.price) }))
    .filter((item) => Number.isFinite(item.price));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Price trend</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="grid h-72 place-items-center text-sm text-zinc-500 dark:text-zinc-400">
            Price history is not available yet.
          </p>
        ) : (
          <div className="h-72">
            <ResponsiveContainer height="100%" width="100%">
              <LineChart data={data} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
                <XAxis
                  dataKey="collectedAt"
                  minTickGap={36}
                  tick={{ fill: "currentColor", fontSize: 11 }}
                  tickFormatter={(value: string) => new Intl.DateTimeFormat("ru-RU", { month: "short", day: "numeric" }).format(new Date(value))}
                />
                <YAxis
                  dataKey="price"
                  tick={{ fill: "currentColor", fontSize: 11 }}
                  tickFormatter={(value: number) => formatPrice(value)}
                  width={58}
                />
                <Tooltip
                  contentStyle={{ borderRadius: "8px", borderColor: "#e4e4e7", fontSize: "12px" }}
                  formatter={(value: number | string) => [formatPrice(value), "Price"]}
                  labelFormatter={(value: string) => formatDate(value)}
                />
                <Line activeDot={{ r: 4 }} dataKey="price" dot={false} stroke="#52525b" strokeWidth={2} type="monotone" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
