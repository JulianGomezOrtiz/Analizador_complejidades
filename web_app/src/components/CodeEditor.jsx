import React, { useState } from 'react'

export function CodeEditor({ code, onChange }) {
  const [showModal, setShowModal] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('http://localhost:8000/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: prompt })
      })
      const data = await response.json()
      if (data.error) {
        setError(data.error)
      } else {
        onChange(data.code)
        setShowModal(false)
        setPrompt('')
      }
    } catch (err) {
      setError("Failed to connect to server")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="relative w-full h-full group">
      <button 
        onClick={() => setShowModal(true)}
        className="absolute top-2 right-6 z-10 bg-indigo-600/90 hover:bg-indigo-600 text-white px-3 py-1 rounded-md text-xs flex items-center gap-1.5 transition-all opacity-0 group-hover:opacity-100 shadow-lg backdrop-blur-sm"
      >
        <span>✨</span> Generate with AI
      </button>

      <textarea
        value={code}
        onChange={(e) => onChange(e.target.value)}
        className="w-full h-full p-4 bg-[#0d1117] text-slate-300 font-mono text-sm resize-none focus:outline-none leading-relaxed custom-scrollbar"
        spellCheck="false"
        placeholder="Enter your algorithm here..."
      />

      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-[#1e293b] p-6 rounded-xl shadow-2xl w-full max-w-md border border-slate-700/50 ring-1 ring-white/10">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <span>✨</span> Generate Algorithm
                </h3>
                <button onClick={() => setShowModal(false)} className="text-slate-400 hover:text-white transition-colors">✕</button>
            </div>
            
            <p className="text-slate-400 text-xs mb-3">Describe the algorithm you want to generate in natural language.</p>
            
            <textarea 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. 'Recursive function to calculate Fibonacci numbers'"
              className="w-full h-32 bg-[#0f172a] text-slate-300 p-3 rounded-lg border border-slate-700 mb-4 text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all resize-none placeholder:text-slate-600"
            />
            
            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
                    <p className="text-red-400 text-xs flex items-center gap-1">
                        <span>⚠️</span> {error}
                    </p>
                </div>
            )}
            
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-slate-400 hover:text-white text-sm font-medium transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={handleGenerate}
                disabled={loading || !prompt.trim()}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-lg shadow-indigo-500/20 flex items-center gap-2"
              >
                {loading ? (
                    <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"/>
                        Generating...
                    </>
                ) : (
                    <>
                        <span>🚀</span> Generate Code
                    </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
