"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import {
  Badge,
  Button,
  Card,
  DisclaimerNote,
  EmptyState,
  ErrorBanner,
  Input,
  Modal,
  PageHeader,
  Select,
  Textarea,
} from "@/components/ui";

interface Specialty { id: number; key: string; name: string }
interface SymptomCat { id: number; key: string; name: string; category: string | null }
interface Doctor {
  id: number; doctor_name: string; specialty: string | null;
  clinic: string | null; phone: string | null; email?: string | null;
  address?: string | null; notes?: string | null; is_family_doctor: boolean;
}
interface UserSymptom {
  id: number; symptom_name: string; duration_text: string | null;
  severity: string; notes: string | null;
}
interface Rec {
  id: number; specialty_name: string; relevance: string; reason: string;
  status: string; created_at: string; source_rules: string[];
}
interface AnalyzeResult {
  red_flag: boolean; matched_indicator?: string | null; message?: string | null;
  insufficient_info?: boolean; recommendations: Rec[];
  family_doctor: { id: number; doctor_name: string; specialty: string | null;
    clinic: string | null; phone: string | null } | null;
}
interface Place {
  name: string; kind: string; address: string | null; phone: string | null;
  distance_km: number; opening_hours: string | null;
}

const TABS = [
  ["doctors", "My Doctors"],
  ["symptoms", "Symptoms"],
  ["suggestions", "Specialist Suggestions"],
  ["find", "Find Doctors"],
  ["nearby", "Nearby Healthcare"],
] as const;
type TabKey = (typeof TABS)[number][0];

export default function DoctorsPage() {
  const [tab, setTab] = useState<TabKey>("doctors");
  const qc = useQueryClient();

  useEffect(() => {
    const t = new URLSearchParams(window.location.search).get("tab");
    if (t && TABS.some(([k]) => k === t)) setTab(t as TabKey);
  }, []);

  function goto(t: TabKey) { setTab(t); }

  return (
    <>
      <PageHeader
        title="Doctor & Specialist"
        subtitle="Your care team, symptoms and guidance on which specialist to discuss concerns with"
      />

      <DisclaimerNote>
        This section offers healthcare navigation support only. Suggestions are
        topics to discuss with a qualified healthcare professional — never a
        diagnosis, referral or prescription.
      </DisclaimerNote>

      <div className="mb-5 flex flex-wrap gap-2">
        {TABS.map(([value, label]) => (
          <button key={value} onClick={() => setTab(value)}
                  className={`rounded-full px-4 py-1.5 text-sm font-semibold ${
                    tab === value ? "bg-brand-600 text-white" : "bg-white text-slate-600 ring-1 ring-slate-200 hover:bg-slate-50"
                  }`}>
            {label}
          </button>
        ))}
      </div>

      {tab === "doctors" && <MyDoctorsTab onGoto={goto} onChanged={() => qc.invalidateQueries({ queryKey: ["doctors"] })} />}
      {tab === "symptoms" && <SymptomsTab />}
      {tab === "suggestions" && <SuggestionsTab onGoto={goto} />}
      {tab === "find" && <FindDoctorsTab />}
      {tab === "nearby" && <NearbyTab />}
    </>
  );
}

/* ============================ My Doctors ============================ */

function MyDoctorsTab({ onGoto, onChanged }: { onGoto: (t: TabKey) => void; onChanged: () => void }) {
  const [addOpen, setAddOpen] = useState(false);
  const [editDoc, setEditDoc] = useState<Doctor | null>(null);
  const doctors = useQuery<Doctor[]>({ queryKey: ["doctors"], queryFn: () => api("/doctors") });

  const family = doctors.data?.find((d) => d.is_family_doctor);
  const others = doctors.data?.filter((d) => !d.is_family_doctor) ?? [];

  async function toggleFamily(d: Doctor) {
    await api(`/doctors/${d.id}/family-doctor`, { method: "POST" });
    onChanged();
  }
  async function removeDoctor(id: number) {
    await api(`/doctors/${id}`, { method: "DELETE" });
    onChanged();
  }

  return (
    <>
      {family && (
        <Card className="mb-4 !bg-brand-50">
          <p className="text-xs font-bold uppercase tracking-wide text-brand-700">My family doctor</p>
          <div className="mt-1 flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-bold text-slate-900">{family.doctor_name}</h2>
              <p className="text-sm text-brand-700">{family.specialty ?? "Family Physician"}{family.clinic ? ` — ${family.clinic}` : ""}</p>
            </div>
            <div className="flex gap-2">
              {family.phone && (
                <a href={`tel:${family.phone}`}><Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button></a>
              )}
              <Button variant="secondary" className="!px-3 !py-1 !text-xs"
                      onClick={() => toggleFamily(family)}>
                Remove as Family Doctor
              </Button>
            </div>
          </div>
        </Card>
      )}

      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-slate-500">Doctors you actually visit — used for follow-ups and emergency context.</p>
        <Button onClick={() => setAddOpen(true)}>Add doctor</Button>
      </div>

      {!doctors.data?.length && !doctors.isLoading ? (
        <EmptyState message="No doctors in your care team yet."
                    hint="Add your family doctor or specialists you see regularly." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {[...others].map((d) => (
            <Card key={d.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="font-bold text-slate-900">{d.doctor_name}</h2>
                  {d.specialty && <p className="text-sm font-medium text-brand-700">{d.specialty}</p>}
                  <dl className="mt-2 space-y-0.5 text-xs text-slate-600">
                    {d.clinic && <dd>{d.clinic}</dd>}
                    {d.phone && <dd className="font-mono">{d.phone}</dd>}
                    {d.email && <dd>{d.email}</dd>}
                    {d.address && <dd>{d.address}</dd>}
                    {d.notes && <dd className="italic text-slate-400">{d.notes}</dd>}
                  </dl>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1.5">
                  {d.phone && (
                    <a href={`tel:${d.phone}`}>
                      <Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button>
                    </a>
                  )}
                  <button onClick={() => setEditDoc(d)}
                          className="text-xs font-medium text-brand-700 hover:underline">Edit</button>
                  <button onClick={() => toggleFamily(d)}
                          className="text-xs font-medium text-slate-500 hover:underline">
                    Mark as Family Doctor
                  </button>
                  <button onClick={() => removeDoctor(d.id)}
                          className="text-xs font-medium text-red-600 hover:underline">Delete</button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add a doctor to your care team">
        <DoctorForm specialtiesQuery={() => api<Specialty[]>("/specialties")}
                    onSaved={() => { setAddOpen(false); onChanged(); }} />
      </Modal>
      <Modal open={!!editDoc} onClose={() => setEditDoc(null)} title={`Edit ${editDoc?.doctor_name ?? ""}`}>
        {editDoc && (
          <DoctorForm specialtiesQuery={() => api<Specialty[]>("/specialties")} initial={editDoc}
                      onSaved={() => { setEditDoc(null); onChanged(); }} />
        )}
      </Modal>

      {!family && doctors.data?.length ? (
        <button onClick={() => onGoto("symptoms")}
                className="mt-4 text-sm font-medium text-brand-700 hover:underline">
          Next: record your symptoms →
        </button>
      ) : null}
    </>
  );
}

function DoctorForm({ specialtiesQuery, initial, onSaved }:
                    { specialtiesQuery: () => Promise<Specialty[]>; initial?: Doctor; onSaved: () => void }) {
  const [name, setName] = useState(initial?.doctor_name ?? "");
  const [specialty, setSpecialty] = useState(initial?.specialty ?? "");
  const [clinic, setClinic] = useState(initial?.clinic ?? "");
  const [phone, setPhone] = useState(initial?.phone ?? "");
  const [email, setEmail] = useState(initial?.email ?? "");
  const [address, setAddress] = useState(initial?.address ?? "");
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [familyDoctor, setFamilyDoctor] = useState(initial?.is_family_doctor ?? false);
  const [error, setError] = useState("");
  const specialties = useQuery<Specialty[]>({ queryKey: ["specialties"], queryFn: specialtiesQuery });

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const body = JSON.stringify({
        doctor_name: name,
        specialty: specialty || null,
        clinic: clinic || null,
        phone: phone || null,
        email: email || null,
        address: address || null,
        notes: notes || null,
        is_family_doctor: familyDoctor,
      });
      await api(initial ? `/doctors/${initial.id}` : "/doctors", {
        method: initial ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body,
      });
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save doctor");
    }
  }

  return (
    <form onSubmit={save} className="space-y-4">
      {error && <ErrorBanner message={error} />}
      <Input id="dn" label="Name" value={name} onChange={(e) => setName(e.target.value)} placeholder="Dr.…" required />
      <Select id="ds" label="Specialty" value={specialty} onChange={(e) => setSpecialty(e.target.value)}>
        <option value="">— optional —</option>
        {(specialties.data ?? []).map((s) => <option key={s.key} value={s.name}>{s.name}</option>)}
      </Select>
      <Input id="dc" label="Clinic / hospital (optional)" value={clinic} onChange={(e) => setClinic(e.target.value)} />
      <Input id="dp" label="Phone (optional)" type="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91…" />
      <Input id="de" label="Email (optional)" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
      <Input id="da" label="Address (optional)" value={address} onChange={(e) => setAddress(e.target.value)} />
      <Textarea id="dno" label="Notes (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} />
      <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-700">
        <input type="checkbox" checked={familyDoctor} onChange={(e) => setFamilyDoctor(e.target.checked)}
               className="h-4 w-4 rounded border-slate-300" />
        Set as my family doctor
      </label>
      <Button type="submit" className="w-full">Save doctor</Button>
    </form>
  );
}

/* ============================== Symptoms ============================== */

function SymptomsTab() {
  const qc = useQueryClient();
  const [q, setQ] = useState("");
  const [selected, setSelected] = useState<SymptomCat | null>(null);
  const [duration, setDuration] = useState("");
  const [severity, setSeverity] = useState("moderate");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");

  const catalog = useQuery<SymptomCat[]>({
    queryKey: ["symptom-catalog", q],
    queryFn: () => api(`/symptoms?q=${encodeURIComponent(q)}`),
  });
  const mine = useQuery<UserSymptom[]>({ queryKey: ["user-symptoms"], queryFn: () => api("/user/symptoms") });

  async function add(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!selected && !q.trim()) { setError("Search for and select a symptom first."); return; }
    try {
      await api("/user/symptoms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symptom_id: selected?.id ?? undefined,
          symptom_name: selected ? undefined : q.trim(),
          duration_text: duration || undefined,
          severity,
          notes: notes || undefined,
        }),
      });
      setSelected(null); setQ(""); setDuration(""); setSeverity("moderate"); setNotes("");
      qc.invalidateQueries({ queryKey: ["user-symptoms"] });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save symptom");
    }
  }

  async function remove(id: number) {
    await api(`/user/symptoms/${id}`, { method: "DELETE" });
    qc.invalidateQueries({ queryKey: ["user-symptoms"] });
  }

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <h2 className="font-bold text-slate-900">Report a symptom</h2>
        <form onSubmit={add} className="mt-3 space-y-3">
          {error && <ErrorBanner message={error} />}
          <Input id="sq" label="Search symptoms" value={q} onChange={(e) => { setQ(e.target.value); setSelected(null); }}
                 placeholder="e.g. joint pain" />
          {q && !selected && (
            <ul className="max-h-40 divide-y divide-slate-100 overflow-y-auto rounded-lg ring-1 ring-slate-200">
              {(catalog.data ?? []).map((s) => (
                <li key={s.id}>
                  <button type="button" onClick={() => setSelected(s)}
                          className="w-full px-3 py-2 text-left text-sm hover:bg-brand-50">
                    {s.name} <span className="text-xs text-slate-400">{s.category}</span>
                  </button>
                </li>
              ))}
              {q.trim() && !(catalog.data ?? []).some((c) => c.name.toLowerCase() === q.trim().toLowerCase()) && (
                <li className="px-3 py-2 text-xs text-slate-400">
                  No catalog match — press “Add” to record “{q.trim()}” as written.
                </li>
              )}
            </ul>
          )}
          {selected && (
            <Badge tone="brand">Selected: {selected.name}</Badge>
          )}
          <Input id="sdur" label="Duration (e.g. 3 weeks)" value={duration} onChange={(e) => setDuration(e.target.value)} />
          <Select id="ssev" label="Severity" value={severity} onChange={(e) => setSeverity(e.target.value)}>
            <option value="mild">Mild</option>
            <option value="moderate">Moderate</option>
            <option value="severe">Severe</option>
          </Select>
          <Textarea id="snotes" label="Notes (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} />
          <Button type="submit" className="w-full">Add symptom</Button>
        </form>
      </Card>

      <div className="space-y-4">
        <h2 className="font-bold text-slate-900">Your recorded symptoms</h2>
        {!mine.data?.length ? (
          <EmptyState message="No symptoms recorded yet."
                      hint="Recorded symptoms feed the Specialist Suggestions engine." />
        ) : (
          mine.data.map((s) => (
            <Card key={s.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-slate-900">{s.symptom_name}</h3>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {s.duration_text ? `${s.duration_text} · ` : ""}<Badge tone={s.severity === "severe" ? "red" : s.severity === "mild" ? "slate" : "amber"}>{s.severity}</Badge>
                  </p>
                  {s.notes && <p className="mt-1 text-xs italic text-slate-400">{s.notes}</p>}
                </div>
                <button onClick={() => remove(s.id)}
                        className="text-xs font-medium text-red-600 hover:underline">Remove</button>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}

/* ======================== Specialist Suggestions ======================== */

function SuggestionsTab({ onGoto }: { onGoto: (t: TabKey) => void }) {
  const qc = useQueryClient();
  const history = useQuery<Rec[]>({
    queryKey: ["spec-recs"], queryFn: () => api("/specialist-recommendations") });
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [busy, setBusy] = useState(false);

  async function analyze() {
    setBusy(true);
    try {
      const data = await api<AnalyzeResult>("/specialist-recommendations/analyze", { method: "POST" });
      setResult(data);
      qc.invalidateQueries({ queryKey: ["spec-recs"] });
      qc.invalidateQueries({ queryKey: ["timeline"] });
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-slate-500">
          Combines your symptoms, conditions, reports, trends and family history.
        </p>
        <Button onClick={analyze} disabled={busy}>{busy ? "Analyzing…" : "Analyze my information"}</Button>
      </div>

      {result?.red_flag && (
        <Card className="!border-red-300 !bg-red-50">
          <Badge tone="red">Emergency</Badge>
          <h2 className="mt-2 whitespace-pre-line font-bold text-red-800">{result.message}</h2>
          <div className="mt-3 flex flex-wrap gap-2">
            <a href="tel:108"><Button className="!bg-red-600">Call Emergency (108)</Button></a>
            <Button variant="secondary" onClick={() => onGoto("contacts")}>Emergency Contacts</Button>
            <Button variant="secondary" onClick={() => onGoto("nearby")}>Nearby Hospital</Button>
          </div>
        </Card>
      )}

      {result?.insufficient_info && (
        <EmptyState message={result.message ?? "Insufficient information for a personalized specialist suggestion."}
                    hint="Consider starting with a primary-care physician if you have a health concern." />
      )}

      {result && !result.red_flag && result.recommendations.map((rec, i) => (
        <SuggestionCard key={rec.id} rec={rec} rank={i + 1} familyDoctor={result.family_doctor} onGoto={onGoto} />
      ))}

      {result && !result.red_flag && result.family_doctor && (
        <Card className="!bg-brand-50">
          <p className="text-xs font-bold uppercase tracking-wide text-brand-700">Recommended first step</p>
          <p className="mt-1 text-sm text-slate-700">
            Discuss this concern with your Family Doctor, {result.family_doctor.doctor_name}.
          </p>
          <div className="mt-2 flex gap-2">
            <Button variant="secondary" className="!px-3 !py-1 !text-xs" onClick={() => onGoto("doctors")}>View Family Doctor</Button>
            {result.family_doctor.phone && (
              <a href={`tel:${result.family_doctor.phone}`}>
                <Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button>
              </a>
            )}
          </div>
        </Card>
      )}

      {!result && !!history.data?.length && (
        <div className="space-y-4">
          <h2 className="font-bold text-slate-900">Previous suggestions</h2>
          {history.data.slice(0, 6).map((rec) => (
            <SuggestionCard key={rec.id} rec={rec} onGoto={onGoto} />
          ))}
        </div>
      )}

      {!result && !history.data?.length && !history.isLoading && (
        <EmptyState message="No suggestions yet."
                    hint="Record symptoms and conditions, then run the analysis above." />
      )}
    </>
  );
}

function SuggestionCard({ rec, rank, familyDoctor, onGoto }:
  { rec: Rec; rank?: number; familyDoctor?: AnalyzeResult["family_doctor"]; onGoto: (t: TabKey) => void }) {
  const [aiReply, setAiReply] = useState("");
  const [asking, setAsking] = useState(false);
  const [remindOpen, setRemindOpen] = useState(false);
  const [when, setWhen] = useState("tomorrow");
  const [customAt, setCustomAt] = useState("");
  const [remindMsg, setRemindMsg] = useState("");

  async function askAi() {
    setAsking(true); setAiReply("");
    try {
      const r = await api<{ reply: string }>("/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: `Why was ${rec.specialty_name} suggested?` }),
      });
      setAiReply(r.reply);
    } finally {
      setAsking(false);
    }
  }

  async function remindMe(e: React.FormEvent) {
    e.preventDefault();
    setRemindMsg("");
    try {
      await api(`/specialist-recommendations/${rec.id}/remind`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(
          when === "custom" ? { when, custom_at: new Date(customAt).toISOString() } : { when },
        ),
      });
      setRemindMsg("Reminder saved.");
      setRemindOpen(false);
    } catch (err) {
      setRemindMsg(err instanceof Error ? err.message : "Could not save reminder");
    }
  }

  const tone = rec.relevance === "high" ? "brand" : rec.relevance === "medium" ? "amber" : "slate";

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="flex items-center gap-2 font-bold text-slate-900">
            {rank && <span className="text-slate-400">#{rank}</span>} 🩺 {rec.specialty_name}
            <Badge tone={tone as "brand"}>{rec.relevance} relevance</Badge>
          </h3>
        </div>
      </div>
      <details className="mt-2">
        <summary className="cursor-pointer text-sm font-semibold text-brand-700">Why?</summary>
        <p className="mt-1 text-sm text-slate-600">{rec.reason}</p>
      </details>
      <p className="mt-2 text-xs text-slate-500">
        Suggested next step: discuss this with a qualified healthcare professional.
        {familyDoctor && " Your Family Doctor may be a good first point of discussion."}
      </p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button variant="secondary" className="!px-3 !py-1 !text-xs" onClick={() => onGoto("find")}>Find Doctors</Button>
        <Button variant="secondary" className="!px-3 !py-1 !text-xs" onClick={() => onGoto("nearby")}>Nearby Hospitals</Button>
        <Button variant="secondary" className="!px-3 !py-1 !text-xs" onClick={askAi} disabled={asking}>
          {asking ? "Asking…" : "Ask AI Why?"}
        </Button>
        <Button variant="secondary" className="!px-3 !py-1 !text-xs" onClick={() => setRemindOpen(!remindOpen)}>Remind Me</Button>
      </div>
      {remindOpen && (
        <form onSubmit={remindMe} className="mt-3 flex flex-wrap items-end gap-2 rounded-lg bg-slate-50 p-3">
          <Select id={`rw-${rec.id}`} label="When" value={when} onChange={(e) => setWhen(e.target.value)}>
            <option value="tomorrow">Tomorrow</option>
            <option value="in_3_days">In 3 days</option>
            <option value="next_week">Next week</option>
            <option value="custom">Custom</option>
          </Select>
          {when === "custom" && (
            <Input id={`rc-${rec.id}`} label="Date & time" type="datetime-local" value={customAt}
                   onChange={(e) => setCustomAt(e.target.value)} required />
          )}
          <Button type="submit" className="!px-3 !py-1.5 !text-xs">Save reminder</Button>
        </form>
      )}
      {remindMsg && <p className="mt-2 text-xs font-medium text-brand-700">{remindMsg}</p>}
      {aiReply && (
        <div className="mt-3 rounded-lg bg-slate-50 p-3 text-sm whitespace-pre-line text-slate-700">{aiReply}</div>
      )}
    </Card>
  );
}

/* ============================ Find Doctors ============================ */

function FindDoctorsTab() {
  const specialties = useQuery<Specialty[]>({ queryKey: ["specialties"], queryFn: () => api("/specialties") });
  const [specialty, setSpecialty] = useState("");
  const [q, setQ] = useState("");
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null);

  const params = new URLSearchParams();
  if (specialty) params.set("specialty", specialty);
  if (q) params.set("q", q);
  if (coords) { params.set("lat", String(coords.lat)); params.set("lon", String(coords.lon)); }
  const search = useQuery<{
    my_doctors: Array<{ id: number; doctor_name: string; specialty: string | null; clinic: string | null; phone: string | null; is_family_doctor: boolean }>;
    facilities: Place[];
  }>({
    queryKey: ["doctor-search", specialty, q, coords],
    queryFn: () => api(`/doctors/search?${params.toString()}`),
    enabled: !!specialty || !!q,
  });

  function locate() {
    navigator.geolocation?.getCurrentPosition(
      (p) => setCoords({ lat: Number(p.coords.latitude.toFixed(4)), lon: Number(p.coords.longitude.toFixed(4)) }),
      () => alert("Location access is required to sort nearby facilities."),
      { timeout: 8000 },
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <div className="grid gap-3 sm:grid-cols-3">
          <Select id="fspec" label="Specialty" value={specialty} onChange={(e) => setSpecialty(e.target.value)}>
            <option value="">Any specialty</option>
            {(specialties.data ?? []).map((s) => <option key={s.key} value={s.name}>{s.name}</option>)}
          </Select>
          <Input id="fq" label="Name / clinic keyword" value={q} onChange={(e) => setQ(e.target.value)} />
          <div className="flex items-end">
            <Button variant="secondary" className="!px-3 !py-1.5 !text-xs" onClick={locate}>Use my location</Button>
          </div>
        </div>
      </Card>

      {search.isLoading && <p className="text-sm text-slate-400">Searching…</p>}

      {!!search.data?.my_doctors.length && (
        <div className="space-y-2">
          <h2 className="font-bold text-slate-900">From your care team</h2>
          {search.data.my_doctors.map((d) => (
            <Card key={d.id}>
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h3 className="font-semibold text-slate-900">{d.doctor_name}{d.is_family_doctor && <span className="ml-2"><Badge tone="brand">Family doctor</Badge></span>}</h3>
                  <p className="text-xs text-slate-500">{d.specialty}{d.clinic ? ` — ${d.clinic}` : ""}</p>
                </div>
                {d.phone && <a href={`tel:${d.phone}`}><Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button></a>}
              </div>
            </Card>
          ))}
        </div>
      )}

      {!!search.data?.facilities.length && (
        <div className="space-y-2">
          <h2 className="font-bold text-slate-900">Facilities</h2>
          {search.data.facilities.map((f) => (
            <Card key={`${f.kind}-${f.name}-${f.address ?? ""}`}>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold capitalize text-slate-900">{f.name} <Badge tone="slate">{f.kind}</Badge></h3>
                  {f.address && <p className="text-xs text-slate-500">{f.address}</p>}
                </div>
                <div className="flex items-center gap-2">
                  {typeof f.distance_km === "number" && <span className="text-xs font-semibold text-slate-500">{f.distance_km} km</span>}
                  {f.phone && <a href={`tel:${f.phone}`}><Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button></a>}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {(specialty || q) && !search.isLoading && !search.data?.my_doctors.length && !search.data?.facilities.length && (
        <EmptyState message="No matches in HealthSphere yet."
                    hint="Only records already in HealthSphere are searched — nothing is invented." />
      )}
      <DisclaimerNote>Search covers your own saved doctors and cached facility data only.</DisclaimerNote>
    </div>
  );
}

/* ========================== Nearby Healthcare ========================== */

function NearbyTab() {
  const KINDS = ["all", "hospital", "clinic", "lab", "pharmacy"];
  const [kind, setKind] = useState("all");
  const [coords, setCoords] = useState({ lat: 12.9716, lon: 77.5946 });
  const [denied, setDenied] = useState(false);

  const nearby = useQuery<{ results: Place[] }>({
    queryKey: ["nearby", kind, coords],
    queryFn: () => api(`/healthcare/nearby?lat=${coords.lat}&lon=${coords.lon}&kind=${kind}`),
  });

  function locate() {
    navigator.geolocation?.getCurrentPosition(
      (p) => { setDenied(false); setCoords({ lat: Number(p.coords.latitude.toFixed(4)), lon: Number(p.coords.longitude.toFixed(4)) }); },
      () => setDenied(true),
      { timeout: 8000 },
    );
  }

  return (
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
        <Button variant="secondary" className="ml-auto !px-3 !py-1.5 !text-xs" onClick={locate}>Use my location</Button>
      </div>

      {denied && <ErrorBanner message="Location access is required to find nearby healthcare facilities." />}

      {!nearby.data?.results.length && !nearby.isLoading ? (
        <EmptyState message="No places found." hint="Try widening the type filter or sharing your location." />
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
                {p.phone && <a href={`tel:${p.phone}`}><Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button></a>}
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
  );
}
