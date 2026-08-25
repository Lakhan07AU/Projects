"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { Button, DisclaimerNote, ErrorBanner, Input } from "@/components/ui";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [apiError, setApiError] = useState("");
  const [busy, setBusy] = useState(false);

  function validate() {
    const errs: Record<string, string> = {};
    if (!fullName.trim()) errs.fullName = "Please enter your name.";
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) errs.email = "Enter a valid email address.";
    if (password.length < 8) errs.password = "Password must be at least 8 characters.";
    if (password !== confirm) errs.confirm = "Passwords do not match.";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setApiError("");
    if (!validate()) return;
    setBusy(true);
    try {
      await register(email, password, fullName.trim());
      router.replace("/profile?welcome=1");
    } catch (err) {
      setApiError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <Link href="/" className="text-xl font-bold text-brand-800">
            Health<span className="text-brand-500">Sphere</span>
          </Link>
          <h1 className="mt-3 text-xl font-semibold">Create your account</h1>
        </div>

        <form onSubmit={onSubmit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          {apiError && <ErrorBanner message={apiError} />}
          <Input id="name" label="Full name" value={fullName}
                 onChange={(e) => setFullName(e.target.value)} error={errors.fullName} required />
          <Input id="email" label="Email" type="email" value={email}
                 onChange={(e) => setEmail(e.target.value)} error={errors.email} required />
          <Input id="password" label="Password (min 8 characters)" type="password" value={password}
                 onChange={(e) => setPassword(e.target.value)} error={errors.password} required minLength={8} />
          <Input id="confirm" label="Confirm password" type="password" value={confirm}
                 onChange={(e) => setConfirm(e.target.value)} error={errors.confirm} required />
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? "Creating account…" : "Create account"}
          </Button>
          <DisclaimerNote>
            Your health information is sensitive. HealthSphere stores it securely, never shares it
            without your explicit consent, and never uses it to diagnose conditions.
          </DisclaimerNote>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link href="/login" className="font-semibold text-brand-700 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
