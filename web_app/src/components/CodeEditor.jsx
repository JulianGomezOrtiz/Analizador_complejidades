import React from 'react'

export function CodeEditor({ code, onChange }) {
  return (
    <textarea
      value={code}
      onChange={(e) => onChange(e.target.value)}
      className="w-full h-full p-4 bg-[#0d1117] text-slate-300 font-mono text-sm resize-none focus:outline-none leading-relaxed custom-scrollbar"
      spellCheck="false"
      placeholder="Enter your algorithm here..."
    />
  )
}
