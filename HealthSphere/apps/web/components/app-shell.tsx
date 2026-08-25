"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-context";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: "◉" },
  { href: "/profile", label: "Profile", icon: "☺" },
  { href: "/family", label: "Family", icon: "👪" },
  { href: "/reports", label: "Reports", icon: "📄" },
  { href: "/health", label: "Health", icon: "📈" },
  { href: "/recommendations", label: "Insights", icon: "💡" },
  { href: "/lifestyle", label: "Lifestyle", icon: "🥗" },
  { href: "/assistant", label: "AI Assistant", icon: "💬" },
  { href: "/care", label: "Find Care", icon: "🩺" },
  { href: "/doctors", label: "Doctors", icon: "🏥" },
  { href: "/contacts", label: "Contacts", icon: "☎" },
  { href: "/settings", label: "Settings", icon: "⚙" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-500" role="status">Loading…</p>
      </div>
    );
  }
  if (!user) return null;

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="hidden w-60 shrink-0 flex-col border-r border-slate-200 bg-white lg:flex">
        <div className="px-5 py-5">
          <Link href="/dashboard" className="text-lg font-bold text-brand-800">
            Health<span className="text-brand-500">Sphere</span>
          </Link>
        </div>
        <nav aria-label="Main navigation" className="flex-1 space-y-0.5 overflow-y-auto px-3 pb-4">
          {NAV.map((item) => {
            const active = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "bg-brand-50 text-brand-800"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                <span aria-hidden="true">{item.icon}</span>
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-slate-200 p-3">
          <Link
            href="/emergency"
            className="mb-2 flex items-center justify-center gap-2 rounded-lg bg-red-600 px-3 py-2.5 text-sm font-bold text-white hover:bg-red-700"
          >
            ⨯ Emergency
          </Link>
          <button
            onClick={async () => {
              await logout();
              router.replace("/login");
            }}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-600 hover:bg-slate-100"
          >
            Log out ({user.email.split("@")[0]})
          </button>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Mobile top bar */}
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 lg:hidden">
          <Link href="/dashboard" className="font-bold text-brand-800">
            HealthSphere
          </Link>
          <div className="flex items-center gap-2">
            <Link
              href="/emergency"
              className="rounded-lg bg-red-600 px-3 py-1.5 text-xs font-bold text-white"
            >
              Emergency
            </Link>
            <select
              aria-label="Navigate to page"
              value=""
              onChange={(e) => e.target.value && router.push(e.target.value)}
              className="rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm"
            >
              <option value="" disabled>Menu…</option>
              {NAV.map((item) => (
                <option key={item.href} value={item.href}>{item.label}</option>
              ))}
            </select>
          </div>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-6">{children}</main>

        <footer className="border-t border-slate-200 px-6 py-3">
          <p className="text-xs text-slate-400">
            HealthSphere provides health-record management and general wellness information only.
            It does not diagnose conditions or replace professional medical advice.
          </p>
        </footer>
      </div>
    </div>
  );
}
