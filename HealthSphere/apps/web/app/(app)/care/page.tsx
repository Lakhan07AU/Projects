"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Button, Card, DisclaimerNote, EmptyState, Input, Modal, PageHeader } from "@/components/ui";

interface Doctor {
  id: number; doctor_name: string; specialty: string | null;
  clinic: string | null; phone: string | null; is_family_doctor: boolean;
}
interface Place {
  name: string; kind: string; address: string | null; phone: string | null;
  distance_km: number; opening_hours: string | null;
}

const SPECIALTIES = ["General Physician", "Cardiology", "Endocrinology", "Pulmonology",
  "Dermatology", "Pediatrics", "Obstetrics & Gynecology", "Orthopedics", "Psychiatry", "Neurology"];
const KINDS = ["all", "hospital", "clinic", "lab", "pharmacy"];

export default function FindCarePage() {
  const [tab, setTab] = useState<"team" | "nearby">("team");
  const [addOpen, setAddOpen] = useState(false);
  const qc = useQueryClient();

  useEffect(() => {
    if (new URLSearchParams(window.location.search).get("tab") === "nearby") setTab("nearby");
  }, []);

  const doctors = useQuery<Doctor[]>({ queryKey: ["doctors"], queryFn: () => api("/doctors") });

  // Nearby care — defaults to Bengaluru until the user shares their location.
  const [kind, setKind] = useState("all");
  const [coords, setCoords] = useState({ lat: 12.9716, lon: 77.5946 });
  const nearby = useQuery<{ results: Place[] }>({
    queryKey: ["nearby", kind, coords],
    queryFn: () => api(`/healthcare/nearby?lat=${coords.lat}&lon=${coords.lon}&kind=${kind}`),
    enabled: tab === "nearby",
  });

  function locate() {
    navigator.geolocation?.getCurrentPosition(
      (p) => setCoords({
        lat: Number(p.coords.latitude.toFixed(4)),
        lon: Number(p.coords.longitude.toFixed(4)),
      }),
      () => setCoords({ lat: 12.9716, lon: 77.5946 }),
      { timeout: 8000 },
    );
  }

  async function removeDoctor(id: number) {
    await api(`/doctors/${id}`, { method: "DELETE" });
    qc.invalidateQueries({ queryKey: ["doctors"] });
  }

  return (
    <>
      <PageHeader title="Find Care" subtitle="Your personal care team and healthcare near you" />

      <div className="mb-5 flex gap-2">
        {([["team", "My care team"], ["nearby", "Nearby care"]] as const).map(([value, label]) => (
          <button key={value} onClick={() => setTab(value)}
                  className={`rounded-full px-4 py-1.5 text-sm font-semibold ${
                    tab === value ? "bg-brand-600 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200"
                  }`}>
            {label}
          </button>
        ))}
      </div>

      {tab === "team" ? (
        <>
          <div className="mb-4 flex items-center justify-between">
            <p className="text-sm text-slate-500">Doctors you actually visit — used for follow-ups and SOS context.</p>
            <Button onClick={() => setAddOpen(true)}>Add doctor</Button>
          </div>

          {!doctors.data?.length && !doctors.isLoading ? (
            <EmptyState message="No doctors in your care team yet."
                        hint="Add your family doctor or specialists you see regularly." />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2">
              {doctors.data?.map((d) => (
                <Card key={d.id}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="flex items-center gap-2 font-bold text-slate-900">
                        {d.doctor_name}
                        {d.is_family_doctor && <Badge tone="brand">Family doctor</Badge>}
                      </h2>
                      {d.specialty && <p className="text-sm font-medium text-brand-700">{d.specialty}</p>}
                      <dl className="mt-2 space-y-0.5 text-xs text-slate-600">
                        {d.clinic && <dd>{d.clinic}</dd>}
                        {d.phone && <dd className="font-mono">{d.phone}</dd>}
                      </dl>
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-1.5">
                      {d.phone && (
                        <a href={`tel:${d.phone}`}>
                          <Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button>
                        </a>
                      )}
                      <button onClick={() => removeDoctor(d.id)}
                              className="text-xs font-medium text-red-600 hover:underline">Remove</button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add a doctor to your care team">
            <DoctorForm onSaved={() => { setAddOpen(false); qc.invalidateQueries({ queryKey: ["doctors"] }); }} />
          </Modal>
        </>
      ) : (
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            {KINDS.map((k) => (
              <button key={k} onClick={() => setKind(k)}
                      className={`rounded-full px-3.5 py-1.5 text-xs font-semibold capitalize ${
                        kind === k ? "bg-brand-600 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
                      }`}>
                {k === "all" ? "All" : `${k}s`}
              </button>
            ))}
            <Button variant="secondary" className="ml-auto !px-3 !py-1.5 !text-xs" onClick={locate}>
              Use my location
            </Button>
          </div>

          {!nearby.data?.results.length && !nearby.isLoading ? (
            <EmptyState message="No places found." hint="Try widening the type filter." />
          ) : (
            nearby.data?.results.map((p) => (
              <Card key={`${p.kind}-${p.name}`}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h2 className="flex items-center gap-2 font-bold capitalize text-slate-900">
                      {p.name} <Badge tone="slate">{p.kind}</Badge>
                    </h2>
                    {p.address && <p className="mt-1 text-sm text-slate-600">{p.address}</p>}
                    {p.opening_hours && <p className="mt-0.5 text-xs text-slate-400">{p.opening_hours}</p>}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-500">{p.distance_km} km</span>
                    {p.phone && (
                      <a href={`tel:${p.phone}`}><Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button></a>
                    )}
                  </div>
                </div>
              </Card>
            ))
          )}

          <DisclaimerNote>
            Location results are sample development data unless a map provider is configured.
            Always verify a provider&apos;s details directly before seeking care.
          </DisclaimerNote>
        </div>
      )}
    </>
  );
}

function DoctorForm({ onSaved }: { onSaved: () => void }) {
  const [name, setName] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [clinic, setClinic] = useState("");
  const [phone, setPhone] = useState("");
  const [familyDoctor, setFamilyDoctor] = useState(false);
  const [error, setError] = useState("");

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/doctors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          doctor_name: name,
          specialty: specialty || null,
          clinic: clinic || null,
          phone: phone || null,
          is_family_doctor: familyDoctor,
        }),
      });
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save doctor");
    }
  }

  return (
    <form onSubmit={save} className="space-y-4">
      {error && <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      <Input id="dn" label="Name" value={name} onChange={(e) => setName(e.target.value)}
             placeholder="Dr.…" required />
      <div>
        <label htmlFor="ds" className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-400">Specialty</label>
        <select id="ds" value={specialty} onChange={(e) => setSpecialty(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
          <option value="">— optional —</option>
          {SPECIALTIES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <Input id="dc" label="Clinic / hospital (optional)" value={clinic}
             onChange={(e) => setClinic(e.target.value)} />
      <Input id="dp" label="Phone (optional)" type="tel" value={phone}
             onChange={(e) => setPhone(e.target.value)} placeholder="+91…" />
      <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
        <input type="checkbox" checked={familyDoctor} onChange={(e) => setFamilyDoctor(e.target.checked)}
               className="h-4 w-4 rounded border-slate-300" />
        Set as my family doctor
      </label>
      <Button type="submit" className="w-full">Save doctor</Button>
    </form>
  );
}
