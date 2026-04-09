"use client";

import Link from "next/link";
import { formatLatency, formatTokens, formatConfidence, statusColor, cn } from "@/lib/utils";

interface WorkflowRun {
  id: string;
  workflow_id: string;
  status: string;
  start_time: string;
  total_latency_ms: number | null;
  total_tokens: number | null;
  avg_confidence: number | null;
}

export default function RunsTable({ runs }: { runs: WorkflowRun[] }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-card">
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Workflow
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Status
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Latency
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Tokens
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Confidence
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Time
            </th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr
              key={run.id}
              className="border-b border-border transition-colors hover:bg-card/50"
            >
              <td className="px-4 py-3">
                <Link
                  href={`/runs/${run.id}`}
                  className="font-medium text-accent hover:underline"
                >
                  {run.workflow_id}
                </Link>
              </td>
              <td className="px-4 py-3">
                <span
                  className={cn(
                    "inline-flex rounded-full border px-2.5 py-0.5 text-xs font-medium",
                    statusColor(run.status)
                  )}
                >
                  {run.status}
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-muted-foreground">
                {formatLatency(run.total_latency_ms)}
              </td>
              <td className="px-4 py-3 font-mono text-muted-foreground">
                {formatTokens(run.total_tokens)}
              </td>
              <td className="px-4 py-3 font-mono text-muted-foreground">
                {formatConfidence(run.avg_confidence)}
              </td>
              <td className="px-4 py-3 text-muted-foreground">
                {new Date(run.start_time).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
