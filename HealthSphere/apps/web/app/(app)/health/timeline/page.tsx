"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { EmptyState, PageHeader } from "@/components/ui";

interface TimelineEvent {
  id: number; event_type: string; event_date: string; title: string;
  description: string | null; source: string;
}

const FILTERS = [
  ["all", "All"], ["report_uploaded", "Reports"], ["measurement", "Measurements"],
  ["recommendation", "Guidance"], ["family_history", "Family"], ["lifestyle", "Lifestyle"],
];

export default function TimelinePage() {
  const [filter, setFilter] = useState("all");
  const timeline = useQuery<TimelineEvent[]>({
    queryKey: ["timeline", filter],
    queryFn: () => api(`/timeline?limit=200${filter === "all" ? "" : `&event_type=${filter}`}`),
  });

  const events = timeline.data ?? [];
  // Group by month for the vertical timeline
  const groups = new Map<string, TimelineEvent[]>();
  for (const e of [...events].sort((a, b) => +new Date(b.event_date) - +new Date(a.event_date))) {
    const label = new Date(e.event_date).toLocaleDateString(undefined, { month: "long", year: "numeric" });
    if (!groups.has(label)) groups.set(label, []);
    groups.get(label)!.push(e);
  }

  return (
    <>
      <PageHeader title="Health Timeline" subtitle="Every record, in order — your digital health memory" />

      <div className="mb-5 flex flex-wrap gap-2">
        {FILTERS.map(([value, label]) => (
          <button key={value} onClick={() => setFilter(value)}
                  className={`rounded-full px-3.5 py-1.5 text-xs font-semibold ${
                    filter === value ? "bg-brand-600 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
                  }`}>
            {label}
          </button>
        ))}
      </div>

      {!events.length ? (
        <EmptyState message="No timeline events yet." hint="Upload reports and record measurements to build your history." />
      ) : (
        <div className="space-y-8">
          {[...groups.entries()].map(([month, items]) => (
            <section key={month} aria-label={month}>
              <h2 className="mb-3 text-sm font-bold uppercase tracking-wider text-slate-400">{month}</h2>
              <ol className="relative space-y-4 border-l-2 border-slate-200 pl-6">
                {items.map((e) => (
                  <li key={e.id} className="relative">
                    <span aria-hidden="true"
                          className="absolute -left-[31px] top-1 flex h-3.5 w-3.5 items-center justify-center rounded-full border-2 border-white bg-brand-500 ring-2 ring-brand-100" />
                    <div className="rounded-lg border border-slate-100 bg-white p-3 shadow-sm">
                      <p className="text-sm font-semibold text-slate-800">{e.title}</p>
                      {e.description && <p className="mt-0.5 text-xs text-slate-500">{e.description}</p>}
                      <p className="mt-1 text-[11px] text-slate-400">
                        {new Date(e.event_date).toLocaleDateString()} · {e.event_type.replace("_", " ")}
                        {e.source !== "system" && e.source !== "user" && ` · ${e.source.replace("rule:", "guideline ")}`}
                      </p>
                    </div>
                  </li>
                ))}
              </ol>
            </section>
          ))}
        </div>
      )}
    </>
  );
}
