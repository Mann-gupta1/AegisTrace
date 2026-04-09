import axios from "axios";
import useSWR from "swr";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_URL });

const fetcher = (url: string) => api.get(url).then((r) => r.data);

export function useRuns(status?: string) {
  const params = status ? `?status=${status}` : "";
  return useSWR(`/runs${params}`, fetcher, { refreshInterval: 2000 });
}

export function useRunsSummary() {
  return useSWR("/runs/summary", fetcher, { refreshInterval: 2000 });
}

export function useRunDetail(id: string) {
  return useSWR(`/runs/${id}`, fetcher, { refreshInterval: 2000 });
}

export function useRunTimeline(id: string) {
  return useSWR(`/runs/${id}/timeline`, fetcher, { refreshInterval: 2000 });
}

export function useTokenAnalytics(groupBy: string = "model") {
  return useSWR(`/analytics/tokens?group_by=${groupBy}`, fetcher, {
    refreshInterval: 5000,
  });
}

export function useLatencyAnalytics() {
  return useSWR("/analytics/latency", fetcher, { refreshInterval: 5000 });
}

export function useConfidenceAnalytics() {
  return useSWR("/analytics/confidence", fetcher, { refreshInterval: 5000 });
}

export function useRetrievalOverview() {
  return useSWR("/retrieval-quality/overview", fetcher, {
    refreshInterval: 5000,
  });
}

export function useRetrievalEvents() {
  return useSWR("/retrieval-quality/events", fetcher, {
    refreshInterval: 5000,
  });
}

export function usePrompts() {
  return useSWR("/prompts", fetcher, { refreshInterval: 5000 });
}

export function usePromptComparison(v1: string, v2: string) {
  const key = v1 && v2 ? `/prompts/compare?v1=${v1}&v2=${v2}` : null;
  return useSWR(key, fetcher);
}
