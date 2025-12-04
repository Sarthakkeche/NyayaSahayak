// src/App.jsx
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Scale,
  ShieldCheck,
  Sparkles,
  Brain,
  RefreshCw,
  Gavel,
  Zap,
} from "lucide-react";

import IncidentForm from "./components/IncidentForm";
import NlpDebug from "./components/NlpDebug";
import SectionResults from "./components/SectionResults";
import SamplePrompts from "./components/SamplePrompts";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [incidentText, setIncidentText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [requestId, setRequestId] = useState(0); // used to animate result reset

  const handleAnalyze = async () => {
    const text = incidentText.trim();
    if (!text) return;

    setLoading(true);
    setError("");
    setAnalysis(null);
    setRequestId((id) => id + 1);

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      if (!res.ok) {
        throw new Error("Server error. Please verify backend is running.");
      }

      const data = await res.json();
      setAnalysis(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleSampleClick = (sample) => {
    setIncidentText(sample);
    setAnalysis(null);
    setError("");
  };

  const handleClear = () => {
    setIncidentText("");
    setAnalysis(null);
    setError("");
    setRequestId((id) => id + 1);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
      {/* Top gradient blob background */}
      <div className="pointer-events-none fixed inset-x-0 top-0 z-0 h-[420px] bg-gradient-to-b from-indigo-500/30 via-slate-900 to-slate-950 blur-3xl opacity-60" />

      <main className="relative z-10 max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-10 space-y-6 sm:space-y-8">
        {/* Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/40 bg-slate-900/60 px-3 py-1 text-[11px] font-medium text-indigo-100 shadow-md shadow-indigo-500/20">
              <Sparkles className="h-3 w-3 text-indigo-300" />
              <span>Prototype • Legal AI Advisor for FIR drafting</span>
            </div>

            <div className="mt-3 flex items-center gap-3">
              <Scale className="hidden sm:block h-8 w-8 text-indigo-300" />
              <div>
                <h1 className="text-2xl sm:text-3xl md:text-4xl font-semibold tracking-tight text-slate-50">
                  NyayaSahayak
                </h1>
                <p className="mt-1 text-xs sm:text-sm text-slate-300">
                  One-shot section suggester for{" "}
                  <span className="font-medium text-indigo-200">
                    BNS / IPC
                  </span>{" "}
                  – no login, no history, just fast legal support for police.
                </p>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="hidden sm:flex flex-col gap-1 rounded-xl border border-slate-700 bg-slate-900/70 px-4 py-2 text-xs text-slate-300 shadow">
              <div className="flex items-center gap-2">
                <Brain className="h-3.5 w-3.5 text-emerald-300" />
                <span className="font-medium text-slate-100">
                  Deterministic mode
                </span>
              </div>
              <p className="text-[11px] text-slate-400">
                AI only understands language. Legal sections are fetched from
                your verified BNS dataset.
              </p>
            </div>
          </div>
        </div>

        {/* Main content grid */}
        <div className="grid lg:grid-cols-[minmax(0,1.1fr)_minmax(0,0.9fr)] gap-5 lg:gap-6">
          {/* Left column: Form + NLP */}
          <div className="space-y-4">
            <IncidentForm
              text={incidentText}
              onChange={setIncidentText}
              onAnalyze={handleAnalyze}
              onClear={handleClear}
              loading={loading}
            />

            <NlpDebug analysis={analysis} loading={loading} />

            {error && (
              <div className="rounded-xl border border-red-500/40 bg-red-950/40 px-4 py-3 text-xs text-red-100">
                {error}
              </div>
            )}
          </div>

          {/* Right column: sample prompts + meta info */}
          <div className="space-y-4">
            <SamplePrompts onSampleClick={handleSampleClick} />

            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: 0.05 }}
              className="rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-4 sm:px-5 sm:py-5 shadow-lg shadow-indigo-500/10"
            >
              <div className="flex items-center gap-2 mb-2">
                <ShieldCheck className="h-4 w-4 text-emerald-300" />
                <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">
                  How officers can use this
                </h3>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                <li className="flex gap-2">
                  <span className="mt-[3px] h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  <span>
                    Type the incident in plain language – Hindi / Hinglish /
                    English is okay.
                  </span>
                </li>
                <li className="flex gap-2">
                  <span className="mt-[3px] h-1.5 w-1.5 rounded-full bg-indigo-400" />
                  <span>
                    Use the suggested sections to draft FIR. Final decision
                    always rests with the officer.
                  </span>
                </li>
                <li className="flex gap-2">
                  <span className="mt-[3px] h-1.5 w-1.5 rounded-full bg-sky-400" />
                  <span>
                    System is tuned for{" "}
                    <span className="font-semibold">BNS 2023</span> – IPC
                    equivalents are also stored in the backend.
                  </span>
                </li>
              </ul>

              <div className="mt-3 flex items-center gap-2 text-[10px] text-slate-400 border-t border-slate-800/80 pt-2">
                <Gavel className="h-3 w-3 text-slate-500" />
                <span>
                  Prototype only – does{" "}
                  <span className="font-semibold text-slate-200">
                    not replace legal advice
                  </span>
                  .
                </span>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.12 }}
              className="hidden md:block rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900 via-slate-900/90 to-indigo-950/80 px-4 py-4 shadow-lg shadow-indigo-500/20"
            >
              <div className="flex items-center gap-2 mb-2">
                <Zap className="h-4 w-4 text-yellow-300" />
                <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">
                  System snapshot
                </h3>
              </div>
              <div className="grid grid-cols-3 gap-3 text-[11px] text-slate-300">
                <div>
                  <p className="text-slate-400">BNS sections loaded</p>
                  <p className="text-sm font-semibold text-slate-50">
                    ~{analysis?.sections?.length || "300+"}
                  </p>
                </div>
                <div>
                  <p className="text-slate-400">NLP mode</p>
                  <p className="text-sm font-semibold text-emerald-300">
                    Rules + spaCy
                  </p>
                </div>
                <div>
                  <p className="text-slate-400">Request ID</p>
                  <p className="text-sm font-semibold text-slate-50">
                    #{requestId}
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </div>

        {/* Suggested sections block */}
        <AnimatePresence mode="wait">
          {analysis?.sections && analysis.sections.length > 0 && (
            <motion.div
              key={requestId}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 12 }}
              transition={{ duration: 0.35 }}
              className="mt-2"
            >
              <SectionResults sections={analysis.sections} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-900/90 bg-slate-950/95">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-col sm:flex-row items-center justify-between gap-2 text-[11px] text-slate-500">
          <span>
            Built as an experimental tool for{" "}
            <span className="text-slate-200 font-medium">Indian policing</span>.
          </span>
          <span className="flex items-center gap-1">
            <RefreshCw className="h-3 w-3" />
            <span>Backend: FastAPI · Frontend: React + Tailwind</span>
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
