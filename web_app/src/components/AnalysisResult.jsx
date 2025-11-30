import React from 'react'
import { CheckCircle2, Clock, Calculator } from 'lucide-react'
import clsx from 'clsx'

export function AnalysisResult({ data }) {
  const { complexity, procedure_name } = data
  
  const getComplexityColor = (theta) => {
    if (!theta) return 'text-slate-500'
    if (theta.includes('1') || theta.includes('log')) return 'text-emerald-400'
    if (theta.includes('n^2') || theta.includes('n**2')) return 'text-orange-400'
    if (theta.includes('n^3') || theta.includes('n**3')) return 'text-red-400'
    if (theta.includes('^n')) return 'text-purple-400'
    return 'text-blue-400'
  }

  const colorClass = getComplexityColor(complexity.big_theta)

  return (
    <div className="space-y-6">
      <div className="border-b border-slate-800 pb-4">
        <h2 className="text-xl font-bold text-slate-200 tracking-tight">{procedure_name}</h2>
        <p className="text-slate-500 text-xs mt-1 font-mono">
          Complexity Analysis
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <MetricCard label="Worst Case (Big-O)" value={complexity.big_o} color="text-slate-300" />
        <MetricCard label="Best Case (Big-Ω)" value={complexity.big_omega} color="text-slate-300" />
        <MetricCard label="Average Case (Big-Θ)" value={complexity.big_theta} color={colorClass} highlight />
      </div>

      {complexity.recurrence && (
        <div className="bg-[#0d1117] rounded border border-slate-800 p-4">
          <h3 className="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-wider flex items-center gap-2">
            <Clock size={12} /> Recurrence Relation
          </h3>
          <p className="font-mono text-sm text-slate-300">
            {complexity.recurrence}
          </p>
        </div>
      )}

      <div>
        <h3 className="text-[10px] font-bold text-slate-500 mb-3 uppercase tracking-wider flex items-center gap-2">
          <CheckCircle2 size={12} /> Reasoning Trace
        </h3>
        <div className="space-y-2 font-mono text-xs">
          {complexity.reasoning.map((step, idx) => (
            <div key={idx} className="flex gap-3 text-slate-400">
              <span className="text-slate-600 select-none">{(idx + 1).toString().padStart(2, '0')}</span>
              <p className="leading-relaxed">
                {step}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function MetricCard({ label, value, color, highlight }) {
  return (
    <div className={clsx("bg-[#0d1117] p-4 rounded border border-slate-800", highlight && "border-slate-700 bg-slate-800/20")}>
      <p className="text-[10px] text-slate-500 mb-1 font-bold uppercase tracking-wider">{label}</p>
      <p className={clsx("text-lg font-mono font-bold tracking-tight", color)}>{value}</p>
    </div>
  )
}
