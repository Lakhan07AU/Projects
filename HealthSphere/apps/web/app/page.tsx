"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-context";

const FEATURES = [
  ["📄", "Medical reports, organized", "Upload PDFs and images. Key values are extracted and explained in plain language."],
  ["📈", "Trends that matter", "See how your measurements change over time — manually entered or extracted from reports."],
  ["👪", "Family health history", "Record conditions across relatives to inform preventive-care discussions."],
  ["💡", "Preventive-care insights", "Guidance topics based on validated public-health rules — always for discussion with a professional."],
  ["🥗", "Lifestyle support", "General activity, sleep and nutrition guidance tuned to your preferences."],
  ["🚨", "Emergency-ready", "One screen with critical info: blood group, allergies, conditions, contacts."],
];

export default function LandingPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [loading, user, router]);

  return (
    <div className="min-h-screen">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <span className="text-xl font-bold text-brand-800">Health<span className="text-brand-500">Sphere</span></span>
        <div className="flex gap-2">
          <Link href="/login" className="rounded-lg px-4 py-2 text-sm font-semibold text-brand-700 hover:bg-brand-50">
            Log in
          </Link>
          <Link href="/register" className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">
            Get started
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-6 pb-16 pt-14 text-center">
        <h1 className="text-balance text-4xl font-extrabold tracking-tight text-slate-900 sm:text-5xl">
          Understand your history.<br />Track your health. <span className="text-brand-600">Act earlier.</span>
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-600">
          A continuously evolving digital health memory and preventive-care assistant for you
          and your family.
        </p>
        <Link
          href="/register"
          className="mt-8 inline-block rounded-xl bg-brand-600 px-8 py-3.5 text-base font-semibold text-white shadow hover:bg-brand-700"
        >
          Create your free account
        </Link>

        <p className="mx-auto mt-10 max-w-2xl rounded-xl border border-slate-200 bg-white px-5 py-4 text-sm text-slate-500">
          HealthSphere is a personal health-record manager and decision-support tool. It never
          diagnoses conditions or replaces advice from qualified healthcare professionals.
        </p>
      </section>

      <section className="border-t border-slate-200 bg-white py-16">
        <div className="mx-auto grid max-w-6xl gap-8 px-6 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(([icon, title, desc]) => (
            <div key={title} className="rounded-xl border border-slate-100 p-6 shadow-sm">
              <div aria-hidden="true" className="text-2xl">{icon}</div>
              <h3 className="mt-3 font-semibold text-slate-900">{title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
