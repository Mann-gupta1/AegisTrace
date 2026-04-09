"use client";

import { use } from "react";
import Link from "next/link";
import { useRunDetail, useRunTimeline } from "@/lib/api";
import {
  formatLatency,
  formatTokens,
  formatConfidence,
  statusColor,
  cn,
} from "@/lib/utils";
import ExecutionTimeline from "@/components/ExecutionTimeline";
import { ArrowLeft } from "lucide-react";

export default function RunDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { data: detail, isLoading } = useRunDetail(id);
  const { data: timeline } = useRunTimeline(id);

  if (isLoading) {
    return (
      <div className="flex h-40 items-center justify-center text-muted-foreground">
        Loading run details...
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="flex h-40 items-center justify-center text-muted-foreground">
        Run not found.
      </div>
    );
  }

  const { workflow, nodes, llm_calls, retrieval_events, tool_calls } = detail;

  return (
    <div>
      <Link
        href="/runs"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Runs
      </Link>

      <div className="mt-4 flex items-center gap-4">
        <h1 className="text-2xl font-semibold tracking-tight">
          {workflow.workflow_id}
        </h1>
        <span
          className={cn(
            "inline-flex rounded-full border px-2.5 py-0.5 text-xs font-medium",
            statusColor(workflow.status)
          )}
        >
          {workflow.status}
        </span>
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Total Latency</p>
          <p className="mt-1 text-xl font-semibold">
            {formatLatency(workflow.total_latency_ms)}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Total Tokens</p>
          <p className="mt-1 text-xl font-semibold">
            {formatTokens(workflow.total_tokens)}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Avg Confidence</p>
          <p className="mt-1 text-xl font-semibold">
            {formatConfidence(workflow.avg_confidence)}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-4">
          <p className="text-xs text-muted-foreground">Nodes</p>
          <p className="mt-1 text-xl font-semibold">{nodes.length}</p>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-lg font-semibold">Execution Timeline</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Waterfall view of node execution sequence.
        </p>
        <div className="mt-4 rounded-xl border border-border bg-card p-6">
          <ExecutionTimeline entries={timeline || []} />
        </div>
      </div>

      {llm_calls.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold">LLM Calls</h2>
          <div className="mt-4 space-y-4">
            {llm_calls.map((call: any) => (
              <div
                key={call.id}
                className="rounded-xl border border-border bg-card p-4"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    {call.model_name}
                    <span className="ml-2 text-xs text-muted-foreground">
                      ({call.provider})
                    </span>
                  </span>
                  <div className="flex gap-4 text-xs text-muted-foreground">
                    <span>{formatLatency(call.latency_ms)}</span>
                    <span>{call.total_tokens} tokens</span>
                    <span>
                      Confidence: {formatConfidence(call.confidence_score)}
                    </span>
                  </div>
                </div>
                {call.prompt_text && (
                  <div className="mt-3">
                    <p className="text-xs font-medium text-muted-foreground">
                      Prompt
                    </p>
                    <pre className="mt-1 max-h-32 overflow-auto rounded-lg bg-muted/30 p-3 text-xs">
                      {call.prompt_text}
                    </pre>
                  </div>
                )}
                {call.response_text && (
                  <div className="mt-3">
                    <p className="text-xs font-medium text-muted-foreground">
                      Response
                    </p>
                    <pre className="mt-1 max-h-32 overflow-auto rounded-lg bg-muted/30 p-3 text-xs">
                      {call.response_text}
                    </pre>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {retrieval_events.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold">Retrieval Events</h2>
          <div className="mt-4 space-y-4">
            {retrieval_events.map((evt: any) => (
              <div
                key={evt.id}
                className="rounded-xl border border-border bg-card p-4"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium truncate max-w-md">
                    {evt.query_text}
                  </span>
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
              </div>
            ))}
          </div>
        </div>
      )}

      {tool_calls.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold">Tool Calls</h2>
          <div className="mt-4 space-y-4">
            {tool_calls.map((tc: any) => (
              <div
                key={tc.id}
                className="rounded-xl border border-border bg-card p-4"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">{tc.tool_name}</span>
                  <div className="flex items-center gap-3 text-xs">
                    <span className="text-muted-foreground">
                      {formatLatency(tc.latency_ms)}
                    </span>
                    <span
                      className={
                        tc.success ? "text-emerald-400" : "text-red-400"
                      }
                    >
                      {tc.success ? "Success" : "Failed"}
                    </span>
                  </div>
                </div>
                {tc.error_message && (
                  <p className="mt-2 text-xs text-red-400">
                    {tc.error_message}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
