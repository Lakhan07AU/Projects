"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, DisclaimerNote, ErrorBanner, Input, PageHeader } from "@/components/ui";

interface Profile {
  date_of_birth: string | null;
  sex: string | null;
  height_cm: number | null;
  weight_kg: number | null;
  blood_group: string | null;
  allergies: string | null;
  diet_preferences: string | null;
  exercise_preferences: string | null;
  emergency_information: string | null;
  age?: number | null;
  bmi?: number | null;
}
interface UserConditionRow { id: number; condition_name: string; diagnosed_year: number | null; status: string }
interface MedicationRow { id: number; name: string; dosage: string | null; status: string }

export default function ProfilePage() {
  const qc = useQueryClient();
  const profile = useQuery<Profile>({ queryKey: ["profile"], queryFn: () => api("/profile") });
  const conditions = useQuery<UserConditionRow[]>({ queryKey: ["my-conditions"], queryFn: () => api("/conditions/mine") });
  const meds = useQuery<MedicationRow[]>({ queryKey: ["medications"], queryFn: () => api("/medications") });

  const [form, setForm] = useState<Partial<Profile>>({});
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (profile.data) setForm(profile.data);
  }, [profile.data]);

  async function save() {
    setError("");
    setSaved(false);
    try {
      await api("/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...form,
          height_cm: form.height_cm ? Number(form.height_cm) : null,
          weight_kg: form.weight_kg ? Number(form.weight_kg) : null,
        }),
      });
      setSaved(true);
      qc.invalidateQueries({ queryKey: ["profile"] });
      // New profile facts can change guidance → refresh recommendations
      api("/recommendations/refresh", { method: "POST" }).catch(() => undefined);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save");
    }
  }

  function field(key: keyof Profile) {
    return {
      value: (form[key] as string | null) ?? "",
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setForm((f) => ({ ...f, [key]: e.target.value })),
    };
  }

  return (
    <>
      <PageHeader
        title="Personal Health Profile"
        subtitle="The central record all HealthSphere features build upon"
        action={<Button onClick={save} disabled={profile.isLoading}>Save changes</Button>}
      />
      {saved && (
        <div role="status" className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          Profile saved.
        </div>
      )}
      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Basics">
          <div className="grid gap-4 sm:grid-cols-2">
            <Input id="dob" label="Date of birth" type="date" {...field("date_of_birth")} />
            <Input id="sex" label="Sex" placeholder="female / male / other" {...field("sex")} />
            <Input id="height" label="Height (cm)" type="number" step="0.1" {...field("height_cm")} />
            <Input id="weight" label="Weight (kg)" type="number" step="0.1" {...field("weight_kg")} />
            <Input id="blood" label="Blood group" placeholder="O+" {...field("blood_group")} />
            <Input id="diet" label="Diet preference" placeholder="vegetarian…" {...field("diet_preferences")} />
          </div>
          {form.bmi != null && (
            <p className="mt-3 text-xs text-slate-500">
              Calculated BMI: <strong>{form.bmi}</strong>
              {form.age != null && <> · Age: <strong>{form.age}</strong></>}
            </p>
          )}
        </Card>

        <Card title="Safety-critical information">
          <div className="space-y-4">
            <Input id="allergies" label="Allergies" placeholder="e.g. Penicillin" {...field("allergies")} />
            <Input id="exercise" label="Exercise preferences" placeholder="walking, yoga…" {...field("exercise_preferences")} />
            <Input id="emerginfo" label="Emergency information" placeholder="Anything first responders should know" {...field("emergency_information")} />
            <DisclaimerNote>
              This information appears on your Emergency screen so it is quickly available when it
              matters most.
            </DisclaimerNote>
          </div>
        </Card>

        <Card title="Existing conditions">
          <ConditionsSection rows={conditions.data ?? []} onChanged={() => qc.invalidateQueries({ queryKey: ["my-conditions"] })} />
        </Card>

        <Card title="Medication records">
          <p className="mb-3 text-xs text-slate-400">
            A personal record of what you take. HealthSphere never manages or adjusts prescriptions.
          </p>
          <MedicationsSection rows={meds.data ?? []} onChanged={() => qc.invalidateQueries({ queryKey: ["medications"] })} />
        </Card>
      </div>
    </>
  );
}

function ConditionsSection({ rows, onChanged }: { rows: UserConditionRow[]; onChanged: () => void }) {
  const [name, setName] = useState("");
  const [year, setYear] = useState("");
  const [busy, setBusy] = useState(false);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    try {
      await api("/conditions/mine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          condition_name: name.trim(),
          diagnosed_year: year ? Number(year) : null,
        }),
      });
      setName(""); setYear(""); onChanged();
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      {!rows.length ? (
        <p className="text-sm text-slate-400">No conditions recorded.</p>
      ) : (
        <ul className="mb-3 space-y-2">
          {rows.map((r) => (
            <li key={r.id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2">
              <span className="text-sm">
                {r.condition_name}
                {r.diagnosed_year && <span className="ml-1.5 text-xs text-slate-400">(since {r.diagnosed_year})</span>}
              </span>
              <button
                aria-label={`Delete ${r.condition_name}`}
                className="text-xs font-semibold text-red-500 hover:text-red-700"
                onClick={async () => { await api(`/conditions/mine/${r.id}`, { method: "DELETE" }); onChanged(); }}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={add} className="flex flex-wrap items-end gap-2">
        <div className="min-w-[10rem] flex-1">
          <Input id="cond-name" label="Condition" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="w-24">
          <Input id="cond-year" label="Year" value={year} onChange={(e) => setYear(e.target.value)} inputMode="numeric" />
        </div>
        <Button type="submit" variant="secondary" disabled={busy}>Add</Button>
      </form>
    </>
  );
}

function MedicationsSection({ rows, onChanged }: { rows: MedicationRow[]; onChanged: () => void }) {
  const [name, setName] = useState("");
  const [dosage, setDosage] = useState("");

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    await api("/medications", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: name.trim(), dosage: dosage.trim() || null }),
    });
    setName(""); setDosage(""); onChanged();
  }

  return (
    <>
      {!rows.length ? (
        <p className="text-sm text-slate-400">No medication records.</p>
      ) : (
        <ul className="mb-3 space-y-2">
          {rows.map((m) => (
            <li key={m.id} className="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2">
              <span className="text-sm">{m.name}{m.dosage && <span className="ml-1.5 text-xs text-slate-400">{m.dosage}</span>}</span>
              <button
                aria-label={`Delete ${m.name}`}
                className="text-xs font-semibold text-red-500 hover:text-red-700"
                onClick={async () => { await api(`/medications/${m.id}`, { method: "DELETE" }); onChanged(); }}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={add} className="flex flex-wrap items-end gap-2">
        <div className="min-w-[8rem] flex-1">
          <Input id="med-name" label="Medication" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div className="w-32">
          <Input id="med-dose" label="Dosage" value={dosage} onChange={(e) => setDosage(e.target.value)} />
        </div>
        <Button type="submit" variant="secondary">Add</Button>
      </form>
    </>
  );
}
