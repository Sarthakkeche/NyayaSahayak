// src/components/SamplePrompts.jsx
import React from "react";
import { motion } from "framer-motion";
import { Wand2 } from "lucide-react";

const samples = [
  "A drunk man slapped a woman on the road and abused her.",
  "Two men threatened a shopkeeper with a knife and stole cash from the counter.",
  "A neighbour threatened to kill me if I file a complaint against him.",
  "Someone stole my mobile phone from my bag in a crowded bus.",
  "A man touched a woman inappropriately in a crowded train.",
];

const SamplePrompts = ({ onSampleClick }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: 0.05 }}
      className="rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-4 sm:px-5 sm:py-4 shadow-md shadow-slate-950/40"
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Wand2 className="h-4 w-4 text-sky-300" />
          <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">
            Try sample incidents
          </h3>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        {samples.map((sample, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSampleClick(sample)}
            className="text-left rounded-full border border-slate-800 bg-slate-950/80 px-3 py-1.5 text-[11px] text-slate-200 hover:border-indigo-500/70 hover:bg-slate-900/90 transition-colors"
          >
            {sample}
          </button>
        ))}
      </div>
    </motion.div>
  );
};

export default SamplePrompts;
