"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useState } from "react";
import { api, apiBlob } from "@/lib/api";
import { Badge, Button, Card, ErrorBanner, Input, Modal, StatusBadge } from "@/components/ui";
import { TrendChart } from "@/components/charts";

interface Entity {
  id: number; test_name: string; value: number; unit: string | null;
  reference_low: number | null; reference_high: number | null;
  abnormal_flag: boolean; confidence: number; source_text: string | null;
}
interface Analysis {
  report: { id: number; file_name: string; category: string; status: string; error_message: string | null; analysis_summary: string | null; report_date: string | null; created_at: string };
  entities: Entity[];
  comparison: { previous_report_id: number; changes: { test_name: string; previous: number; current: number; delta: number; direction: string }[] } | null;
}

export default function ReportDetailPage() {
  const params = useParams<{ id: string }>();
  const qc = useQueryClient();
  const id = params.id;

  const analysis = useQuery<Analysis>({
    queryKey: ["report", id],
    queryFn: () => api(`/reports/${id}`),
    refetchInterval: (q) => (["uploaded", "processing", "analyzing"].includes(q.state.data?.report.status ?? "") ? 2000 : false),
  });

  const [editing, setEditing] = useState<Entity | null>(null);
  const [trendTest, setTrendTest] = useState<string | null>(null);

  if (analysis.isLoading) return <p className="text-sm text-slate-400">Loading report…</p>;
  if (analysis.isError || !analysis.data)
    return <ErrorBanner message="Report not found." />;

  const { report, entities, comparison } = analysis.data;

  async function saveCorrection(e: React.FormEvent) {
    e.preventDefault();
    if (!editing) return;
    await api(`/reports/${id}/entities/${editing.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        value: editing.value,
        unit: editing.unit,
        reference_low: editing.reference_low,
        reference_high: editing.reference_high,
      }),
    });
    setEditing(null);
    qc.invalidateQueries({ queryKey: ["report", id] });
    qc.invalidateQueries({ queryKey: ["metrics-summary"] });
  }

  async function openOriginal() {
    const blob = await apiBlob(`/reports/${id}/download`);
    const url = URL.createObjectURL(blob);
    window.open(url, "_blank", "noopener");
    setTimeout(() => URL.revokeObjectURL(url), 60_000);
  }

  return (
    <>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{report.file_name}</h1>
          <p className="mt-1 flex flex-wrap items-center gap-2 text-sm text-slate-500">
            <span className="capitalize">{report.category.replace("_", " ")}</span> ·
            <span>{report.report_date ? new Date(report.report_date).toLocaleDateString() : new Date(report.created_at).toLocaleDateString()}</span>
            · <StatusBadge status={report.status} />
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={openOriginal}>Open original</Button>
          <Button variant="secondary" onClick={() => api(`/reports/${id}/reprocess`, { method: "POST" }).then(() => qc.invalidateQueries({ queryKey: ["report", id] }))}>
            Re-analyze
          </Button>
        </div>
      </div>

      {report.status === "failed" && (
        <div className="mb-4"><ErrorBanner message={report.error_message || "Processing failed."} /></div>
      )}
      {(report.status === "processing" || report.status === "analyzing") && (
        <p role="status" className="mb-4 animate-pulse rounded-lg bg-brand-50 px-4 py-3 text-sm text-brand-800">
          Processing your report… This page updates automatically.
        </p>
      )}

      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Extracted results" className="lg:col-span-2">
          {!entities.length ? (
            <p className="text-sm text-slate-400">
              {report.status === "complete" ? "No lab values could be extracted from this document." : "Waiting for processing…"}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
                    <th className="pb-2 pr-3">Test</th>
                    <th className="pb-2 pr-3">Value</th>
                    <th className="pb-2 pr-3">Reference</th>
                    <th className="pb-2 pr-3">Status</th>
                    <th className="pb-2 pr-3">Confidence</th>
                    <th className="pb-2"></th>
                  </tr>
                </thead>
                <tbody>
                  {entities.map((e) => (
                    <tr key={e.id} className="border-b border-slate-100 last:border-0 align-top">
                      <td className="py-2.5 pr-3 font-medium">{e.test_name}</td>
                      <td className="py-2.5 pr-3">{e.value}{e.unit && ` ${e.unit}`}</td>
                      <td className="py-2.5 pr-3 text-slate-500">
                        {e.reference_low != null && e.reference_high != null ? `${e.reference_low} – ${e.reference_high}` : "not on report"}
                      </td>
                      <td className="py-2.5 pr-3">
                        {e.abnormal_flag ? <Badge tone="red">outside range</Badge> : <Badge tone="green">in range</Badge>}
                      </td>
                      <td className="py-2.5 pr-3 text-xs text-slate-500">
                        {(e.confidence * 100).toFixed(0)}%
                        {e.confidence < 0.7 && <p className="text-[10px] text-amber-600">verify manually</p>}
                      </td>
                      <td className="py-2.5 space-x-2 whitespace-nowrap">
                        <button onClick={() => setEditing(e)} className="text-xs font-semibold text-brand-700 hover:underline">Correct</button>
                        <button onClick={() => setTrendTest(e.test_name)} className="text-xs font-semibold text-brand-700 hover:underline">Trend</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="mt-2 text-xs text-slate-400">
                Values are extracted with their original wording preserved so you can verify against the document.
              </p>
            </div>
          )}
        </Card>

        <div className="space-y-4">
          {report.analysis_summary && (
            <Card title="Plain-language explanation">
              <p className="whitespace-pre-line text-sm leading-relaxed text-slate-600">{report.analysis_summary}</p>
              <p className="mt-3 text-xs text-slate-400">
                Informational only — not a medical assessment. Discuss results with a healthcare professional.
              </p>
            </Card>
          )}

          {comparison && comparison.changes.length > 0 && (
            <Card title={`Changes vs previous report`}>
              <ul className="space-y-2.5">
                {comparison.changes.map((c) => (
                  <li key={c.test_name} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm">
                    <span>{c.test_name}</span>
                    <span className="flex items-center gap-2 text-slate-500">
                      {c.previous} → <strong className="text-slate-800">{c.current}</strong>
                      <span className={`font-bold ${c.direction === "up" ? "text-amber-600" : c.direction === "down" ? "text-sky-600" : "text-emerald-600"}`}>
                        {c.direction === "up" ? "↑" : c.direction === "down" ? "↓" : "→"}
                      </span>
                    </span>
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      </div>

      {/* Correction modal */}
      <Modal open={!!editing} onClose={() => setEditing(null)} title={`Correct value — ${editing?.test_name ?? ""}`}>
        <form onSubmit={saveCorrection} className="space-y-4">
          <Input id="c-value" label="Value" type="number" step="any"
                 value={editing?.value ?? ""} onChange={(e) => setEditing((x) => x && ({ ...x, value: Number(e.target.value) }))} required />
          <Input id="c-unit" label="Unit" value={editing?.unit ?? ""}
                 onChange={(e) => setEditing((x) => x && ({ ...x, unit: e.target.value || null }))} />
          <div className="grid grid-cols-2 gap-3">
            <Input id="c-low" label="Reference low" type="number" step="any" value={editing?.reference_low ?? ""}
                   onChange={(e) => setEditing((x) => x && ({ ...x, reference_low: e.target.value === "" ? null : Number(e.target.value) }))} />
            <Input id="c-high" label="Reference high" type="number" step="any" value={editing?.reference_high ?? ""}
                   onChange={(e) => setEditing((x) => x && ({ ...x, reference_high: e.target.value === "" ? null : Number(e.target.value) }))} />
          </div>
          <Button type="submit" className="w-full">Save correction</Button>
        </form>
      </Modal>

      {/* Trend modal */}
      <TrendModal test={trendTest} onClose={() => setTrendTest(null)} />
    </>
  );
}

function TrendModal({ test, onClose }: { test: string | null; onClose: () => void }) {
  const id = useParams<{ id: string }>().id;
  const trend = useQuery<{ points: { date: string; value: number; unit: string | null }[]; trend: { direction: string } }>({
    queryKey: ["entity-trend", id, test],
    queryFn: () => api(`/reports/${id}/trend/${encodeURIComponent(test!)}`),
    enabled: !!test,
  });

  return (
    <Modal open={!!test} onClose={onClose} title={`History — ${test ?? ""}`}>
      {trend.data && (
        <>
          <TrendChart points={trend.data.points} unit={trend.data.points[0]?.unit} />
          <p className="mt-2 text-center text-sm text-slate-500">
            Direction across your records: <strong className="capitalize">{trend.data.trend.direction.replace("_", " ")}</strong>
          </p>
          <p className="mt-2 text-xs text-slate-400">
            A trend describes your own recorded values over time and is not a diagnosis.
          </p>
        </>
      )}
    </Modal>
  );
}
