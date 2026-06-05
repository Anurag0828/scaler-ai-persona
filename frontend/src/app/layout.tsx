import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Anurag Sajwan | Autonomous AI Persona",
  description: "Chat with Anurag Sajwan's autonomous AI persona. Powered by RAG, NVIDIA NIM, and Pinecone. Ask about his experience, skills, projects, or schedule an interview.",
  keywords: ["AI Persona", "Anurag Sajwan", "RAG", "NVIDIA NIM", "Scaler", "AI Engineer"],
  authors: [{ name: "Anurag Sajwan" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full`}>
      <body className="min-h-full flex flex-col antialiased" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
