"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { api } from "@/lib/api";
import { Badge, Button, Card, EmptyState, Input, Modal, PageHeader } from "@/components/ui";

interface Contact {
  id: number; name: string; relationship: string;
  phone: string; priority: number; notes: string | null;
}

const RELATIONSHIPS = ["family", "friend", "neighbour", "doctor", "other"];

export default function ContactsPage() {
  const qc = useQueryClient();
  const [addOpen, setAddOpen] = useState(false);
  const contacts = useQuery<Contact[]>({
    queryKey: ["contacts"],
    queryFn: () => api("/emergency-contacts"),
  });

  async function remove(id: number) {
    await api(`/emergency-contacts/${id}`, { method: "DELETE" });
    qc.invalidateQueries({ queryKey: ["contacts"] });
  }

  async function makePrimary(c: Contact) {
    await api(`/emergency-contacts/${c.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: c.name, relationship: c.relationship, phone: c.phone, priority: 1 }),
    });
    qc.invalidateQueries({ queryKey: ["contacts"] });
  }

  return (
    <>
      <PageHeader
        title="Emergency Contacts"
        subtitle="People notified when you trigger an SOS alert — lower priority number is contacted first"
        action={<Button onClick={() => setAddOpen(true)}>Add contact</Button>}
      />

      {!contacts.data?.length ? (
        <EmptyState message="No emergency contacts saved."
                    hint="Add at least one trusted person so SOS alerts can reach someone." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {contacts.data.map((c) => (
            <Card key={c.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="flex items-center gap-2 font-bold text-slate-900">
                    {c.name}
                    {c.priority === 1 && <Badge tone="brand">Called first</Badge>}
                  </h2>
                  <p className="text-xs capitalize text-slate-500">{c.relationship}</p>
                  <p className="mt-2 font-mono text-sm text-slate-700">{c.phone}</p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <a href={`tel:${c.phone}`}><Button variant="secondary" className="!px-3 !py-1 !text-xs">Call</Button></a>
                  {c.priority !== 1 && (
                    <button onClick={() => makePrimary(c)}
                            className="text-xs font-medium text-brand-700 hover:underline">Move to first</button>
                  )}
                  <button onClick={() => remove(c.id)}
                          className="text-xs font-medium text-red-600 hover:underline">Remove</button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Modal open={addOpen} onClose={() => setAddOpen(false)} title="Add emergency contact">
        <ContactForm onSaved={() => { setAddOpen(false); qc.invalidateQueries({ queryKey: ["contacts"] }); }} />
      </Modal>
    </>
  );
}

function ContactForm({ onSaved }: { onSaved: () => void }) {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [relationship, setRelationship] = useState("family");
  const [priority, setPriority] = useState(2);
  const [error, setError] = useState("");

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await api("/emergency-contacts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, phone, relationship, priority }),
      });
      onSaved();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not save contact");
    }
  }

  return (
    <form onSubmit={save} className="space-y-4">
      {error && <p role="alert" className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
      <Input id="cn" label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <Input id="cp" label="Phone number" type="tel" value={phone}
             onChange={(e) => setPhone(e.target.value)} placeholder="+91…"
             pattern="\+?[0-9\s\-]{7,15}" required />
      <div>
        <label htmlFor="cr" className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-400">Relationship</label>
        <select id="cr" value={relationship} onChange={(e) => setRelationship(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
          {RELATIONSHIPS.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
      </div>
      <Input id="cq" label="Priority (1 = called first)" type="number" min={1} max={99} value={priority}
             onChange={(e) => setPriority(Number(e.target.value))} required />
      <Button type="submit" className="w-full">Save contact</Button>
    </form>
  );
}
