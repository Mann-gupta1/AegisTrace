"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface ConfidenceBucket {
  bucket: string;
  count: number;
}

const BUCKET_COLORS: Record<string, string> = {
  "0.0-0.2": "#ef4444",
  "0.2-0.4": "#f97316",
  "0.4-0.6": "#f59e0b",
  "0.6-0.8": "#84cc16",
  "0.8-1.0": "#10b981",
};

export default function ConfidenceDistribution({
  data,
}: {
  data: ConfidenceBucket[];
}) {
  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis dataKey="bucket" stroke="#71717a" fontSize={12} />
          <YAxis stroke="#71717a" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#18181b",
              border: "1px solid #27272a",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {data.map((entry) => (
              <Cell
                key={entry.bucket}
                fill={BUCKET_COLORS[entry.bucket] || "#6366f1"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
