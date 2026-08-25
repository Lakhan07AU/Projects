"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api, apiBlob, clearTokens, saveBlob } from "@/lib/api";
import { Badge, Button, Card, DisclaimerNote, Input, PageHeader } from "@/components/ui";

interface Consent {
  id: number; consent_type: string; granted: boolean; version: string;
}

const CONSENT_TYPES: Record<string, string> = {
  medical_data_processing: "Process my reports and metrics to power insights and the assistant",
  ai_analysis: "Let the AI explain my reports in plain language",
  location_access: "Use my location only when I open Nearby Care",
  contact_import: "Read device contacts to pre-fill emergency contact forms",
  data_sharing: "Share any data with third parties (nothing is shared by default)",
  notifications: "Show in-app reminders and guidance notifications",
};

export default function SettingsPage() {
  const qc = useQueryClient();
  const consents = useQuery<Consent[]>({ queryKey: ["consents"], queryFn: () => api("/consents") });
  const [confirmText, setConfirmText] = useState("");
  const [deleting, setDeleting] = useState(false);

  function isGranted(type: string): boolean {
    return consents.data?.find((c) => c.consent_type === type)?.granted ?? false;
  }

  async function toggle(consentType: string, granted: boolean) {
    await api("/consents", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ consent_type: consentType, granted }),
    });
    qc.invalidateQueries({ queryKey: ["consents"] });
  }

  async function exportJson() {
    saveBlob(await apiBlob("/export/json"), "healthsphere-export.json");
  }
  async function exportCsv() {
    saveBlob(await apiBlob("/export/metrics.csv"), "healthsphere-metrics.csv");
  }

  async function deleteAccount() {
    if (confirmText !== "DELETE" || deleting) return;
    setDeleting(true);
    try {
      await api(`/account/delete-request?confirm_text=${encodeURIComponent(confirmText)}`, { method: "POST" });
      clearTokens();
      location.href = "/login";
    } finally {
      setDeleting(false);
    }
  }

  return (
    <>
      <PageHeader title="Privacy & Settings"
                  subtitle="You own your health data. Control it here — no hidden processing." />

      <Card title="Consent controls">
        <ul className="divide-y divide-slate-100">
          {Object.entries(CONSENT_TYPES).map(([type, description]) => (
            <li key={type} className="flex items-center justify-between gap-4 py-3.5">
              <div>
                <p className="text-sm font-semibold capitalize text-slate-800">{type.replace(/_/g, " ")}</p>
                <p className="mt-0.5 text-xs leading-relaxed text-slate-500">{description}</p>
              </div>
              <label className="flex shrink-0 cursor-pointer items-center gap-2 text-xs font-semibold">
                <span className={isGranted(type) ? "text-emerald-600" : "text-slate-400"}>
                  {isGranted(type) ? "Granted" : "Revoked"}
                </span>
                <input type="checkbox" role="switch" checked={isGranted(type)}
                       onChange={(e) => toggle(type, e.target.checked)}
                       aria-label={`Toggle ${type} consent`}
                       className="h-5 w-9 appearance-none rounded-full bg-slate-200 transition-colors before:block before:h-4 before:w-4 before:translate-x-0.5 before:rounded-full before:bg-white before:shadow checked:bg-brand-600 checked:before:translate-x-[1.15rem]" />
              </label>
            </li>
          ))}
        </ul>
      </Card>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Card title="Export your data">
          <p className="text-sm leading-relaxed text-slate-600">
            Download a complete machine-readable copy of everything stored about you — profile,
            reports, metrics, timeline, insights, and audit log.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <Button onClick={exportJson}>Export JSON</Button>
            <Button variant="secondary" onClick={exportCsv}>Metrics CSV</Button>
          </div>
        </Card>

        <Card title="Delete account & all data">
          <p className="text-sm leading-relaxed text-red-700">
            Permanently erases every record, measurement, document, insight, alert, and consent tied
            to your account, then deactivates the account itself. Type{" "}
            <Badge tone="red">DELETE</Badge> below to confirm.
          </p>
          <div className="mt-3 flex items-end gap-2">
            <Input id="confirm-del" label="" value={confirmText}
                   onChange={(e) => setConfirmText(e.target.value.toUpperCase())}
                   placeholder="Type DELETE" className="max-w-40" />
            <Button variant="danger" disabled={confirmText !== "DELETE" || deleting} onClick={deleteAccount}>
              Delete everything
            </Button>
          </div>
        </Card>
      </div>

      <div className="mt-6"><DisclaimerNote>
        Deletion is immediate and permanent in this build. Exports download directly to your device —
        nothing is stored on a server waiting to expire.
      </DisclaimerNote></div>
    </>
  );
}
