import React, { useState } from 'react'
import { CheckCircle2, Clock, Calculator, FileCode, X, Network } from 'lucide-react'
import clsx from 'clsx'

export function AnalysisResult({ data }) {
  const { complexity, procedure_name } = data
  const [showCostModal, setShowCostModal] = useState(false)
  const [showDiagramModal, setShowDiagramModal] = useState(false)

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

      {/* 1. Metrics: Worst, Best, Average */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <MetricCard label="Worst Case (Big-O)" value={complexity.big_o} color="text-slate-300" />
        <MetricCard label="Best Case (Big-Ω)" value={complexity.big_omega} color="text-slate-300" />
        <MetricCard label="Average Case (Big-Θ)" value={complexity.big_theta} color={colorClass} highlight />
      </div>

      {/* 2. Formula: Recurrence OR Summation */}
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

      {complexity.summation && (
        <div className="bg-[#0d1117] rounded border border-slate-800 p-4">
          <h3 className="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-wider flex items-center gap-2">
            <Calculator size={12} /> Summation Formula
          </h3>
          <p className="font-mono text-sm text-slate-300">
            {complexity.summation}
          </p>
        </div>
      )}

      {/* 3. Resolution Method */}
      {complexity.method && (
        <div className="bg-[#0d1117] rounded border border-slate-800 p-4">
          <h3 className="text-[10px] font-bold text-slate-500 mb-2 uppercase tracking-wider flex items-center gap-2">
            <Calculator size={12} /> Resolution Method
          </h3>
          <p className="font-mono text-sm text-emerald-400 font-bold">
            {complexity.method}
          </p>
        </div>
      )}

      {/* 4. Actions */}
      <div className="flex gap-3">
        <button
          onClick={() => setShowCostModal(true)}
          className="w-fit px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-bold rounded transition-colors border border-slate-700 flex items-center gap-2"
        >
          <FileCode size={16} />
          VIEW ALGORITHM COST ANALYSIS
        </button>

        {data.diagram && (
          <button
            onClick={() => setShowDiagramModal(true)}
            className="w-fit px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-bold rounded transition-colors border border-slate-700 flex items-center gap-2"
          >
            <Network size={16} />
            VIEW CONTROL FLOW GRAPH
          </button>
        )}
      </div>

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

      {/* Cost Modal */}
      {showCostModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0d1117] border border-slate-800 rounded-lg shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-slate-800">
              <h3 className="font-bold text-slate-200 flex items-center gap-2">
                <FileCode size={16} /> Algorithm Cost Analysis
              </h3>
              <button onClick={() => setShowCostModal(false)} className="text-slate-500 hover:text-slate-300">
                <X size={20} />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-0 font-mono text-xs">
              <table className="w-full border-collapse">
                <thead className="bg-slate-900 sticky top-0">
                  <tr>
                    <th className="p-3 text-left text-slate-500 font-bold border-b border-slate-800 w-12">#</th>
                    <th className="p-3 text-left text-slate-500 font-bold border-b border-slate-800">Code</th>
                    <th className="p-3 text-right text-slate-500 font-bold border-b border-slate-800 w-24">Cost</th>
                  </tr>
                </thead>
                <tbody>
                  {data.source_code ? data.source_code.split('\n').map((line, i) => {
                    const lineNum = i + 1
                    const cost = complexity.line_costs ? complexity.line_costs[lineNum.toString()] : ''
                    return (
                      <tr key={i} className="hover:bg-slate-800/30 transition-colors border-b border-slate-800/50">
                        <td className="p-3 text-slate-600 select-none border-r border-slate-800/50 text-right">{lineNum}</td>
                        <td className="p-3 text-slate-300 whitespace-pre">{line}</td>
                        <td className="p-3 text-right font-bold text-emerald-400 border-l border-slate-800/50">
                          {cost || ''}
                        </td>
                      </tr>
                    )
                  }) : (
                    <tr>
                      <td colSpan={3} className="p-8 text-center text-slate-500">
                        Source code not available for display.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Diagram Modal */}
      {showDiagramModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <div className="bg-[#0d1117] border border-slate-800 rounded-lg shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-slate-800">
              <h3 className="font-bold text-slate-200 flex items-center gap-2">
                <Network size={16} /> Control Flow Graph
              </h3>
              <button onClick={() => setShowDiagramModal(false)} className="text-slate-500 hover:text-slate-300">
                <X size={20} />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4 flex items-center justify-center bg-white/5">
              <img src={`data:image/png;base64,${data.diagram}`} alt="Control Flow Graph" className="max-w-full max-h-full object-contain rounded shadow-lg" />
            </div>
          </div>
        </div>
      )}
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
