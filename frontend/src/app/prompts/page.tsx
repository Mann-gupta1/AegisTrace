"use client";

import { useState } from "react";
import { usePrompts, usePromptComparison } from "@/lib/api";
import PromptComparison from "@/components/PromptComparison";

export default function PromptsPage() {
  const { data: prompts } = usePrompts();
  const [v1, setV1] = useState("");
  const [v2, setV2] = useState("");
  const { data: comparison } = usePromptComparison(v1, v2);

  return (
    <div>
      <h1 className="text-2xl font-semibold tracking-tight">
        Prompt Versions
      </h1>
      <p className="mt-1 text-sm text-muted-foreground">
        Registry of prompt templates with version comparison.
      </p>

      <div className="mt-8">
        <h2 className="text-lg font-semibold">Prompt Registry</h2>
        <div className="mt-4 space-y-3">
          {(prompts || []).map((p: any) => (
            <div
              key={p.id}
              className="rounded-xl border border-border bg-card p-4"
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium">{p.prompt_name}</span>
                  <span className="ml-2 rounded-full bg-accent/15 px-2 py-0.5 text-xs font-medium text-accent">
                    v{p.version}
                  </span>
                </div>
                <span className="text-xs text-muted-foreground">
                  {new Date(p.created_at).toLocaleDateString()}
                </span>
              </div>
              <pre className="mt-3 max-h-24 overflow-auto rounded-lg bg-muted/30 p-3 text-xs text-muted-foreground">
                {p.template_text}
              </pre>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-lg font-semibold">Compare Versions</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Select two prompt versions to compare performance metrics.
        </p>
        <div className="mt-4 flex gap-4">
          <select
            value={v1}
            onChange={(e) => setV1(e.target.value)}
            className="rounded-lg border border-border bg-card px-3 py-2 text-sm"
          >
            <option value="">Version 1</option>
            {(prompts || []).map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.prompt_name} v{p.version}
              </option>
            ))}
          </select>
          <select
            value={v2}
            onChange={(e) => setV2(e.target.value)}
            className="rounded-lg border border-border bg-card px-3 py-2 text-sm"
          >
            <option value="">Version 2</option>
            {(prompts || []).map((p: any) => (
              <option key={p.id} value={p.id}>
                {p.prompt_name} v{p.version}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-6">
          <PromptComparison data={comparison || null} />
        </div>
      </div>
    </div>
  );
}
