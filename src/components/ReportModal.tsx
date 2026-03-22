import React from 'react';
import { X, FileText, Download, Shield } from 'lucide-react';

interface Report {
  title: string;
  content: string;
}

interface ReportModalProps {
  entityId: string;
  report: Report | null;
  onClose: () => void;
  loading: boolean;
}

export default function ReportModal({ entityId, report, onClose, loading }: ReportModalProps) {
  if (!entityId && !loading) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-[#0f0f15] border border-white/10 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl overflow-hidden animate-in zoom-in-95 duration-200">
        
        {/* Modal Header */}
        <div className="p-4 border-b border-white/5 bg-black/40 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-indigo-500/20 p-2 rounded-lg border border-indigo-500/30">
              <FileText className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-white font-bold leading-tight">Intelligence Report</h3>
              <p className="text-[10px] text-slate-500 uppercase tracking-[0.2em]">Priority Authentication Required</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-white/5 rounded-full transition-colors text-slate-400 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar bg-[radial-gradient(circle_at_top_right,rgba(99,102,241,0.05),transparent)]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 gap-4">
              <div className="relative flex h-12 w-12">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-20"></span>
                <div className="relative inline-flex rounded-full h-12 w-12 bg-indigo-500/10 border-2 border-indigo-500/30 items-center justify-center">
                  <Shield className="w-6 h-6 text-indigo-400 animate-pulse" />
                </div>
              </div>
              <p className="text-indigo-400 font-mono text-sm animate-pulse">Running Deep Fusion Analysis...</p>
            </div>
          ) : report ? (
            <div className="space-y-6">
              <div className="border-l-4 border-indigo-500 pl-4 py-1">
                <h4 className="text-xl font-bold text-white tracking-tight">{report.title}</h4>
                <div className="flex items-center gap-2 mt-2">
                  <span className="text-[10px] text-slate-500 font-mono">DOCKET: {entityId}</span>
                  <span className="w-1 h-1 rounded-full bg-slate-700" />
                  <span className="text-[10px] text-slate-500 font-mono">TIMESTAMP: {new Date().toISOString()}</span>
                </div>
              </div>
              
              <div className="space-y-4">
                {report.content.split('\n').filter(p => p.trim()).map((paragraph, idx) => (
                  <p key={idx} className="text-slate-300 leading-relaxed text-sm">
                    {paragraph}
                  </p>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-10">
              <p className="text-slate-500 italic">No report data generated.</p>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-white/5 bg-black/20 flex justify-end gap-3">
          <button 
            onClick={() => window.print()}
            disabled={loading || !report}
            className="flex items-center gap-2 px-4 py-2 text-slate-300 hover:text-white hover:bg-white/5 rounded-lg transition-all text-xs border border-transparent hover:border-white/10 disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5" />
            Download PDF
          </button>
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition-all text-xs font-bold shadow-lg shadow-indigo-500/20 active:scale-95"
          >
            Acknowledge
          </button>
        </div>
      </div>
    </div>
  );
}
