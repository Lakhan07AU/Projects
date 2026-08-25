"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Badge, Card, EmptyState, PageHeader, StatusBadge } from "@/components/ui";
import { TrendChart, TrendArrow, type TrendPoint } from "@/components/charts";

interface MetricSummary {
  metrics: {
    metric_key: string;
    display_name: string;
    value: number;
    secondary_value: number | null;
    unit: string | null;
    recorded_at: string;
    source: string;
  }[];
}
interface ReportItem { id: number; file_name: string; category: string; status: string; created_at: string; report_date: string | null }
interface RecoItem { id: number; topic: string; guidance: string | null; priority: string }
interface ReminderItem { id: number; title: string; due_at: string; status: string }

export default function DashboardPage() {
  const summary = useQuery<MetricSummary>({ queryKey: ["metrics-summary"], queryFn: () => api("/health-metrics/summary") });
  const reports = useQuery<ReportItem[]>({ queryKey: ["reports"], queryFn: () => api("/reports?limit=5") });
  const recos = useQuery<RecoItem[]>({ queryKey: ["recommendations"], queryFn: () => api("/recommendations") });
  const reminders = useQuery<ReminderItem[]>({ queryKey: ["reminders-open"], queryFn: () => api("/reminders?status=open") });

  const weightTrend = useQuery<TrendPoint[]>({
    queryKey: ["trend", "weight"],
    queryFn: () => api<{ points: TrendPoint[] }>("/health-metrics/weight/trend").then((d) => d.points),
    retry: false,
  });

  return (
    <>
      <PageHeader
        title="Health Overview"
        subtitle="Your records at a glance"
        action={
          <div className="flex gap-2">
            <Link href="/reports/upload" className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">
              Upload Report
            </Link>
            <Link href="/profile" className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
              Edit Profile
            </Link>
          </div>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Latest metrics */}
        <Card title="Latest measurements" className="lg:col-span-2">
          {summary.isLoading ? (
            <p className="text-sm text-slate-400">Loading…</p>
          ) : !summary.data?.metrics.length ? (
            <EmptyState message="No health data recorded yet." hint="Add a measurement from your Profile or upload a report." />
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {summary.data.metrics.slice(0, 6).map((m) => (
                <div key={m.metric_key} className="rounded-lg border border-slate-100 bg-slate-50 p-3">
                  <p className="text-xs font-medium text-slate-500">{m.display_name}</p>
                  <p className="mt-1 text-xl font-bold text-slate-900">
                    {m.value}
                    {m.secondary_value != null && ` / ${m.secondary_value}`}
                    {m.unit && <span className="ml-1 text-xs font-normal text-slate-500">{m.unit}</span>}
                  </p>
                  <p className="text-[11px] text-slate-400">{new Date(m.recorded_at).toLocaleDateString()}</p>
                </div>
              ))}
            </div>
          )}
          <div className="mt-3 flex justify-end">
            <Link href="/health" className="text-sm font-semibold text-brand-700 hover:underline">Track health →</Link>
          </div>
        </Card>

        {/* AI insights */}
        <Card title="Guidance topics" action={<Link href="/recommendations" className="text-xs font-semibold text-brand-700 hover:underline">View all</Link>}>
          {!recos.data?.length ? (
            <EmptyState message="No active guidance right now." />
          ) : (
            <ul className="space-y-3">
              {recos.data.slice(0, 3).map((r) => (
                <li key={r.id} className="rounded-lg bg-brand-50 p-3">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold uppercase tracking-wide text-brand-800">
                      {r.topic.replace(/_/g, " ")}
                    </span>
                    <Badge tone={r.priority === "high" ? "red" : r.priority === "medium" ? "amber" : "slate"}>
                      {r.priority}
                    </Badge>
                  </div>
                  <p className="mt-1 line-clamp-3 text-xs leading-relaxed text-slate-600">{r.guidance}</p>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Weight trend */}
        <Card title="Weight trend" className="md:col-span-2">
          {weightTrend.isError || !weightTrend.data?.length ? (
            <EmptyState message="Not enough data for a weight trend yet." />
          ) : (
            <>
              <TrendChart points={weightTrend.data} unit="kg" height={200} />
              <p className="mt-2 text-xs text-slate-400">
                Trends show changes in your own records. They are not medical assessments.
              </p>
            </>
          )}
        </Card>

        {/* Recent reports */}
        <Card title="Recent reports" action={<Link href="/reports" className="text-xs font-semibold text-brand-700 hover:underline">All</Link>}>
          {!reports.data?.length ? (
            <EmptyState message="No reports uploaded." hint="Upload a lab report to extract its values." />
          ) : (
            <ul className="space-y-2.5">
              {reports.data.map((r) => (
                <li key={r.id}>
                  <Link href={`/reports/${r.id}`} className="flex items-center justify-between rounded-lg p-2 hover:bg-slate-50">
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-slate-800">{r.file_name}</p>
                      <p className="text-xs text-slate-400">
                        {r.category.replace("_", " ")} · {new Date(r.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <StatusBadge status={r.status} />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Reminders */}
        <Card title="Upcoming reminders" action={<Link href="/health/timeline" className="text-xs font-semibold text-brand-700 hover:underline">Timeline</Link>}>
          {!reminders.data?.length ? (
            <EmptyState message="Nothing scheduled." />
          ) : (
            <ul className="space-y-2.5">
              {reminders.data.slice(0, 4).map((r) => (
                <li key={r.id} className="flex items-start gap-2 rounded-lg border border-slate-100 p-2.5">
                  <span aria-hidden="true" className="mt-0.5">⏰</span>
                  <div>
                    <p className="text-sm font-medium text-slate-800">{r.title}</p>
                    <p className="text-xs text-slate-400">{new Date(r.due_at).toLocaleString()}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>

        {/* Emergency quick card */}
        <Card title="Emergency readiness">
          <p className="text-sm text-slate-600">
            Keep critical information one tap away — blood group, allergies, conditions and
            emergency contacts.
          </p>
          <Link
            href="/emergency"
            className="mt-3 inline-flex w-full items-center justify-center rounded-lg bg-red-600 px-4 py-2.5 text-sm font-bold text-white hover:bg-red-700"
          >
            Open Emergency Screen
          </Link>
        </Card>
      </div>
    </>
  );
}
