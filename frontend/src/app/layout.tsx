import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CrowdSense | Real-Time Crowd Intelligence & Personal Rerouting",
  description: "Next-generation venue crowd management, bottleneck prediction, and personalized attendee navigation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#080b11] text-slate-100 min-h-screen antialiased selection:bg-cyan-500 selection:text-slate-950 font-sans">
        {children}
      </body>
    </html>
  );
}
