// src/components/SectionCard.jsx
import React from "react";
import { BadgeCheck } from "lucide-react";

const badge =
  "inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold";

const SectionCard = ({ section }) => {
  const snippet =
    section.full_text && section.full_text.length > 260
      ? section.full_text.slice(0, 260) + "..."
      : section.full_text || "";

  const victims = section.victim_type || [];
  const severity = section.severity_level ?? null;

  return (
    <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 sm:p-4.5 shadow-lg shadow-slate-950/60">
      <div className="flex justify-between gap-3 mb-1.5">
        <div>
          <p className="text-[11px] uppercase tracking-wide text-slate-400">
            {section.act_name || "BNS"} · Section {section.section_number}
          </p>
          <p className="font-semibold text-sm text-slate-50">
            {section.title}
          </p>
        </div>
        <span
          className={`${badge} bg-indigo-500/15 text-indigo-200 border border-indigo-500/40`}
        >
          {section.section_id}
        </span>
      </div>

      {/* Meta chips */}
      <div className="flex flex-wrap items-center gap-1.5 mt-2 mb-2">
        {section.primary_offence && (
          <span className={`${badge} bg-slate-800 text-slate-200`}>
            {section.primary_offence.replace(/_/g, " ")}
          </span>
        )}
        {section.subtype && (
          <span className={`${badge} bg-slate-800 text-slate-200`}>
            {section.subtype.replace(/_/g, " ")}
          </span>
        )}
        {severity && (
          <span className={`${badge} bg-rose-500/15 text-rose-200 border border-rose-500/40`}>
            Severity: {severity}/5
          </span>
        )}
        {section.is_sexual_offence && (
          <span className={`${badge} bg-pink-500/15 text-pink-100 border border-pink-500/40`}>
            Sexual offence
          </span>
        )}
        {section.is_property_offence && (
          <span className={`${badge} bg-amber-500/15 text-amber-100 border border-amber-500/40`}>
            Property offence
          </span>
        )}
        {section.has_weapon && (
          <span className={`${badge} bg-red-500/15 text-red-100 border border-red-500/40`}>
            Weapon involved
          </span>
        )}
        {victims.length > 0 && (
          <span className={`${badge} bg-emerald-500/15 text-emerald-100 border border-emerald-500/40`}>
            Victim: {victims.join(", ")}
          </span>
        )}
      </div>

      <p className="text-xs text-slate-300 leading-relaxed">{snippet}</p>

      <div className="mt-2 flex items-center gap-1 text-[10px] text-slate-500">
        <BadgeCheck className="h-3 w-3 text-emerald-400" />
        <span>From verified BNS_enriched dataset</span>
      </div>
    </div>
  );
};

export default SectionCard;
