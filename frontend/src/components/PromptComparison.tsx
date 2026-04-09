"use client";

import { formatLatency, formatConfidence } from "@/lib/utils";

interface ComparisonResult {
  v1_name: string;
  v2_name: string;
  v1_version: number;
  v2_version: number;
  latency_delta_ms: number;
  confidence_delta: number;
  coverage_delta: number;
  token_delta: number;
  v1_avg_latency: number;
  v2_avg_latency: number;
  v1_avg_confidence: number;
  v2_avg_confidence: number;
  v1_avg_coverage: number;
  v2_avg_coverage: number;
  v1_avg_tokens: number;
  v2_avg_tokens: number;
}

function DeltaIndicator({ value, unit, inverse }: { value: number; unit: string; inverse?: boolean }) {
  const improved = inverse ? value < 0 : value > 0;
  const color = improved ? "text-emerald-400" : "text-red-400";
  const sign = value > 0 ? "+" : "";
  return (
    <span className={`text-sm font-medium ${color}`}>
      {sign}
      {unit === "%" ? (value * 100).toFixed(1) + "%" : unit === "ms" ? Math.round(value) + "ms" : Math.round(value)}
    </span>
  );
}

export default function PromptComparison({
  data,
}: {
  data: ComparisonResult | null;
}) {
  if (!data) {
    return (
      <p className="text-sm text-muted-foreground">
        Select two prompt versions to compare.
      </p>
    );
  }

  const metrics = [
    {
      label: "Avg Latency",
      v1: formatLatency(data.v1_avg_latency),
      v2: formatLatency(data.v2_avg_latency),
      delta: data.latency_delta_ms,
      unit: "ms",
      inverse: true,
    },
    {
      label: "Avg Confidence",
      v1: formatConfidence(data.v1_avg_confidence),
      v2: formatConfidence(data.v2_avg_confidence),
      delta: data.confidence_delta,
      unit: "%",
    },
    {
      label: "Avg Coverage",
      v1: formatConfidence(data.v1_avg_coverage),
      v2: formatConfidence(data.v2_avg_coverage),
      delta: data.coverage_delta,
      unit: "%",
    },
    {
      label: "Avg Tokens",
      v1: String(Math.round(data.v1_avg_tokens)),
      v2: String(Math.round(data.v2_avg_tokens)),
      delta: data.token_delta,
      unit: "",
      inverse: true,
    },
  ];

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-card">
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Metric
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              {data.v1_name} v{data.v1_version}
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              {data.v2_name} v{data.v2_version}
            </th>
            <th className="px-4 py-3 text-left font-medium text-muted-foreground">
              Delta
            </th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((m) => (
            <tr key={m.label} className="border-b border-border">
              <td className="px-4 py-3 font-medium">{m.label}</td>
              <td className="px-4 py-3 font-mono text-muted-foreground">
                {m.v1}
              </td>
              <td className="px-4 py-3 font-mono text-muted-foreground">
                {m.v2}
              </td>
              <td className="px-4 py-3">
                <DeltaIndicator
                  value={m.delta}
                  unit={m.unit}
                  inverse={m.inverse}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
