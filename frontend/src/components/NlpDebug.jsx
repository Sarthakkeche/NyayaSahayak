// src/components/NlpDebug.jsx
import React from "react";
import { motion } from "framer-motion";
import { BadgeCheck, Brain } from "lucide-react";

const NlpDebug = ({ analysis, loading }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.05 }}
      className="rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3 sm:px-5 sm:py-3.5 text-xs shadow-md shadow-slate-950/40"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Brain className="h-4 w-4 text-emerald-300" />
          <h3 className="text-[11px] font-semibold uppercase tracking-wide text-slate-200">
            NLP Extraction
          </h3>
        </div>
        <div className="flex items-center gap-1 text-[10px] text-slate-400">
          <BadgeCheck className="h-3 w-3 text-emerald-400" />
          <span>Deterministic → No legal hallucinations</span>
        </div>
      </div>

      {loading && (
        <p className="text-[11px] text-slate-400">
          Understanding incident text...
        </p>
      )}

      {!loading && analysis && (
        <div className="space-y-2">
          <div>
            <p className="text-[11px] text-slate-400 mb-1">
              Normalized crime tags:
            </p>
            <div className="flex flex-wrap gap-1.5">
              {analysis.normalized_keywords.length === 0 && (
                <span className="text-[11px] text-slate-500">
                  No tags detected yet.
                </span>
              )}
              {analysis.normalized_keywords.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-medium text-emerald-200 border border-emerald-500/30"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {analysis.lemmas && analysis.lemmas.length > 0 && (
            <div>
              <p className="text-[11px] text-slate-400 mb-1">
                Debug lemmas (from text):
              </p>
              <div className="flex flex-wrap gap-1.5">
                {analysis.lemmas.map((lemma, idx) => (
                  <span
                    key={`${lemma}-${idx}`}
                    className="rounded-full border border-slate-700 bg-slate-900/80 px-2 py-0.5 text-[10px] text-slate-300"
                  >
                    {lemma}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!loading && !analysis && (
        <p className="text-[11px] text-slate-500">
          Tags and lemmas will appear here after you analyze an incident.
        </p>
      )}
    </motion.div>
  );
};

export default NlpDebug;
