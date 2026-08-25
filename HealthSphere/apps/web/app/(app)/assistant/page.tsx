"use client";

import { useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { Badge, Button, DisclaimerNote, Input, PageHeader } from "@/components/ui";

interface Message {
  role: "user" | "assistant";
  content: string;
  safetyFiltered?: boolean;
}

const STARTERS = [
  "What do common preventive checkups include?",
  "Explain what HbA1c measures in simple words.",
  "How much daily activity is generally recommended?",
];

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const health = useQuery<{ metrics: { metric_key: string; display_name: string; value: number; secondary_value: number | null; unit: string | null; recorded_at: string }[] }>({
    queryKey: ["metrics-summary"],
    queryFn: () => api("/health-metrics/summary"),
  });

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  async function send(text?: string) {
    const content = (text ?? input).trim();
    if (!content || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content }]);
    setBusy(true);
    try {
      const res = await api<{ reply: string; safety_filtered?: boolean }>("/assistant/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: content }),
      });
      setMessages((m) => [...m, {
        role: "assistant",
        content: res.reply,
        safetyFiltered: res.safety_filtered ?? false,
      }]);
    } catch {
      setMessages((m) => [...m, { role: "assistant", content: "The assistant is unavailable right now. Please try again later." }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <PageHeader title="Health Assistant"
                  subtitle="General health education only — it cannot diagnose, prescribe, or read your reports" />

      <div className="mx-auto flex max-w-2xl flex-col rounded-xl border border-slate-200 bg-white shadow-sm" style={{ height: "70vh" }}>
        <div aria-live="polite" className="flex-1 space-y-3 overflow-y-auto p-4">
          {!messages.length && (
            <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
              <p className="text-sm text-slate-400">Ask a general health question to begin.</p>
              <div className="flex flex-wrap justify-center gap-2">
                {STARTERS.map((s) => (
                  <button key={s} onClick={() => send(s)}
                          className="rounded-full bg-brand-50 px-3 py-1.5 text-xs font-medium text-brand-800 hover:bg-brand-100">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-brand-600 text-white"
                  : msg.safetyFiltered ? "border border-red-200 bg-red-50 text-red-900" : "bg-slate-100 text-slate-800"
              }`}>
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {busy && <div className="text-xs text-slate-400">Assistant is thinking…</div>}
          <div ref={endRef} />
        </div>

        <form onSubmit={(e) => { e.preventDefault(); send(); }}
              className="flex gap-2 border-t border-slate-100 p-3">
          <Input id="chat-in" label="" value={input} onChange={(e) => setInput(e.target.value)}
                 placeholder="Ask about general health topics…" disabled={busy} wrapperClassName="flex-1" />
          <Button type="submit" disabled={busy || !input.trim()}>Send</Button>
        </form>
      </div>

      <div className="mx-auto mt-4 max-w-2xl space-y-3">
        {!!health.data?.metrics.length && (
          <div className="rounded-xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Context shared with the assistant</p>
            <ul className="mt-2 flex flex-wrap gap-1.5">
              {health.data.metrics.slice(0, 8).map((m) => (
                <li key={m.metric_key} className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] text-slate-600">
                  latest {m.display_name.toLowerCase()}: {m.value}{m.secondary_value != null && `/${m.secondary_value}`}{m.unit ?? ""}
                </li>
              ))}
            </ul>
          </div>
        )}
        <DisclaimerNote>
          The assistant gives general educational information with cited public-health sources. It will
          refuse diagnosis, medication advice, and report interpretation, and will point you to
          emergency services when messages suggest danger.
        </DisclaimerNote>
      </div>
    </>
  );
}
