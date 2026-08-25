"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { Button, ErrorBanner, Input } from "@/components/ui";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(email.trim().toLowerCase(), password);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
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
          <h1 className="mt-3 text-xl font-semibold">Welcome back</h1>
        </div>

        <form onSubmit={onSubmit} className="space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          {error && <ErrorBanner message={error} />}
          <Input id="email" label="Email" type="email" value={email}
                 onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
          <Input id="password" label="Password" type="password" value={password}
                 onChange={(e) => setPassword(e.target.value)} required autoComplete="current-password" />
          <Button type="submit" disabled={busy} className="w-full">
            {busy ? "Signing in…" : "Log in"}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-slate-500">
          New here?{" "}
          <Link href="/register" className="font-semibold text-brand-700 hover:underline">
            Create an account
          </Link>
        </p>
      </div>
    </div>
  );
}
