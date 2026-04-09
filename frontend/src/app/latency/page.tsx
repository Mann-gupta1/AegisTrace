"use client";

import { useLatencyAnalytics, useConfidenceAnalytics } from "@/lib/api";
import LatencyHistogram from "@/components/LatencyHistogram";
import ConfidenceDistribution from "@/components/ConfidenceDistribution";

export default function LatencyPage() {
  const { data: latency } = useLatencyAnalytics();
  const { data: confidence } = useConfidenceAnalytics();

  const latest = latency?.[latency.length - 1];

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">
        Latency Dashboard
      </h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Response time percentiles and confidence score distribution.
      </p>

      {latest && (
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-border bg-card p-6">
            <p className="text-sm text-muted-foreground">P50 Latency</p>
            <p className="mt-2 text-3xl font-semibold text-emerald-400">
              {Math.round(latest.p50)}ms
            </p>
          </div>
          <div className="rounded-xl border border-border bg-card p-6">
            <p className="text-sm text-muted-foreground">P95 Latency</p>
            <p className="mt-2 text-3xl font-semibold text-amber-400">
              {Math.round(latest.p95)}ms
            </p>
          </div>
          <div className="rounded-xl border border-border bg-card p-6">
            <p className="text-sm text-muted-foreground">P99 Latency</p>
            <p className="mt-2 text-3xl font-semibold text-red-400">
              {Math.round(latest.p99)}ms
            </p>
          </div>
        </div>
      )}

      <div className="mt-8 rounded-xl border border-border bg-card p-6">
        <h2 className="mb-4 text-sm font-medium text-muted-foreground">
          Latency Percentiles Over Time
        </h2>
        <LatencyHistogram data={latency || []} />
      </div>

      <div className="mt-8 rounded-xl border border-border bg-card p-6">
        <h2 className="mb-4 text-sm font-medium text-muted-foreground">
          Confidence Score Distribution
        </h2>
        <ConfidenceDistribution data={confidence || []} />
      </div>
    </div>
  );
}
