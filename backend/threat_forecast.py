import json
import random

class ThreatForecastEngine:
    def __init__(self, fusion_results, heat_scores):
        self.fusion_results = fusion_results if fusion_results is not None else []
        self.heat_scores = {str(item.get("entity_id", "")): item for item in (heat_scores if heat_scores else [])}
        
    def generate_forecasts(self):
        forecasts = []
        cluster_id = 1
        
        high_threats = [f for f in self.fusion_results if f.get("threat_level") in ["HIGH", "CRITICAL"]]
        if not high_threats:
            return []
            
        for i in range(min(3, len(high_threats))):
            entity = high_threats[i]
            entity_id = str(entity.get("entity_id", ""))
            entity_heat = self.heat_scores.get(entity_id, {})
            
            forecasts.append({
                "cluster_id": f"Cluster #{cluster_id}",
                "member_count": random.randint(3, 8),
                "threat_level": entity.get("threat_level", "HIGH"),
                "activation_window": f"{random.randint(12, 48)}h",
                "confidence": min(entity.get("confidence", 50), 92.0),
                "active_signals": len(entity_heat.get("signals", [])),
                "last_convergence": "2 hours ago",
                "primary_entity": entity_id
            })
            cluster_id += 1
            
        return forecasts
