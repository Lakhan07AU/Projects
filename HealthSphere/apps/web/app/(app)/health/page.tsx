"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, DisclaimerNote, EmptyState, ErrorBanner, Input, Modal, PageHeader } from "@/components/ui";
import { TrendArrow, TrendChart, type TrendPoint } from "@/components/charts";

interface Summary {
  metrics: { metric_key: string; display_name: string; value: number; secondary_value: number | null; unit: string | null; recorded_at: string }[];
}
interface TrendResponse {
  metric_key: string;
  unit: string | null;
  points: TrendPoint[];
  trend: { direction: string; stability: string; possible_outlier: boolean; confidence: number };
}

const METRIC_OPTIONS = [
  ["weight", "Weight (kg)"], ["blood_pressure", "Blood pressure"], ["heart_rate", "Heart rate"],
  ["blood_glucose", "Blood glucose"], ["hba1c", "HbA1c (%)"], ["sleep_hours", "Sleep (hours)"],
  ["steps", "Steps"], ["exercise_minutes", "Exercise (min)"],
];

export default function HealthPage() {
  const qc = useQueryClient();
  const summary = useQuery<Summary>({ queryKey: ["metrics-summary"], queryFn: () => api("/health-metrics/summary") });
  const [addOpen, setAddOpen] = useState(false);
  const [viewingTrend, setViewingTrend] = useState<string | null>(null);

  return (
    <>
      <PageHeader
        title="Health Metrics"
        subtitle="Track measurements over time — manual entries and report values are combined"
        action={<Button onClick={() => setAddOpen(true)}>Add measurement</Button>}
      />

      {!summary.data?.metrics.length ? (
        <EmptyState message="No measurements recorded yet." hint="Add weight or blood pressure to start building your health graph." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {summary.data.metrics.map((m) => (
            <button key={m.metric_key} onClick={() => setViewingTrend(m.metric_key)}
                    className="rounded-xl border border-slate-200 bg-white p-5 text-left shadow-sm transition-colors hover:border-brand-300">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{m.display_name}</p>
                <TrendArrowInline metricKey={m.metric_key} />
              </div>
              <p className="mt-2 text-2xl font-bold text-slate-900">
                {m.value}
                {m.secondary_value != null && <span className="text-lg text-slate-400"> / {m.secondary_value}</span>}
                {m.unit && <span className="ml-1.5 text-sm font-normal text-slate-500">{m.unit}</span>}
              </p>
              <p className="mt-1 text-xs text-slate-400">{new Date(m.recorded_at).toLocaleDateString()}</p>
            </button>
          ))}
        </div>
      )}

      <div className="mt-6"><DisclaimerNote>
        Trends describe changes in your own records. They are informational only and are never a
        diagnosis.
      </DisclaimerNote></div>

      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add measurement">
        <MetricForm onSaved={() => { setAddOpen(false); qc.invalidateQueries({ queryKey: ["metrics-summary"] }); }} />
      </Modal>

      <TrendViewer metricKey={viewingTrend} onClose={() => setViewingTrend(null)} />
    </>
  );
}

function TrendArrowInline({ metricKey }: { metricKey: string }) {
  const trend = useQuery<TrendResponse>({
    queryKey: ["trend", metricKey],
    queryFn: () => api(`/health-metrics/${metricKey}/trend`),
    retry: false,
    staleTime: 60_000,
  });
  if (!trend.data) return null;
  return <TrendArrow direction={trend.data.trend.direction} />;
}

function MetricForm({ onSaved }: { onSaved: () => void }) {
  const [key, setKey] = useState("weight");
  const [value, setValue] = useState("");
  const [secondary, setSecondary] = useState("");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [error, setError] = useState("");

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/health-metrics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          metric_key: key,
          value: Number(value),
          secondary_value: secondary ? Number(secondary) : undefined,
          recorded_at: date ? new Date(date).toISOString() : undefined,
        }),
      });
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save measurement");
    }
  }

  const isBP = key === "blood_pressure";
  return (
    <form onSubmit={save} className="space-y-4">
      {error && <ErrorBanner message={error} />}
      <label htmlFor="mk" className="block text-sm font-medium text-slate-700">Metric
        <select id="mk" value={key} onChange={(e) => setKey(e.target.value)} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {METRIC_OPTIONS.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      </label>
      <Input id="mv" label={isBP ? "Systolic" : "Value"} type="number" step="any" value={value}
             onChange={(e) => setValue(e.target.value)} required />
      {isBP && <Input id="mv2" label="Diastolic" type="number" value={secondary}
                      onChange={(e) => setSecondary(e.target.value)} />}
      <Input id="md" label="Date" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
      <Button type="submit" className="w-full">Save measurement</Button>
    </form>
  );
}

function TrendViewer({ metricKey, onClose }: { metricKey: string | null; onClose: () => void }) {
  const qc = useQueryClient();
  const trend = useQuery<TrendResponse>({
    queryKey: ["trend", metricKey],
    queryFn: () => api(`/health-metrics/${metricKey}/trend`),
    enabled: !!metricKey,
  });
  if (!metricKey || !trend.data) return <Modal open={false} onClose={onClose} title="">null</Modal>;
  void qc;

  const t = trend.data.trend;
  return (
    <Modal open onClose={onClose} title={`Trend — ${metricKey.replace("_", " ")}`}>
      <TrendChart points={trend.data.points} unit={trend.data.unit} />
      <dl className="mt-4 grid grid-cols-2 gap-2 text-sm">
        <dt className="text-slate-500">Direction</dt><dd className="font-semibold capitalize">{t.direction.replace("_", " ")}</dd>
        <dt className="text-slate-500">Stability</dt><dd className="capitalize">{t.stability.replace("_", " ")}</dd>
        <dt className="text-slate-500">Possible outlier</dt><dd>{t.possible_outlier ? "Yes — verify unusual readings" : "No"}</dd>
        <dt className="text-slate-500">Data points</dt><dd>{trend.data.points.length}</dd>
      </dl>
      <p className="mt-3 text-xs text-slate-400">
        Based on your own records only ({trend.data.points.length} points). Confidence {(t.confidence * 100).toFixed(0)}%.
      </p>
    </Modal>
  );
}
