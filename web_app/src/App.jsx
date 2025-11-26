import { useState } from 'react'
import axios from 'axios'
import { CodeEditor } from './components/CodeEditor'
import { AnalysisResult } from './components/AnalysisResult'
import { Play, Loader2, Terminal } from 'lucide-react'

function App() {
  const [code, setCode] = useState(DEFAULT_CODE)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await axios.post('http://localhost:8000/analyze', { code })
      if (res.data.error) {
        setError(res.data.error)
        setResult(null)
      } else {
        setResult(res.data)
      }
    } catch (err) {
      setError(err.message)
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0d1117] text-slate-300 font-mono selection:bg-slate-700/50">
      {/* Navbar Minimalista */}
      <nav className="border-b border-slate-800 bg-[#0d1117]/95 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Terminal size={18} className="text-emerald-500" />
            <span className="font-bold text-sm tracking-wide text-slate-200">COMPLEXITY.AI</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-500">v1.0.0</span>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-3.5rem)]">
        {/* Panel Izquierdo: Editor */}
        <div className="flex flex-col gap-4 h-full">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">Input Source</h2>
            <button
              onClick={handleAnalyze}
              disabled={loading}
              className="flex items-center gap-2 bg-slate-100 hover:bg-white text-slate-900 px-4 py-1.5 rounded text-xs font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} fill="currentColor" />}
              RUN ANALYSIS
            </button>
          </div>
          
          <div className="flex-1 border border-slate-800 rounded-lg overflow-hidden bg-[#0d1117]">
            <CodeEditor code={code} onChange={setCode} />
          </div>

          {error && (
            <div className="bg-red-950/30 border border-red-900/50 text-red-400 p-3 rounded text-xs font-mono">
              <span className="font-bold mr-2">[ERROR]</span>
              {error}
            </div>
          )}
        </div>

        {/* Panel Derecho: Resultados */}
        <div className="flex flex-col gap-4 h-full overflow-hidden">
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">Analysis Output</h2>
          <div className="flex-1 bg-[#161b22] rounded-lg border border-slate-800 p-6 overflow-y-auto custom-scrollbar">
            {result ? (
              <AnalysisResult data={result} />
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-3">
                <Terminal size={32} className="opacity-20" />
                <p className="text-sm font-mono">Ready to analyze...</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

const DEFAULT_CODE = `PROCEDURE InsertionSort(A, n)
BEGIN
  FOR i <- 2 TO n DO
  BEGIN
    key <- A[i];
    j <- i - 1;
    WHILE j > 0 and A[j] > key DO
    BEGIN
      A[j+1] <- A[j];
      j <- j - 1;
    END
    A[j+1] <- key;
  END
END`

export default App
