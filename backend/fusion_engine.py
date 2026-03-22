import json
from datetime import datetime
import os

class FusionEngine:
    def __init__(self, data_path="../data/sample_dataset.json"):
        self.data_path = data_path
        self.data = self._load_data()
        
    def _load_data(self):
        if not os.path.exists(self.data_path):
            return {"entities": [], "cdr_logs": [], "chat_logs": [], "transaction_logs": [], "location_logs": []}
        try:
            with open(self.data_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"entities": [], "cdr_logs": [], "chat_logs": [], "transaction_logs": [], "location_logs": []}

    def _safe_parse_time(self, t_str):
        if not t_str or t_str == 'nan': return None
        try:
            return datetime.fromisoformat(str(t_str))
        except:
            return None

    def fuse_signals(self):
        entities = self.data.get("entities", [])
        fusion_results = []
        
        for entity in entities:
            active_sources = set()
            
            for log in self.data.get("cdr_logs", []):
                if log.get("caller_id") == entity or log.get("receiver_id") == entity:
                    if self._safe_parse_time(log.get("timestamp")): active_sources.add("CDR")
                    
            for log in self.data.get("chat_logs", []):
                if log.get("sender_id") == entity or log.get("receiver_id") == entity:
                    if self._safe_parse_time(log.get("timestamp")): active_sources.add("chat")
                    
            for log in self.data.get("transaction_logs", []):
                if log.get("account_id") == entity:
                    if self._safe_parse_time(log.get("timestamp")): active_sources.add("transaction")
                    
            for log in self.data.get("location_logs", []):
                if log.get("entity_id") == entity:
                    if self._safe_parse_time(log.get("timestamp")): active_sources.add("location")
                    
            active_sources = list(active_sources)
            if len(active_sources) >= 2:
                confidence = (len(active_sources) / 4.0) * 100
                threat_level = "LOW"
                if confidence >= 75: threat_level = "CRITICAL"
                elif confidence >= 50: threat_level = "HIGH"
                elif confidence >= 25: threat_level = "MEDIUM"
                    
                fusion_results.append({
                    "entity_id": entity,
                    "agreeing_sources": active_sources,
                    "confidence": confidence,
                    "time_window": "Last 24 hours",
                    "threat_level": threat_level
                })
                
        return fusion_results

if __name__ == "__main__":
    engine = FusionEngine()
    print(json.dumps(engine.fuse_signals()[:2], indent=2))
