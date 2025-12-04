// src/components/SectionResults.jsx
import React from "react";
import { motion } from "framer-motion";
import { Gavel } from "lucide-react";
import SectionCard from "./SectionCard";

const SectionResults = ({ sections }) => {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/80 shadow-2xl shadow-indigo-500/20">
      <div className="px-4 py-3 sm:px-5 sm:py-3.5 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Gavel className="h-4 w-4 text-indigo-300" />
          <h2 className="text-sm font-semibold text-slate-50">
            Suggested Legal Sections
          </h2>
        </div>
        <p className="text-[11px] text-slate-400">
          {sections.length} section{sections.length !== 1 && "s"} suggested
        </p>
      </div>

      <div className="divide-y divide-slate-800/80">
        {sections.map((section, idx) => (
          <motion.div
            key={section.section_id || idx}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: 0.03 * idx }}
            className="p-4 sm:p-5"
          >
            <SectionCard section={section} />
          </motion.div>
        ))}
      </div>
    </section>
  );
};

export default SectionResults;
