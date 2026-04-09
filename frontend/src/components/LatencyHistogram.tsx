"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

interface LatencyData {
  date: string;
  p50: number;
  p95: number;
  p99: number;
}

export default function LatencyHistogram({ data }: { data: LatencyData[] }) {
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
          <XAxis dataKey="date" stroke="#71717a" fontSize={12} />
          <YAxis stroke="#71717a" fontSize={12} unit="ms" />
          <Tooltip
            contentStyle={{
              backgroundColor: "#18181b",
              border: "1px solid #27272a",
              borderRadius: "8px",
              fontSize: "12px",
            }}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="p50"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="P50"
          />
          <Line
            type="monotone"
            dataKey="p95"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="P95"
          />
          <Line
            type="monotone"
            dataKey="p99"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ r: 3 }}
            name="P99"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
