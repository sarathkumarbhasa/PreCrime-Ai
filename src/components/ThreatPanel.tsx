import React from 'react';
import { AlertTriangle, Clock, Target, Activity } from 'lucide-react';
import { clsx } from 'clsx';

interface ThreatForecast {
  cluster_id: string;
  member_count: number;
  threat_level: string;
  activation_window: string;
  confidence: number;
  active_signals: number;
  last_convergence: string;
  primary_entity: string;
}

interface ThreatPanelProps {
  forecasts: ThreatForecast[];
}

export default function ThreatPanel({ forecasts }: ThreatPanelProps) {
  if (!forecasts || forecasts.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-slate-500 text-sm">
        No active threats detected.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {forecasts.map((forecast, idx) => (
        <div 
          key={idx} 
          className={clsx(
            "rounded-lg border p-3 flex flex-col gap-3",
            forecast.threat_level === 'CRITICAL' 
              ? "bg-red-950/20 border-red-500/30" 
              : "bg-orange-950/20 border-orange-500/30"
          )}
        >
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-2">
                <AlertTriangle className={clsx(
                  "w-4 h-4",
                  forecast.threat_level === 'CRITICAL' ? "text-red-500" : "text-orange-500"
                )} />
                <h3 className="font-bold text-sm text-white">{forecast.cluster_id}</h3>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">Primary: <span className="font-mono text-slate-300">{forecast.primary_entity}</span></p>
            </div>
            <span className={clsx(
              "text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider",
              forecast.threat_level === 'CRITICAL' 
                ? "bg-red-500/20 text-red-400" 
                : "bg-orange-500/20 text-orange-400"
            )}>
              {forecast.threat_level}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="bg-black/30 rounded p-2 border border-white/5">
              <div className="flex items-center gap-1.5 text-slate-400 mb-1">
                <Clock className="w-3 h-3" />
                <span className="text-[10px] uppercase tracking-wider">Window</span>
              </div>
              <div className="font-mono text-sm text-white">{forecast.activation_window}</div>
            </div>
            
            <div className="bg-black/30 rounded p-2 border border-white/5">
              <div className="flex items-center gap-1.5 text-slate-400 mb-1">
                <Target className="w-3 h-3" />
                <span className="text-[10px] uppercase tracking-wider">Confidence</span>
              </div>
              <div className="font-mono text-sm text-white">{forecast.confidence}%</div>
            </div>
          </div>

          <div className="flex items-center justify-between text-xs text-slate-400 bg-black/20 p-2 rounded border border-white/5">
            <div className="flex items-center gap-1.5">
              <Activity className="w-3 h-3" />
              <span>Signals: {forecast.active_signals}/5</span>
            </div>
            <span>{forecast.member_count} members</span>
          </div>
        </div>
      ))}
    </div>
  );
}
