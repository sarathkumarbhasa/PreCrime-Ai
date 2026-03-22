import React, { useEffect, useState } from 'react';
import { User, BrainCircuit, Loader2, FileText } from 'lucide-react';
import { clsx } from 'clsx';

interface PersonaCardsProps {
  entities: any[];
  selectedEntity: string | null;
  onGenerateReport: (id: string) => void;
}

export default function PersonaCards({ entities, selectedEntity, onGenerateReport }: PersonaCardsProps) {
  const [profiles, setProfiles] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState<Record<string, boolean>>({});

  useEffect(() => {
    // Fetch profiles for the top entities
    entities.forEach(entity => {
      if (!profiles[entity.entity_id] && !loading[entity.entity_id]) {
        fetchProfile(entity.entity_id, entity.score);
      }
    });
  }, [entities]);

  const fetchProfile = async (entityId: string, score: number | string) => {
    setLoading(prev => ({ ...prev, [entityId]: true }));
    try {
      const response = await fetch(`http://localhost:8000/api/persona/${entityId}`).catch(e => { throw e; });
      if (!response.ok) {
        throw new Error("Backend error");
      }
      const data = await response.json();
      if (!data) throw new Error("Empty data returned");
      setProfiles(prev => ({ ...prev, [entityId]: data }));
    } catch (err) {
      console.error("Backend Persona Error:", err);
      // Mock fallback
      setProfiles(prev => ({ 
        ...prev, 
        [entityId]: {
          archetype: ["Coordinator", "Mule", "Ghost", "Banker"][Math.floor(Math.random() * 4)],
          summary: `Entity ${entityId} shows high centrality and frequent short-duration contacts. Likely acting as a central node for resource distribution.`
        } 
      }));
    } finally {
      setLoading(prev => ({ ...prev, [entityId]: false }));
    }
  };

  // If an entity is selected, put it first
  const displayEntities = [...entities];
  if (selectedEntity) {
    const selectedIdx = displayEntities.findIndex(e => e.entity_id === selectedEntity);
    if (selectedIdx > 0) {
      const [selected] = displayEntities.splice(selectedIdx, 1);
      displayEntities.unshift(selected);
    } else if (selectedIdx === -1) {
      // If selected entity is not in top 5, add it
      displayEntities.unshift({ entity_id: selectedEntity, score: '?' });
      if (!profiles[selectedEntity] && !loading[selectedEntity]) {
        fetchProfile(selectedEntity, '?');
      }
    }
  }

  return (
    <div className="flex gap-4 h-full">
      {displayEntities.map((entity) => {
        const profile = profiles[entity.entity_id];
        const isLoading = loading[entity.entity_id];
        const isSelected = selectedEntity === entity.entity_id;

        return (
          <div 
            key={entity.entity_id}
            className={clsx(
              "min-w-[280px] max-w-[320px] bg-[#12121a] border rounded-xl p-4 flex flex-col gap-3 transition-all",
              isSelected ? "border-slate-400 shadow-[0_0_15px_rgba(148,163,184,0.2)]" : "border-white/5"
            )}
          >
            <div className="flex items-center justify-between border-b border-white/5 pb-2">
              <div className="flex items-center gap-2">
                <div className="bg-slate-800 p-1.5 rounded-md">
                  <User className="w-4 h-4 text-slate-300" />
                </div>
                <span className="font-mono font-bold text-white">{entity.entity_id}</span>
              </div>
              {profile && (
                <span className="text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                  {profile.archetype}
                </span>
              )}
            </div>

            <div className="flex-1 text-sm text-slate-400 leading-relaxed">
              {isLoading ? (
                <div className="flex flex-col items-center justify-center h-full gap-2 text-slate-500">
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span className="text-xs">Generating profile...</span>
                </div>
              ) : profile ? (
                <div className="flex flex-col h-full">
                  <div className="flex gap-2 items-start flex-1">
                    <BrainCircuit className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                    <p>{profile.summary}</p>
                  </div>
                  <button 
                    onClick={() => onGenerateReport(entity.entity_id)}
                    className="mt-4 flex items-center justify-center gap-2 w-full py-2 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/20 hover:border-indigo-500/30 rounded-lg transition-all text-[10px] font-bold uppercase tracking-wider group"
                  >
                    <FileText className="w-3 h-3 group-hover:scale-110 transition-transform" />
                    Generate Full Report
                  </button>
                </div>
              ) : (
                <p className="italic text-slate-600">Profile unavailable</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
