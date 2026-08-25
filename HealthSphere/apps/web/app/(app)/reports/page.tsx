"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { api, apiUpload } from "@/lib/api";
import { Button, Card, DisclaimerNote, ErrorBanner, PageHeader, StatusBadge } from "@/components/ui";

interface ReportRow {
  id: number; file_name: string; category: string; status: string;
  report_date: string | null; created_at: string;
}

export default function ReportsPage() {
  const reports = useQuery<ReportRow[]>({ queryKey: ["reports"], queryFn: () => api("/reports") });
  const [aId, setAId] = useState<number | null>(null);
  const [bId, setBId] = useState<number | null>(null);
  const [compare, setCompare] = useState<CompareResult | null>(null);
  const [compareError, setCompareError] = useState("");

  const rows = reports.data ?? [];

  async function runCompare() {
    setCompareError(""); setCompare(null);
    if (!aId || !bId) return;
    try {
      const result = await api<CompareResult>(`/reports/compare?a=${aId}&b=${bId}`);
      setCompare(result);
    } catch (err) {
      setCompareError(err instanceof Error ? err.message : "Comparison failed");
    }
  }

  return (
    <>
      <PageHeader
        title="Medical Reports"
        subtitle="Upload a PDF or photo of a report — values are extracted automatically"
        action={<a href="/reports/upload" className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">Upload Report</a>}
      />

      <Card title="Your reports" className="mb-6">
        {!rows.length ? (
          <p className="text-sm text-slate-400">No reports yet. Upload your first lab report to get started.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-400">
                  <th className="pb-2 pr-4">File</th>
                  <th className="pb-2 pr-4">Category</th>
                  <th className="pb-2 pr-4">Report date</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2"></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className="border-b border-slate-100 last:border-0">
                    <td className="py-2.5 pr-4 font-medium">{r.file_name}</td>
                    <td className="py-2.5 pr-4 capitalize text-slate-500">{r.category.replace("_", " ")}</td>
                    <td className="py-2.5 pr-4 text-slate-500">
                      {r.report_date ? new Date(r.report_date).toLocaleDateString() : "—"}
                    </td>
                    <td className="py-2.5 pr-4"><StatusBadge status={r.status} /></td>
                    <td className="py-2.5">
                      <a href={`/reports/${r.id}`} className="font-semibold text-brand-700 hover:underline">View</a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      <Card title="Compare two reports">
        <DisclaimerNote>Only the same test on both reports is compared — with dates shown so you can verify against originals.</DisclaimerNote>
        <div className="mt-3 flex flex-wrap items-end gap-3">
          <select aria-label="Report A" value={aId ?? ""} onChange={(e) => setAId(Number(e.target.value))}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
            <option value="">Report A…</option>
            {rows.map((r) => <option key={r.id} value={r.id}>{r.file_name}</option>)}
          </select>
          <span aria-hidden="true" className="pb-1.5 font-bold text-slate-400">vs</span>
          <select aria-label="Report B" value={bId ?? ""} onChange={(e) => setBId(Number(e.target.value))}
                  className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
            <option value="">Report B…</option>
            {rows.map((r) => <option key={r.id} value={r.id}>{r.file_name}</option>)}
          </select>
          <Button onClick={runCompare} disabled={!aId || !bId || aId === bId}>Compare</Button>
        </div>
        {compareError && <div className="mt-3"><ErrorBanner message={compareError} /></div>}
        {compare && (
          <div className="mt-4 overflow-x-auto rounded-lg border border-slate-100">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
                  <th className="px-3 py-2">Test</th>
                  <th className="px-3 py-2">Previous ({new Date(compare.report_a.date).toLocaleDateString()})</th>
                  <th className="px-3 py-2">Current ({new Date(compare.report_b.date).toLocaleDateString()})</th>
                  <th className="px-3 py-2">Trend</th>
                </tr>
              </thead>
              <tbody>
                {compare.comparisons.length === 0 ? (
                  <tr><td colSpan={4} className="px-3 py-4 text-center text-slate-400">No shared tests between these reports.</td></tr>
                ) : (
                  compare.comparisons.map((c) => (
                    <tr key={c.test_name} className="border-t border-slate-100">
                      <td className="px-3 py-2 font-medium">{c.test_name}</td>
                      <td className="px-3 py-2 text-slate-600">{c.report_a.value}{c.unit && ` ${c.unit}`}</td>
                      <td className="px-3 py-2 text-slate-600">{c.report_b.value}{c.unit && ` ${c.unit}`}</td>
                      <td className={`px-3 py-2 font-semibold ${c.trend === "up" ? "text-amber-600" : c.trend === "down" ? "text-sky-600" : "text-emerald-600"}`}>
                        {c.trend === "up" ? "↑" : c.trend === "down" ? "↓" : "→"}
                        <span className="ml-1 text-xs font-normal text-slate-400">{c.delta > 0 ? "+" : ""}{c.delta}</span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  );
}

interface CompareResult {
  report_a: { id: number; date: string; file_name: string };
  report_b: { id: number; date: string; file_name: string };
  comparisons: {
    test_name: string; unit: string | null;
    report_a: { id: number; date: string; value: number };
    report_b: { id: number; date: string; value: number };
    delta: number; trend: string; direction: string;
  }[];
}
