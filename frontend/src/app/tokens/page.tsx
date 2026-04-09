"use client";

import { useState } from "react";
import { useTokenAnalytics } from "@/lib/api";
import { TokenBarChart, TokenPieChart } from "@/components/TokenUsageChart";
import { formatCost } from "@/lib/utils";

const GROUP_OPTIONS = [
  { label: "By Model", value: "model" },
  { label: "By Workflow", value: "workflow" },
  { label: "By Node", value: "node" },
];

export default function TokensPage() {
  const [groupBy, setGroupBy] = useState("model");
  const { data: tokenData } = useTokenAnalytics(groupBy);

  const totalTokens =
    tokenData?.reduce(
      (sum: number, d: any) => sum + (d.total_tokens || 0),
      0
    ) || 0;
  const totalCost =
    tokenData?.reduce(
      (sum: number, d: any) => sum + (d.estimated_cost_usd || 0),
      0
    ) || 0;

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">
        Token Analytics
      </h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Track token consumption and estimated costs across workflows.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="text-sm text-muted-foreground">Total Tokens</p>
          <p className="mt-2 text-3xl font-semibold">
            {totalTokens.toLocaleString()}
          </p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="text-sm text-muted-foreground">Estimated Cost</p>
          <p className="mt-2 text-3xl font-semibold">{formatCost(totalCost)}</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <p className="text-sm text-muted-foreground">Groups</p>
          <p className="mt-2 text-3xl font-semibold">
            {tokenData?.length || 0}
          </p>
        </div>
      </div>

      <div className="mt-6 flex gap-2">
        {GROUP_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setGroupBy(opt.value)}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
              groupBy === opt.value
                ? "bg-accent/15 text-accent"
                : "text-muted-foreground hover:bg-muted hover:text-foreground"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">
            Token Distribution
          </h2>
          <TokenBarChart data={tokenData || []} />
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">
            Usage Share
          </h2>
          <TokenPieChart data={tokenData || []} />
        </div>
      </div>

      <div className="mt-8 overflow-x-auto rounded-xl border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-card">
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">
                Group
              </th>
              <th className="px-4 py-3 text-right font-medium text-muted-foreground">
                Prompt Tokens
              </th>
              <th className="px-4 py-3 text-right font-medium text-muted-foreground">
                Completion Tokens
              </th>
              <th className="px-4 py-3 text-right font-medium text-muted-foreground">
                Total
              </th>
              <th className="px-4 py-3 text-right font-medium text-muted-foreground">
                Est. Cost
              </th>
              <th className="px-4 py-3 text-right font-medium text-muted-foreground">
                Calls
              </th>
            </tr>
          </thead>
          <tbody>
            {(tokenData || []).map((row: any) => (
              <tr key={row.group_key} className="border-b border-border">
                <td className="px-4 py-3 font-medium">{row.group_key}</td>
                <td className="px-4 py-3 text-right font-mono text-muted-foreground">
                  {row.prompt_tokens?.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right font-mono text-muted-foreground">
                  {row.completion_tokens?.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right font-mono">
                  {row.total_tokens?.toLocaleString()}
                </td>
                <td className="px-4 py-3 text-right font-mono text-emerald-400">
                  {formatCost(row.estimated_cost_usd)}
                </td>
                <td className="px-4 py-3 text-right font-mono text-muted-foreground">
                  {row.count}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
