"use client";

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface RetrievalEvent {
  id: string;
  coverage_score: number | null;
  risk_score: number | null;
  num_docs_retrieved: number | null;
  query_text: string | null;
}

function riskColor(risk: number): string {
  if (risk < 0.3) return "#10b981";
  if (risk < 0.6) return "#f59e0b";
  return "#ef4444";
}

export default function RetrievalHeatmap({
  events,
}: {
  events: RetrievalEvent[];
}) {
  const data = events
    .filter((e) => e.coverage_score != null && e.risk_score != null)
    .map((e) => ({
      coverage: e.coverage_score!,
      risk: e.risk_score!,
      docs: e.num_docs_retrieved || 0,
      query: e.query_text || "—",
    }));

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis
            dataKey="coverage"
            name="Coverage"
            stroke="#71717a"
            fontSize={12}
            domain={[0, 1]}
            label={{
              value: "Coverage Score",
              position: "insideBottom",
              offset: -5,
              fill: "#71717a",
              fontSize: 11,
            }}
          />
          <YAxis
            dataKey="risk"
            name="Risk"
            stroke="#71717a"
            fontSize={12}
            domain={[0, 1]}
            label={{
              value: "Risk Score",
              angle: -90,
              position: "insideLeft",
              fill: "#71717a",
              fontSize: 11,
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#18181b",
              border: "1px solid #27272a",
              borderRadius: "8px",
              fontSize: "12px",
            }}
            formatter={(value, name) => [
              Number(value).toFixed(3),
              String(name),
            ]}
          />
          <Scatter data={data}>
            {data.map((entry, index) => (
              <Cell key={index} fill={riskColor(entry.risk)} />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
