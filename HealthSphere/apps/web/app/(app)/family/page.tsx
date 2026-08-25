"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, DisclaimerNote, EmptyState, ErrorBanner, Input, Modal, PageHeader } from "@/components/ui";

interface FamilyConditionRow { id: number; condition_name: string; diagnosis_age: number | null }
interface FamilyMember {
  id: number;
  relationship: string;
  name: string;
  date_of_birth: string | null;
  living_status: string;
  relevant_notes: string | null;
  conditions: FamilyConditionRow[];
}
interface Pattern { condition: string; occurrences: string[]; note: string }

const RELATIONSHIPS = ["father", "mother", "brother", "sister", "son", "daughter", "grandfather", "grandmother", "uncle", "aunt", "other"];

export default function FamilyPage() {
  const qc = useQueryClient();
  const members = useQuery<FamilyMember[]>({ queryKey: ["family"], queryFn: () => api("/family/members") });
  const summary = useQuery<{ total_members: number; patterns: Pattern[] }>({
    queryKey: ["family-summary"],
    queryFn: () => api("/family/summary"),
  });

  const [addOpen, setAddOpen] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);

  const selectedMember = members.data?.find((m) => m.id === selected);

  return (
    <>
      <PageHeader
        title="Family Health History"
        subtitle="Understanding shared history helps inform preventive-care discussions"
        action={<Button onClick={() => setAddOpen(true)}>Add family member</Button>}
      />

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card title="Family tree">
            {members.isLoading ? (
              <p className="text-sm text-slate-400">Loading…</p>
            ) : !members.data?.length ? (
              <EmptyState message="No family members added yet." hint="Start with your parents — their history is often most relevant." />
            ) : (
              <div className="grid gap-3 sm:grid-cols-2">
                {members.data.map((m) => (
                  <button
                    key={m.id}
                    onClick={() => setSelected(m.id)}
                    aria-expanded={selected === m.id}
                    className={`rounded-xl border p-4 text-left transition-colors ${
                      selected === m.id ? "border-brand-400 bg-brand-50" : "border-slate-200 hover:border-brand-200"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-800">{m.name}</span>
                      <span className="text-xs font-medium uppercase tracking-wide text-brand-700">{m.relationship}</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-500">
                      {m.living_status === "deceased" ? "Deceased" : m.living_status === "living" ? "Living" : "Status unknown"}
                    </p>
                    {m.conditions.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {m.conditions.map((c) => (
                          <span key={c.id} className="rounded-full bg-white px-2 py-0.5 text-[11px] font-medium text-slate-600 ring-1 ring-slate-200">
                            {c.condition_name}{c.diagnosis_age != null && ` · age ${c.diagnosis_age}`}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </Card>
        </div>

        <Card title="Potentially relevant patterns">
          {!summary.data?.patterns.length ? (
            <EmptyState message="Patterns appear once family conditions are recorded." />
          ) : (
            <>
              <ul className="space-y-3">
                {summary.data.patterns.map((p) => (
                  <li key={p.condition} className="rounded-lg bg-slate-50 p-3">
                    <p className="text-sm font-semibold text-slate-800">{p.condition}</p>
                    <p className="mt-0.5 text-xs text-slate-500">Reported for: {p.occurrences.join(", ")}</p>
                    <p className="mt-1 text-xs text-slate-400">{p.note}</p>
                  </li>
                ))}
              </ul>
              <div className="mt-3"><DisclaimerNote>
                The system only shows what you have entered. These observations are meant to be
                mentioned during preventive-care discussions with a professional.
              </DisclaimerNote></div>
            </>
          )}
        </Card>
      </div>

      {/* Member detail modal */}
      <Modal open={!!selectedMember} onClose={() => setSelected(null)} title={selectedMember?.name ?? ""}>
        {selectedMember && (
          <MemberDetail
            member={selectedMember}
            onChanged={() => {
              qc.invalidateQueries({ queryKey: ["family"] });
              qc.invalidateQueries({ queryKey: ["family-summary"] });
            }}
            onClose={() => setSelected(null)}
          />
        )}
      </Modal>

      <AddMemberModal open={addOpen} onClose={() => setAddOpen(false)} onAdded={() => {
        qc.invalidateQueries({ queryKey: ["family"] });
        qc.invalidateQueries({ queryKey: ["family-summary"] });
      }} />
    </>
  );
}

function MemberDetail({ member, onChanged, onClose }: { member: FamilyMember; onChanged: () => void; onClose: () => void }) {
  const [condName, setCondName] = useState("");
  const [diagAge, setDiagAge] = useState("");
  const [error, setError] = useState("");

  async function addCondition(e: React.FormEvent) {
    e.preventDefault();
    if (!condName.trim()) return;
    setError("");
    try {
      await api(`/family/members/${member.id}/conditions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          condition_name: condName.trim(),
          diagnosis_age: diagAge ? Number(diagAge) : null,
        }),
      });
      setCondName(""); setDiagAge(""); onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add condition");
    }
  }

  return (
    <div>
      {error && <ErrorBanner message={error} />}
      <dl className="mb-4 space-y-1 text-sm">
        <div className="flex gap-2"><dt className="w-28 text-slate-500">Relationship</dt><dd className="capitalize">{member.relationship}</dd></div>
        <div className="flex gap-2"><dt className="w-28 text-slate-500">Date of birth</dt><dd>{member.date_of_birth ?? "—"}</dd></div>
        <div className="flex gap-2"><dt className="w-28 text-slate-500">Notes</dt><dd>{member.relevant_notes ?? "—"}</dd></div>
      </dl>

      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Recorded conditions</h3>
      {member.conditions.length === 0 ? (
        <p className="mb-3 text-sm text-slate-400">None recorded.</p>
      ) : (
        <ul className="mb-3 space-y-1.5">
          {member.conditions.map((c) => (
            <li key={c.id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm">
              <span>{c.condition_name}{c.diagnosis_age != null && <span className="ml-1 text-xs text-slate-400">diagnosed ~age {c.diagnosis_age}</span>}</span>
              <button
                aria-label={`Remove ${c.condition_name}`}
                className="text-xs font-semibold text-red-500 hover:text-red-700"
                onClick={async () => { await api(`/family/conditions/${c.id}`, { method: "DELETE" }); onChanged(); }}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}

      <form onSubmit={addCondition} className="flex flex-wrap items-end gap-2">
        <div className="min-w-[9rem] flex-1">
          <Input id="fc-name" label="Condition" value={condName} onChange={(e) => setCondName(e.target.value)} />
        </div>
        <div className="w-20">
          <Input id="fc-age" label="Diag. age" inputMode="numeric" value={diagAge} onChange={(e) => setDiagAge(e.target.value)} />
        </div>
        <Button type="submit" variant="secondary">Add</Button>
      </form>

      <div className="mt-5 border-t border-slate-100 pt-4">
        <button
          className="text-sm font-semibold text-red-600 hover:text-red-700"
          onClick={async () => {
            if (!confirm(`Remove ${member.name} and all recorded conditions?`)) return;
            await api(`/family/members/${member.id}`, { method: "DELETE" });
            onChanged(); onClose();
          }}
        >
          Remove family member
        </button>
      </div>
    </div>
  );
}

function AddMemberModal({ open, onClose, onAdded }: { open: boolean; onClose: () => void; onAdded: () => void }) {
  const [relationship, setRelationship] = useState("father");
  const [name, setName] = useState("");
  const [dob, setDob] = useState("");
  const [status, setStatus] = useState("living");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await api("/family/members", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          relationship,
          name: name.trim(),
          date_of_birth: dob || null,
          living_status: status,
          relevant_notes: notes.trim() || null,
        }),
      });
      setName(""); setDob(""); setNotes(""); onClose(); onAdded();
    } finally {
      setBusy(false);
    }
  }

  return (
    <Modal open={open} onClose={onClose} title="Add family member">
      <form onSubmit={submit} className="space-y-4">
        <Input id="fm-name" label="Name (or nickname)" value={name} onChange={(e) => setName(e.target.value)} required />
        <label htmlFor="fm-rel" className="block text-sm font-medium text-slate-700">Relationship</label>
        <select id="fm-rel" value={relationship} onChange={(e) => setRelationship(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {RELATIONSHIPS.map((r) => <option key={r} value={r}>{r[0].toUpperCase() + r.slice(1)}</option>)}
        </select>
        <Input id="fm-dob" label="Date of birth (optional)" type="date" value={dob} onChange={(e) => setDob(e.target.value)} />
        <label htmlFor="fm-status" className="block text-sm font-medium text-slate-700">Living status</label>
        <select id="fm-status" value={status} onChange={(e) => setStatus(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
          <option value="living">Living</option>
          <option value="deceased">Deceased</option>
          <option value="unknown">Unknown</option>
        </select>
        <Input id="fm-notes" label="Notes (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} />
        <Button type="submit" disabled={busy} className="w-full">{busy ? "Adding…" : "Add member"}</Button>
      </form>
    </Modal>
  );
}
