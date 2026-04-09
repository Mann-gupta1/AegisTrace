import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatLatency(ms: number | null | undefined): string {
  if (ms == null) return "—";
  if (ms < 1000) return `${Math.round(ms)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

export function formatTokens(tokens: number | null | undefined): string {
  if (tokens == null) return "—";
  if (tokens < 1000) return String(tokens);
  return `${(tokens / 1000).toFixed(1)}k`;
}

export function formatConfidence(score: number | null | undefined): string {
  if (score == null) return "—";
  return `${(score * 100).toFixed(1)}%`;
}

export function formatCost(cost: number | null | undefined): string {
  if (cost == null) return "—";
  return `$${cost.toFixed(6)}`;
}

export function statusColor(status: string): string {
  switch (status) {
    case "completed":
      return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    case "running":
      return "bg-blue-500/15 text-blue-400 border-blue-500/30";
    case "failed":
      return "bg-red-500/15 text-red-400 border-red-500/30";
    default:
      return "bg-zinc-500/15 text-zinc-400 border-zinc-500/30";
  }
}

export function nodeTypeColor(type: string): string {
  switch (type) {
    case "retrieval":
      return "#6366f1";
    case "tool":
      return "#f59e0b";
    case "llm":
      return "#10b981";
    case "postprocessing":
      return "#8b5cf6";
    default:
      return "#6b7280";
  }
}
