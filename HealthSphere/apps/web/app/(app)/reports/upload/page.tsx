"use client";

import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { apiUpload } from "@/lib/api";
import { Button, Card, DisclaimerNote, ErrorBanner, Input } from "@/components/ui";

const CATEGORIES = [
  ["other", "Other"], ["cbc", "CBC"], ["lipid_profile", "Lipid Profile"],
  ["hba1c", "HbA1c"], ["blood_glucose", "Blood Glucose"], ["thyroid", "Thyroid"],
  ["liver_function", "Liver Function"], ["kidney_function", "Kidney Function"],
  ["ecg", "ECG"], ["imaging", "Imaging Report"], ["prescription", "Prescription"],
  ["doctor_note", "Doctor Note"],
];

export default function UploadReportPage() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [category, setCategory] = useState("other");
  const [reportDate, setReportDate] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function accept(f: File | null | undefined) {
    if (!f) return;
    const ok = ["application/pdf", "image/jpeg", "image/png"].includes(f.type);
    if (!ok) {
      setError("Please choose a PDF, JPG or PNG file.");
      setFile(null);
      return;
    }
    if (f.size > 25 * 1024 * 1024) {
      setError("File exceeds the maximum size of 25 MB.");
      return;
    }
    setError("");
    setFile(f);
  }

  async function upload() {
    if (!file) return;
    setBusy(true); setError("");
    try {
      const query = `?category=${encodeURIComponent(category)}${reportDate ? `&report_date=${encodeURIComponent(reportDate)}` : ""}`;
      const report = await apiUpload<{ id: number }>("/reports", file, query);
      router.push(`/reports/${report.id}?fresh=1`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-2xl font-bold text-slate-900">Upload Medical Report</h1>
      <p className="mb-6 text-sm text-slate-500">
        PDF, JPG or PNG · up to 25 MB. Processing happens in the background.
      </p>

      {error && <div className="mb-4"><ErrorBanner message={error} /></div>}

      <div
        role="button"
        tabIndex={0}
        aria-label="Choose a file to upload"
        onClick={() => inputRef.current?.click()}
        onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => { e.preventDefault(); setDragging(false); accept(e.dataTransfer.files[0]); }}
        className={`flex min-h-[220px] cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-colors ${
          dragging ? "border-brand-500 bg-brand-50" : "border-slate-300 bg-white hover:border-brand-300"
        }`}
      >
        <input ref={inputRef} type="file" accept=".pdf,.jpg,.jpeg,.png" className="hidden"
               onChange={(e) => accept(e.target.files?.[0])} />
        {file ? (
          <>
            <p className="font-semibold text-slate-800">{file.name}</p>
            <p className="mt-1 text-xs text-slate-400">{(file.size / 1024).toFixed(0)} KB — click to change</p>
          </>
        ) : (
          <>
            <p aria-hidden="true" className="text-3xl">📤</p>
            <p className="mt-2 font-medium text-slate-700">Drag & drop your report here</p>
            <p className="mt-1 text-sm text-slate-400">or click to choose a file</p>
          </>
        )}
      </div>

      <Card title="Report details (optional)" className="my-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <label htmlFor="cat" className="block text-sm font-medium text-slate-700 sm:col-span-2">
          Category
            <select id="cat" value={category} onChange={(e) => setCategory(e.target.value)}
                    className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm">
              {CATEGORIES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </label>
          <Input id="rdate" label="Report date" type="date" value={reportDate}
                 onChange={(e) => setReportDate(e.target.value)} />
        </div>
      </Card>

      <Button onClick={upload} disabled={!file || busy} className="w-full">
        {busy ? "Uploading…" : file ? `Upload "${file.name}"` : "Choose a file first"}
      </Button>

      <div className="mt-5"><DisclaimerNote>
        Documents are stored securely and processed automatically. If we cannot reliably read the
        document, you will be asked to verify values manually — we never guess.
      </DisclaimerNote></div>
    </div>
  );
}
