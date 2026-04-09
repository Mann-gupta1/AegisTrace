"use client";

import { formatLatency, nodeTypeColor, cn, statusColor } from "@/lib/utils";

interface TimelineEntry {
  node_id: string;
  node_type: string;
  start_time: string;
  end_time: string | null;
  latency_ms: number | null;
  status: string;
  order_index: number;
}

export default function ExecutionTimeline({
  entries,
}: {
  entries: TimelineEntry[];
}) {
  if (!entries.length) return null;

  const sorted = [...entries].sort((a, b) => a.order_index - b.order_index);
  const maxLatency = Math.max(...sorted.map((e) => e.latency_ms || 0), 1);

  return (
    <div className="space-y-3">
      {sorted.map((entry, i) => {
        const widthPct = ((entry.latency_ms || 0) / maxLatency) * 100;
        const color = nodeTypeColor(entry.node_type);

        return (
          <div key={entry.node_id + i} className="flex items-center gap-4">
            <div className="w-40 shrink-0">
              <p className="text-sm font-medium truncate">{entry.node_id}</p>
              <p className="text-xs text-muted-foreground">{entry.node_type}</p>
            </div>

            <div className="flex-1">
              <div className="relative h-8 rounded-md bg-muted/30">
                <div
                  className="absolute inset-y-0 left-0 rounded-md transition-all"
                  style={{
                    width: `${Math.max(widthPct, 2)}%`,
                    backgroundColor: color,
                    opacity: 0.7,
                  }}
                />
                <div className="absolute inset-y-0 flex items-center px-3">
                  <span className="text-xs font-medium text-white drop-shadow">
                    {formatLatency(entry.latency_ms)}
                  </span>
                </div>
              </div>
            </div>

            <div className="w-24 shrink-0 text-right">
              <span
                className={cn(
                  "inline-flex rounded-full border px-2 py-0.5 text-xs font-medium",
                  statusColor(entry.status)
                )}
              >
                {entry.status}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
