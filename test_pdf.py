import sys
sys.path.append('backend')
from report_generator import generate_report
from heat_score import HeatScoreEngine
from fusion_engine import FusionEngine
from threat_forecast import ThreatForecastEngine
from persona_profiler import PersonaProfiler
from main import get_suspicious_timeline, graph_engine

print("Initializing engines...")
heat_engine = HeatScoreEngine('data/sample_dataset.json')
fusion_engine = FusionEngine('data/sample_dataset.json')
profiler = PersonaProfiler()

entities = heat_engine.calculate_scores()
fusion_res = fusion_engine.fuse_signals()
f_engine = ThreatForecastEngine(fusion_res, entities)
threats = f_engine.generate_forecasts()

import hashlib
print("Compiling personas list...")
personas_list = []
for e in entities:
    if e['score'] >= 66:
        eid = e['entity_id']
        seed = int(hashlib.md5(eid.encode()).hexdigest(), 16)
        sig_list = e.get('signals', [])
        signals_dict = {
            "call_spike": "Call frequency spike" in sig_list,
            "unusual_hours": "Unusual hours activity" in sig_list,
            "location_convergence": "Location convergence" in sig_list,
            "micro_splits": "Transaction micro-splits" in sig_list,
            "burner_contact": "New burner contact" in sig_list
        }
        entity_obj = {
            "id": eid,
            "heat_score": e['score'],
            "centrality": graph_engine.get_network_data()['nodes'][0].get('centrality', 0.5) if graph_engine.get_network_data()['nodes'] else 0,
            "archetype": "CRITICAL" if e['score'] >= 81 else "HIGH",
            "signals": signals_dict,
            "stats": {
                "total_calls": 10 + (seed % 50),
                "night_call_pct": 20 + (seed % 60),
                "avg_call_duration": 15 + (seed % 45),
                "total_transactions": 5 + (seed % 25),
                "avg_transaction": 500 + (seed % 4500),
                "location_convergence_count": 1 + (seed % 5),
                "active_days": 5 + (seed % 10),
                "unique_contacts": 3 + (seed % 15)
            }
        }
        if hasattr(graph_engine, 'get_centrality_scores'):
            entity_obj["centrality"] = graph_engine.get_centrality_scores().get(eid, 0)
        personas_list.append(entity_obj)

print("Kicking off profiler generation for all filtered entities...")
generated_personas = profiler.generate_all_personas(personas_list)
personas = {p['entity_id']: p for p in generated_personas}

print("Running PDF Document Assembly...")
timeline = get_suspicious_timeline()
pdf_buffer = generate_report(entities, threats, personas, timeline)
print(f"Success! PDF generated with size: {len(pdf_buffer)} bytes")
