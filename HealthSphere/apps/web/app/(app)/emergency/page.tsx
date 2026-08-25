"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Badge, Button, Card, DisclaimerNote, EmptyState, PageHeader } from "@/components/ui";

interface Alert {
  id: number; triggered_at: string; status: string;
  message_sent: string | null; notified: string[]; cancelled_at: string | null;
}
interface Profile {
  blood_group: string | null; allergies: string | null; emergency_information: string | null;
}

const STATUS_TONE: Record<string, "red" | "amber" | "slate" | "brand"> = {
  pending: "amber", sent: "red", acknowledged: "brand", resolved: "slate", cancelled: "slate",
};

export default function EmergencyPage() {
  const qc = useQueryClient();
  const alerts = useQuery<Alert[]>({ queryKey: ["alerts"], queryFn: () => api("/emergency/alerts") });
  const profile = useQuery<Profile>({ queryKey: ["profile"], queryFn: () => api("/profile") });
  const [confirming, setConfirming] = useState(false);

  async function trigger() {
    await api("/emergency/trigger", { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    setConfirming(false);
    qc.invalidateQueries({ queryKey: ["alerts"] });
  }
  async function cancel(id: number) {
    await api(`/emergency/alerts/${id}/cancel`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" });
    qc.invalidateQueries({ queryKey: ["alerts"] });
  }

  return (
    <>
      <PageHeader title="Emergency SOS"
                  subtitle="Alert your saved emergency contacts and open a pre-filled call to local services" />

      <Card>
        <div className="flex flex-col items-center gap-4 py-6">
          <button
            onClick={() => setConfirming(true)}
            aria-label="Trigger emergency SOS alert"
            className="flex h-40 w-40 items-center justify-center rounded-full bg-red-600 text-2xl font-black tracking-widest text-white shadow-lg shadow-red-600/30 transition-transform hover:scale-105 active:scale-95 focus-visible:outline focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-red-300">
            SOS
          </button>
          <p className="max-w-md text-center text-xs leading-relaxed text-slate-500">
            Pressing SOS sends a text-format alert with your location link (if permitted) to your
            primary contact first. It does <strong>not</strong> replace calling your local emergency number.
          </p>
        </div>
      </Card>

      {profile.data && (profile.data.blood_group || profile.data.allergies || profile.data.emergency_information) && (
        <Card title="Included in the alert (medical card)" className="mt-4">
          <ul className="space-y-1.5 text-sm text-slate-700">
            {profile.data.blood_group && <li><strong>Blood group:</strong> {profile.data.blood_group}</li>}
            {profile.data.allergies && <li><strong>Allergies:</strong> {profile.data.allergies}</li>}
            {profile.data.emergency_information && (
              <li><strong>Additional info:</strong> {profile.data.emergency_information}</li>
            )}
          </ul>
        </Card>
      )}

      <h2 className="mb-3 mt-8 text-sm font-bold uppercase tracking-wider text-slate-400">Recent alerts</h2>
      {!alerts.data?.length ? (
        <EmptyState message="No SOS alerts triggered." />
      ) : (
        <ul className="space-y-3">
          {alerts.data.map((a) => (
            <li key={a.id} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-semibold text-slate-800">{new Date(a.triggered_at).toLocaleString()}</p>
                <div className="flex items-center gap-2">
                  <Badge tone={STATUS_TONE[a.status] ?? "slate"}>{a.status}</Badge>
                  {(a.status === "pending" || a.status === "sent") && !a.cancelled_at && (
                    <Button variant="secondary" className="!px-3 !py-1 !text-xs" onClick={() => cancel(a.id)}>
                      Mark safe / cancel
                    </Button>
                  )}
                </div>
              </div>
              {!!a.notified.length && (
                <p className="mt-1.5 text-xs text-slate-500">Notified: {a.notified.join(", ")}</p>
              )}
              {a.message_sent && <p className="mt-1 rounded bg-slate-50 p-2 font-mono text-[11px] text-slate-500">{a.message_sent}</p>}
            </li>
          ))}
        </ul>
      )}

      <div className="mt-6"><DisclaimerNote>
        In a real emergency, always call your local emergency number directly. This feature is a
        notification aid, not a life-safety service.
      </DisclaimerNote></div>

      <ConfirmDialog open={confirming} onConfirm={trigger} onCancel={() => setConfirming(false)} />
    </>
  );
}

function ConfirmDialog({ open, onConfirm, onCancel }: { open: boolean; onConfirm: () => void; onCancel: () => void }) {
  if (!open) return null;
  return (
    <div role="dialog" aria-modal="true" aria-labelledby="sos-title" className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="w-full max-w-sm rounded-xl bg-white p-6 text-center shadow-xl">
        <h2 id="sos-title" className="text-lg font-bold text-red-700">Trigger SOS alert?</h2>
        <p className="mt-2 text-sm leading-relaxed text-slate-600">
          Your saved emergency contacts will be alerted. If this is an actual emergency, call your
          local emergency number now.
        </p>
        <div className="mt-5 flex flex-col gap-2">
          <Button variant="danger" onClick={onConfirm}>Yes — send alert</Button>
          <Button variant="secondary" onClick={onCancel}>Cancel</Button>
        </div>
      </div>
    </div>
  );
}
