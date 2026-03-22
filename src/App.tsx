import React, { useState, useEffect } from 'react';
import NetworkGraph from './components/NetworkGraph';
import ThreatPanel from './components/ThreatPanel';
import HeatList from './components/HeatList';
import PersonaCards from './components/PersonaCards';
import GeoMap from './components/GeoMap';
import ReportModal from './components/ReportModal';
import { ShieldAlert, Activity, RefreshCw, Play } from 'lucide-react';

// Mock data fallback for AI Studio preview
const MOCK_DATA = {
  network: {
    nodes: Array.from({ length: 20 }, (_, i) => ({
      id: `E${String(i + 1).padStart(3, '0')}`,
      centrality: Math.random()
    })),
    links: Array.from({ length: 40 }, () => ({
      source: `E${String(Math.floor(Math.random() * 20) + 1).padStart(3, '0')}`,
      target: `E${String(Math.floor(Math.random() * 20) + 1).padStart(3, '0')}`,
      weight: Math.floor(Math.random() * 5) + 1
    }))
  },
  heatScores: Array.from({ length: 20 }, (_, i) => ({
    entity_id: `E${String(i + 1).padStart(3, '0')}`,
    score: Math.floor(Math.random() * 100),
    signals: ["Call frequency spike", "Location convergence"]
  })).sort((a, b) => b.score - a.score),
  forecasts: [
    {
      cluster_id: "Cluster #1",
      member_count: 5,
      threat_level: "CRITICAL",
      activation_window: "12-36h",
      confidence: 85,
      active_signals: 4,
      last_convergence: "2 hours ago",
      primary_entity: "E007"
    },
    {
      cluster_id: "Cluster #2",
      member_count: 3,
      threat_level: "HIGH",
      activation_window: "24-48h",
      confidence: 65,
      active_signals: 3,
      last_convergence: "5 hours ago",
      primary_entity: "E012"
    }
  ]
};

export default function App() {
  const [networkData, setNetworkData] = useState(MOCK_DATA.network);
  const [heatScores, setHeatScores] = useState(MOCK_DATA.heatScores);
  const [forecasts, setForecasts] = useState(MOCK_DATA.forecasts);
  const [selectedEntity, setSelectedEntity] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportEntity, setReportEntity] = useState<string | null>(null);
  const [currentReport, setCurrentReport] = useState<any>(null);
  const [reportLoading, setReportLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const downloadReport = async () => {
    setDownloading(true);
    try {
      const response = await fetch('http://localhost:8000/api/report');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PRECRIME_Report_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Report download failed:', err);
    }
    setDownloading(false);
  };

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Attempt to fetch from Python backend
      const [netRes, heatRes, forecastRes] = await Promise.all([
        fetch('http://localhost:8000/api/network').catch(e => { throw e; }),
        fetch('http://localhost:8000/api/heat-scores').catch(e => { throw e; }),
        fetch('http://localhost:8000/api/forecasts').catch(e => { throw e; })
      ]);
      
      if (netRes.ok && heatRes.ok && forecastRes.ok) {
        setNetworkData(await netRes.json());
        setHeatScores(await heatRes.json());
        setForecasts(await forecastRes.json());
      } else {
        throw new Error("Backend not reachable");
      }
    } catch (err) {
      console.warn("Using mock data. Backend not reachable at http://localhost:8000");
      // Fallback to mock data is already set in state
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSimulateThreat = () => {
    const targetId = "E015"; // Pick a specific node to spike
    let currentScore = heatScores.find(h => h.entity_id === targetId)?.score || 30;
    
    const interval = setInterval(() => {
      currentScore += 15;
      if (currentScore >= 95) {
        currentScore = 95;
        clearInterval(interval);
      }
      
      setHeatScores(prev => {
        const newScores = [...prev];
        const idx = newScores.findIndex(h => h.entity_id === targetId);
        if (idx !== -1) {
          newScores[idx] = { 
            ...newScores[idx], 
            score: currentScore, 
            signals: Array.from(new Set([...newScores[idx].signals, "Rapid Heat Spike", "Geo-Convergence"]))
          };
        }
        return newScores.sort((a, b) => b.score - a.score);
      });
      
    }, 800);
  };
  
  const handleGenerateReport = async (entityId: string) => {
    setReportEntity(entityId);
    setReportLoading(true);
    setCurrentReport(null);
    try {
      const res = await fetch(`http://localhost:8000/api/report/${entityId}`).catch(e => { throw e; });
      if (!res.ok) throw new Error("Report generation failed");
      const data = await res.json();
      setCurrentReport(data);
    } catch (err) {
      console.error(err);
    } finally {
      setReportLoading(false);
    }
  };

  const criticalThreats = forecasts.filter(f => f.threat_level === 'CRITICAL' || f.threat_level === 'HIGH').length;

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-300 font-sans flex flex-col overflow-hidden">
      {/* Header */}
      <header className="h-14 border-b border-white/10 bg-black/50 flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-3">
          <ShieldAlert className="w-6 h-6 text-red-500" />
          <h1 className="text-lg font-bold tracking-wider text-white">PRECRIME AI</h1>
        </div>
        
        <div className="flex items-center gap-6">
          <button 
            onClick={handleSimulateThreat}
            className="flex items-center gap-2 px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 rounded-md transition-colors text-xs font-bold uppercase tracking-wider"
          >
            <Play className="w-3 h-3" />
            Simulate Threat
          </button>

          <div className="flex items-center gap-2">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Live Threats:</span>
            <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 font-mono text-sm font-bold border border-red-500/30">
              {criticalThreats}
            </span>
          </div>
          
          <button
            onClick={downloadReport}
            disabled={downloading}
            className="bg-red-900 hover:bg-red-700 text-white px-4 py-1 rounded text-sm font-bold border border-red-500 transition-all"
          >
            {downloading ? '⏳ Generating...' : '📄 Download Report'}
          </button>
          
          <div className="flex items-center gap-2">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
            <span className="text-xs font-mono text-emerald-500 uppercase tracking-wider">System Active</span>
          </div>
          
          <button 
            onClick={fetchData}
            className="p-2 hover:bg-white/5 rounded-full transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 text-slate-400 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col md:flex-row overflow-hidden p-4 gap-4">
        
        {/* Left Sidebar: Entity List */}
        <div className="w-full md:w-64 flex flex-col gap-4 shrink-0">
          <div className="bg-[#12121a] border border-white/5 rounded-xl flex-1 flex flex-col overflow-hidden shadow-lg">
            <div className="p-3 border-b border-white/5 bg-black/20">
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-3 h-3" />
                Entity Heat List
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-2 custom-scrollbar">
              <HeatList 
                scores={heatScores} 
                selectedEntity={selectedEntity}
                onSelectEntity={setSelectedEntity} 
              />
            </div>
          </div>
        </div>

        {/* Center: Network Graph */}
        <div className="flex-1 bg-[#12121a] border border-white/5 rounded-xl flex flex-col overflow-hidden shadow-lg relative min-h-[400px]">
          <div className="absolute top-4 left-4 z-10 pointer-events-none">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider bg-black/50 px-3 py-1.5 rounded-md backdrop-blur-sm border border-white/5">
              Living Network Graph
            </h2>
          </div>
          <div className="flex-1 relative">
            <NetworkGraph 
              data={networkData} 
              heatScores={heatScores}
              selectedEntity={selectedEntity}
              onNodeClick={setSelectedEntity}
            />
          </div>
        </div>

        {/* Right Sidebar: Threat Forecast & GeoMap */}
        <div className="w-full md:w-80 flex flex-col gap-4 shrink-0">
          <div className="bg-[#12121a] border border-white/5 rounded-xl flex flex-col overflow-hidden shadow-lg shrink-0">
            <GeoMap />
          </div>
          <div className="bg-[#12121a] border border-white/5 rounded-xl flex-1 flex flex-col overflow-hidden shadow-lg">
            <div className="p-3 border-b border-white/5 bg-black/20">
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Threat Forecast
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto p-3 custom-scrollbar">
              <ThreatPanel forecasts={forecasts} />
            </div>
          </div>
        </div>
      </main>

      {/* Bottom Panel: Persona Profiles */}
      <footer className="h-48 border-t border-white/10 bg-[#0a0a0f] shrink-0 p-4 overflow-hidden flex flex-col">
        <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 shrink-0">
          Persona Profiles
        </h2>
        <div className="flex-1 overflow-x-auto custom-scrollbar pb-2">
          <PersonaCards 
            entities={heatScores} 
            selectedEntity={selectedEntity}
            onGenerateReport={handleGenerateReport}
          />
        </div>
      </footer>

      <ReportModal 
        entityId={reportEntity || ''}
        report={currentReport}
        loading={reportLoading}
        onClose={() => setReportEntity(null)}
      />
    </div>
  );
}
