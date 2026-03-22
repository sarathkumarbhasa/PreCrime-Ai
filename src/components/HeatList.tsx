import React from 'react';
import { clsx } from 'clsx';

interface HeatScore {
  entity_id: string;
  score: number;
  signals: string[];
}

interface HeatListProps {
  scores: HeatScore[];
  selectedEntity: string | null;
  onSelectEntity: (id: string) => void;
}

export default function HeatList({ scores, selectedEntity, onSelectEntity }: HeatListProps) {
  const getScoreColor = (score: number) => {
    if (score >= 81) return 'text-red-500 bg-red-500/10 border-red-500/20';
    if (score >= 66) return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
    if (score >= 41) return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
    return 'text-green-500 bg-green-500/10 border-green-500/20';
  };

  const getDotColor = (score: number) => {
    if (score >= 81) return 'bg-red-500';
    if (score >= 66) return 'bg-orange-500';
    if (score >= 41) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="flex flex-col gap-1.5">
      {scores.map((item) => (
        <button
          key={item.entity_id}
          onClick={() => onSelectEntity(item.entity_id)}
          className={clsx(
            "w-full text-left px-3 py-2 rounded-md border transition-all flex items-center justify-between group",
            selectedEntity === item.entity_id 
              ? "bg-white/10 border-white/20" 
              : "bg-transparent border-transparent hover:bg-white/5 hover:border-white/10"
          )}
        >
          <div className="flex items-center gap-3">
            <div className={clsx("w-2 h-2 rounded-full", getDotColor(item.score))} />
            <span className="font-mono text-sm text-slate-200">{item.entity_id}</span>
          </div>
          
          <div className={clsx(
            "px-2 py-0.5 rounded text-xs font-mono font-bold border",
            getScoreColor(item.score)
          )}>
            {item.score}
          </div>
        </button>
      ))}
    </div>
  );
}
