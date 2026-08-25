"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Button, Card, DisclaimerNote, Input, PageHeader } from "@/components/ui";

interface Lifestyle {
  activity_level: string | null; sleep_goal_hours: number | null; diet_type: string | null;
  goal: string | null; smoking_status: string | null; stress_level: string | null;
}
interface ExerciseRow { id: number; activity: string; duration_minutes: number; performed_on: string }
interface SleepRow { id: number; hours: number; quality: string | null; logged_on: string }
interface Plan { plan: { day: string; activity: string }[]; estimated_weekly_minutes: number; guideline_note: string; caution_note: string | null }
interface Nutrition { notes: string[]; substitutions: { instead_of: string; try: string }[]; disclaimer: string }

export default function LifestylePage() {
  const qc = useQueryClient();
  const profile = useQuery<Lifestyle>({ queryKey: ["lifestyle"], queryFn: () => api("/lifestyle") });
  const exercise = useQuery<ExerciseRow[]>({ queryKey: ["exercise"], queryFn: () => api("/lifestyle/exercise?limit=10") });
  const sleep = useQuery<SleepRow[]>({ queryKey: ["sleep"], queryFn: () => api("/lifestyle/sleep?limit=10") });
  const plan = useQuery<Plan>({ queryKey: ["weekly-plan"], queryFn: () => api("/lifestyle/weekly-plan") });
  const nutrition = useQuery<Nutrition>({ queryKey: ["nutrition"], queryFn: () => api("/lifestyle/nutrition-guidance") });

  const [activity, setActivity] = useState("");
  const [minutes, setMinutes] = useState("30");
  const [sleepHours, setSleepHours] = useState("");
  const [form, setForm] = useState<Partial<Lifestyle>>({});

  async function saveProfile() {
    await api("/lifestyle", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        sleep_goal_hours: form.sleep_goal_hours ? Number(form.sleep_goal_hours) : undefined,
      }),
    });
    qc.invalidateQueries({ queryKey: ["lifestyle"] });
    qc.invalidateQueries({ queryKey: ["weekly-plan"] });
    qc.invalidateQueries({ queryKey: ["nutrition"] });
  }

  async function logExercise(e: React.FormEvent) {
    e.preventDefault();
    if (!activity.trim()) return;
    await api("/lifestyle/exercise", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ activity: activity.trim(), duration_minutes: Number(minutes), performed_on: new Date().toISOString().slice(0, 10) }),
    });
    setActivity(""); setMinutes("30");
    qc.invalidateQueries({ queryKey: ["exercise"] });
  }

  async function logSleep(e: React.FormEvent) {
    e.preventDefault();
    if (!sleepHours) return;
    await api("/lifestyle/sleep", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ hours: Number(sleepHours), logged_on: new Date().toISOString().slice(0, 10) }),
    });
    setSleepHours("");
    qc.invalidateQueries({ queryKey: ["sleep"] });
  }

  return (
    <>
      <PageHeader title="Lifestyle" subtitle="General wellness guidance — separated from medical care by design" />

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Your weekly movement plan">
          {!plan.data ? <p className="text-sm text-slate-400">Loading…</p> : (
            <>
              <ul className="divide-y divide-slate-100">
                {plan.data.plan.map((p) => (
                  <li key={p.day} className="flex items-center justify-between py-2 text-sm">
                    <span className="font-medium text-slate-700">{p.day}</span>
                    <span className="text-slate-600">{p.activity}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs leading-relaxed text-slate-500">
                ≈{plan.data.estimated_weekly_minutes} min/week · {plan.data.guideline_note}
              </p>
              {plan.data.caution_note && (
                <p role="note" className="mt-2 rounded-lg bg-amber-50 p-3 text-xs font-medium text-amber-800">
                  ⚠ {plan.data.caution_note}
                </p>
              )}
            </>
          )}
        </Card>

        <Card title="Nutrition guidance">
          {!nutrition.data ? <p className="text-sm text-slate-400">Loading…</p> : (
            <>
              <ul className="list-disc space-y-1.5 pl-5 text-sm leading-relaxed text-slate-600">
                {nutrition.data.notes.map((n, i) => <li key={i}>{n}</li>)}
              </ul>
              <h3 className="mt-4 mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">Simple swaps</h3>
              <ul className="space-y-1.5">
                {nutrition.data.substitutions.map((s) => (
                  <li key={s.instead_of} className="rounded-lg bg-slate-50 px-3 py-2 text-xs">
                    Instead of <strong>{s.instead_of}</strong> → try <strong>{s.try}</strong>
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-[11px] leading-relaxed text-slate-400">{nutrition.data.disclaimer}</p>
            </>
          )}
        </Card>

        <Card title="Log today's activity">
          <form onSubmit={logExercise} className="flex flex-wrap items-end gap-2">
            <div className="min-w-[8rem] flex-1"><Input id="ex-a" label="Activity" value={activity} onChange={(e) => setActivity(e.target.value)} placeholder="Walking…" /></div>
            <div className="w-24"><Input id="ex-m" label="Minutes" inputMode="numeric" value={minutes} onChange={(e) => setMinutes(e.target.value)} /></div>
            <Button type="submit" variant="secondary">Log</Button>
          </form>
          {!!exercise.data?.length && (
            <ul className="mt-3 space-y-1.5 text-sm">
              {exercise.data.slice(0, 5).map((x) => (
                <li key={x.id} className="flex justify-between rounded bg-slate-50 px-3 py-1.5">
                  <span>{x.activity}</span><span className="text-slate-500">{x.duration_minutes} min</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Log sleep">
          <form onSubmit={logSleep} className="flex items-end gap-2">
            <div className="flex-1"><Input id="sl-h" label="Hours slept last night" type="number" step="0.5" value={sleepHours} onChange={(e) => setSleepHours(e.target.value)} /></div>
            <Button type="submit" variant="secondary">Log</Button>
          </form>
          {!!sleep.data?.length && (
            <ul className="mt-3 space-y-1.5 text-sm">
              {sleep.data.slice(0, 5).map((s) => (
                <li key={s.id} className="flex justify-between rounded bg-slate-50 px-3 py-1.5">
                  <span>{new Date(s.logged_on).toLocaleDateString()}</span><span className="text-slate-500">{s.hours} h{s.quality && ` · ${s.quality}`}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Preferences & goals" className="lg:col-span-2">
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <label htmlFor="act" className="text-sm font-medium text-slate-700">Activity level
              <select id="act" defaultValue={profile.data?.activity_level ?? ""} onChange={(e) => setForm((f) => ({ ...f, activity_level: e.target.value || null }))} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm capitalize">
                <option value="">—</option>
                {["sedentary", "light", "moderate", "active", "athlete"].map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            </label>
            <Input id="goal-h" label="Sleep goal (hours)" type="number" step="0.5"
                   defaultValue={profile.data?.sleep_goal_hours ?? 8}
                   onChange={(e) => setForm((f) => ({ ...f, sleep_goal_hours: Number(e.target.value) }))} />
            <label htmlFor="diet-t" className="text-sm font-medium text-slate-700">Diet type
              <select id="diet-t" defaultValue={profile.data?.diet_type ?? ""} onChange={(e) => setForm((f) => ({ ...f, diet_type: e.target.value || null }))} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm capitalize">
                <option value="">—</option>
                {["vegetarian", "vegan", "eggetarian", "non_vegetarian", "other"].map((v) => <option key={v} value={v}>{v.replace("_", " ")}</option>)}
              </select>
            </label>
            <label htmlFor="life-goal" className="text-sm font-medium text-slate-700">Goal
              <select id="life-goal" defaultValue={profile.data?.goal ?? ""} onChange={(e) => setForm((f) => ({ ...f, goal: e.target.value || null }))} className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm capitalize">
                <option value="">—</option>
                {["maintain", "lose_weight", "gain_muscle", "improve_fitness"].map((v) => <option key={v} value={v}>{v.replace("_", " ")}</option>)}
              </select>
            </label>
          </div>
          <div className="mt-4 flex justify-end">
            <Button onClick={saveProfile}>Save preferences</Button>
          </div>
          <div className="mt-4"><DisclaimerNote>
            All lifestyle guidance here is general wellness information for healthy adults — it is
            not medical treatment and does not replace advice from your doctor or a registered dietitian.
          </DisclaimerNote></div>
        </Card>
      </div>
    </>
  );
}
