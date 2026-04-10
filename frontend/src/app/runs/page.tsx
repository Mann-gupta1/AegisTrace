"use client";

import { useState } from "react";
import { useRuns } from "@/lib/api";
import RunsTable from "@/components/RunsTable";

const FILTERS = [
  { label: "All", value: "" },
  { label: "Running", value: "running" },
  { label: "Completed", value: "completed" },
  { label: "Failed", value: "failed" },
];

export default function RunsPage() {
  const [status, setStatus] = useState("");
  const { data: runs, error, isLoading } = useRuns(status || undefined);

  return (
    <div>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            Workflow Runs
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Browse and inspect agent workflow executions.
          </p>
        </div>
      </div>

      <div className="mt-6 flex gap-2">
        {FILTERS.map((f) => (
          <button
            key={f.value}
            onClick={() => setStatus(f.value)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              status === f.value
                ? "bg-accent/15 text-accent"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <div className="mt-6">
        {isLoading ? (
          <div className="flex h-40 items-center justify-center text-muted-foreground">
            Loading runs...
          </div>
        ) : error ? (
          <div className="rounded-xl border border-red-500/30 bg-red-500/10 p-6 text-sm text-red-200">
            <p className="font-medium">Could not load runs from the API.</p>
            <p className="mt-2 text-red-200/80">
              Set{" "}
              <code className="rounded bg-black/30 px-1 py-0.5 font-mono text-xs">
                NEXT_PUBLIC_API_URL
              </code>{" "}
              on Vercel to your Render URL (no trailing slash), and add your Vercel origin to{" "}
              <code className="rounded bg-black/30 px-1 py-0.5 font-mono text-xs">
                ALLOWED_ORIGINS
              </code>{" "}
              on Render.
            </p>
          </div>
        ) : runs?.length ? (
          <RunsTable runs={runs} />
        ) : (
          <div className="flex h-40 items-center justify-center rounded-xl border border-border text-muted-foreground">
            No workflow runs found.
          </div>
        )}
      </div>
    </div>
  );
}
