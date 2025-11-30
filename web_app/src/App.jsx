import { useState } from 'react'
import axios from 'axios'
import { CodeEditor } from './components/CodeEditor'
import { AnalysisResult } from './components/AnalysisResult'
import { Sidebar } from './components/Sidebar'
import { Play, Loader2 } from 'lucide-react'

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
    <div className="flex h-screen bg-[#0d1117] text-slate-300 font-mono selection:bg-slate-700/50 overflow-hidden">
      {/* Sidebar */}
      <Sidebar onSelectAlgorithm={setCode} selectedAlgorithm={code} />

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header / Toolbar */}
        <header className="h-14 border-b border-slate-800 flex items-center justify-between px-6 bg-[#0d1117]/95 backdrop-blur z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-sm font-bold text-slate-400">Code Editor</h2>
          </div>
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded text-xs font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-900/20"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} fill="currentColor" />}
            RUN ANALYSIS
          </button>
        </header>

        {/* Content Grid */}
        <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-hidden">
          {/* Editor Panel */}
          <div className="flex flex-col gap-4 h-full min-h-0">
            <div className="flex-1 border border-slate-800 rounded-lg overflow-hidden bg-[#0d1117] shadow-sm relative group">
              <div className="absolute top-0 right-0 p-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                <span className="text-[10px] text-slate-600 bg-slate-900/80 px-2 py-1 rounded">Editable</span>
              </div>
              <CodeEditor code={code} onChange={setCode} />
            </div>

            {error && (
              <div className="bg-red-950/20 border border-red-900/50 text-red-400 p-3 rounded text-xs font-mono animate-in fade-in slide-in-from-top-2">
                <span className="font-bold mr-2 text-red-500">[ERROR]</span>
                {error}
              </div>
            )}
          </div>

          {/* Results Panel */}
          <div className="flex flex-col gap-4 h-full min-h-0">
            <div className="flex-1 bg-[#161b22] rounded-lg border border-slate-800 p-6 overflow-y-auto custom-scrollbar shadow-sm">
              {result ? (
                <AnalysisResult data={result} />
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-4">
                  <div className="w-16 h-16 rounded-full bg-slate-800/50 flex items-center justify-center">
                    <Play size={24} className="opacity-20 ml-1" />
                  </div>
                  <div className="text-center">
                    <p className="text-sm font-bold text-slate-500 mb-1">No Analysis Yet</p>
                    <p className="text-xs text-slate-600">Run the analyzer to see complexity details</p>
                  </div>
                </div>
              )}
            </div>
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
