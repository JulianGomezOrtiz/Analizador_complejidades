import React, { useEffect, useState, useRef } from 'react';
import { Graphviz } from 'graphviz-react';

const DiagramViewer = ({ dotSource }) => {
  const [zoom, setZoom] = useState(1);
  const containerRef = useRef(null);

  if (!dotSource) return null;

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.1, 2));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.1, 0.5));

  return (
    <div className="mt-6 p-4 bg-[#0d1117] rounded-lg border border-slate-800 shadow-sm">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-slate-200">Flujo de Control</h3>
        <div className="flex gap-2">
          <button 
            onClick={handleZoomOut}
            className="px-2 py-1 text-sm bg-[#161b22] border border-slate-700 text-slate-300 rounded hover:bg-slate-800 transition-colors"
          >
            -
          </button>
          <span className="text-sm text-slate-400 self-center font-mono">{Math.round(zoom * 100)}%</span>
          <button 
            onClick={handleZoomIn}
            className="px-2 py-1 text-sm bg-[#161b22] border border-slate-700 text-slate-300 rounded hover:bg-slate-800 transition-colors"
          >
            +
          </button>
        </div>
      </div>
      
      <div 
        ref={containerRef}
        className="overflow-auto flex justify-center bg-white rounded border border-slate-700 p-4"
        style={{ minHeight: '300px' }}
      >
        <div style={{ transform: `scale(${zoom})`, transformOrigin: 'top center', transition: 'transform 0.2s' }}>
          <Graphviz 
            dot={dotSource} 
            options={{ 
              height: null, 
              width: null, 
              fit: true, 
              zoom: false 
            }} 
          />
        </div>
      </div>
    </div>
  );
};

export default DiagramViewer;
