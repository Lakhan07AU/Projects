import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "HealthSphere — Understand your history. Track your health.",
  description:
    "AI-powered personal and family health intelligence platform. Manage records, reports, trends and preventive-care discussions in one place.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
