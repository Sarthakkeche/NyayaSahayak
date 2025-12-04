// src/components/IncidentForm.jsx
import React from "react";
import { motion } from "framer-motion";
import { Loader2, Sparkles } from "lucide-react";

const IncidentForm = ({ text, onChange, onAnalyze, onClear, loading }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="rounded-2xl border border-slate-800 bg-slate-900/80 shadow-xl shadow-indigo-500/10"
    >
      <div className="border-b border-slate-800/80 px-4 py-3 sm:px-5 sm:py-3.5 flex items-center justify-between">
        <div>
          <h2 className="text-sm sm:text-base font-semibold text-slate-50">
            Incident Description
          </h2>
          <p className="text-[11px] text-slate-400">
            Type the incident in simple language. NyayaSahayak will suggest
            likely sections.
          </p>
        </div>
        <Sparkles className="hidden sm:block h-5 w-5 text-indigo-300" />
      </div>

      <div className="px-4 py-3 sm:px-5 sm:py-4 space-y-3">
        <textarea
          className="w-full min-h-[120px] max-h-[220px] rounded-xl border border-slate-700 bg-slate-950/80 px-3 py-2 text-sm text-slate-50 placeholder:text-slate-500 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-500/60 shadow-inner shadow-slate-900"
          placeholder="Example: A drunk man slapped a woman on the road and threatened her with abuse..."
          value={text}
          onChange={(e) => onChange(e.target.value)}
        />

        <div className="flex items-center justify-between gap-3 flex-wrap">
          <p className="text-[11px] text-slate-400">
            Tip: Mention{" "}
            <span className="font-medium text-slate-200">
              who, what, where, and any weapons
            </span>{" "}
            used.
          </p>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClear}
              disabled={loading || !text.trim()}
              className="text-[11px] px-3 py-1.5 rounded-full border border-slate-700 bg-slate-900/80 text-slate-300 hover:bg-slate-800 disabled:opacity-40"
            >
              Clear
            </button>
            <button
              type="button"
              onClick={onAnalyze}
              disabled={loading || !text.trim()}
              className="inline-flex items-center gap-2 rounded-full bg-indigo-500 px-4 py-1.5 text-xs font-medium text-white shadow-md shadow-indigo-500/50 hover:bg-indigo-600 disabled:opacity-40"
            >
              {loading ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>Analyze Incident</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default IncidentForm;
