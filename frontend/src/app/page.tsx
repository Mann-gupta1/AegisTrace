"use client";

import { useRunsSummary, useLatencyAnalytics, useTokenAnalytics } from "@/lib/api";
import { formatLatency, formatTokens, formatConfidence } from "@/lib/utils";
import { Activity, Clock, Zap, TrendingUp, Radio } from "lucide-react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";

function StatCard({
  label,
  value,
  icon: Icon,
  accent,
}: {
  label: string;
  value: string;
  icon: React.ElementType;
  accent?: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{label}</p>
        <Icon className={`h-5 w-5 ${accent || "text-muted-foreground"}`} />
      </div>
      <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const { data: summary } = useRunsSummary();
  const { data: latency } = useLatencyAnalytics();
  const { data: tokens } = useTokenAnalytics("model");

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Real-time overview of your agent pipeline telemetry.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard
          label="Total Runs"
          value={summary?.total_runs?.toString() || "0"}
          icon={Activity}
          accent="text-accent"
        />
        <StatCard
          label="Active Runs"
          value={summary?.active_runs?.toString() || "0"}
          icon={Radio}
          accent="text-blue-400"
        />
        <StatCard
          label="Avg Latency"
          value={formatLatency(summary?.avg_latency_ms)}
          icon={Clock}
          accent="text-amber-400"
        />
        <StatCard
          label="Avg Confidence"
          value={formatConfidence(summary?.avg_confidence)}
          icon={TrendingUp}
          accent="text-emerald-400"
        />
        <StatCard
          label="Total Tokens"
          value={formatTokens(summary?.total_tokens)}
          icon={Zap}
          accent="text-purple-400"
        />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">
            Latency Trend (p50 / p95 / p99)
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={latency || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="date" stroke="#71717a" fontSize={12} />
                <YAxis stroke="#71717a" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#18181b",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="p50"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="p95"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={false}
                />
                <Line
                  type="monotone"
                  dataKey="p99"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="mb-4 text-sm font-medium text-muted-foreground">
            Token Usage by Model
          </h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tokens || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                <XAxis dataKey="group_key" stroke="#71717a" fontSize={11} />
                <YAxis stroke="#71717a" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#18181b",
                    border: "1px solid #27272a",
                    borderRadius: "8px",
                    fontSize: "12px",
                  }}
                />
                <Bar dataKey="prompt_tokens" fill="#6366f1" stackId="a" />
                <Bar dataKey="completion_tokens" fill="#8b5cf6" stackId="a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
