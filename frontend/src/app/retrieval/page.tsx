"use client";

import { useRetrievalOverview, useRetrievalEvents } from "@/lib/api";
import RetrievalHeatmap from "@/components/RetrievalHeatmap";
import { formatConfidence } from "@/lib/utils";

export default function RetrievalPage() {
  const { data: overview } = useRetrievalOverview();
  const { data: events } = useRetrievalEvents();

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">
        Retrieval Quality
      </h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Monitor context retrieval coverage and hallucination risk.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="text-sm text-muted-foreground">Avg Coverage</p>
          <p className="mt-2 text-3xl font-semibold text-emerald-400">
            {formatConfidence(overview?.avg_coverage)}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="text-sm text-muted-foreground">Avg Risk</p>
          <p className="mt-2 text-3xl font-semibold text-amber-400">
            {formatConfidence(overview?.avg_risk)}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="text-sm text-muted-foreground">Total Retrievals</p>
          <p className="mt-2 text-3xl font-semibold">
            {overview?.total_retrievals || 0}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="text-sm text-muted-foreground">
            Low Coverage (&lt;50%)
          </p>
          <p className="mt-2 text-3xl font-semibold text-red-400">
            {overview?.low_coverage_count || 0}
          </p>
        </div>
      </div>

      <div className="mt-8 rounded-xl border border-border bg-card p-6">
        <h2 className="mb-4 text-sm font-medium text-muted-foreground">
          Coverage vs Risk Score
        </h2>
        <RetrievalHeatmap events={events || []} />
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold">Recent Retrieval Events</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Sorted by coverage score (lowest first).
        </p>
        <div className="mt-4 space-y-3">
          {(events || []).slice(0, 20).map((evt: any) => (
            <div
              key={evt.id}
              className="flex items-center justify-between rounded-xl border border-border bg-card p-4"
            >
              <p className="max-w-lg truncate text-sm">{evt.query_text}</p>
              <div className="flex gap-4 text-xs">
                <span className="text-emerald-400">
                  Coverage: {((evt.coverage_score || 0) * 100).toFixed(1)}%
                </span>
                <span className="text-amber-400">
                  Risk: {((evt.risk_score || 0) * 100).toFixed(1)}%
                </span>
                <span className="text-muted-foreground">
                  {evt.num_docs_retrieved} docs
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
