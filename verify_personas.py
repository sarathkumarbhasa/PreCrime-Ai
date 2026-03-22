import sys
sys.path.append('backend')
from heat_score import HeatScoreEngine
from persona_profiler import PersonaProfiler
from graph_engine import GraphEngine
import hashlib

heat_engine = HeatScoreEngine('data/sample_dataset.json')
graph_engine = GraphEngine('data/sample_dataset.json')
profiler = PersonaProfiler()

entities = heat_engine.calculate_scores()

personas_list = []
for e in entities:
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

print("Generating personas via OpenRouter Proxy...")
generated_personas = profiler.generate_all_personas(personas_list)
personas = {p['entity_id']: p for p in generated_personas}

for e in entities:
    eid = e['entity_id']
    if eid in personas:
        raw = personas[eid].get('archetype_label', 'Unknown')
        e['archetype'] = raw.replace("The ", "").strip()
    else:
        e['archetype'] = 'Unknown'

print("\nEntity   Score   Level      Archetype       Signals")
print("------   -----   --------   ------------    -------")
for e in sorted(entities, key=lambda x: x['score'], reverse=True):
    score = e['score']
    level = "CRITICAL" if score >= 81 else ("HIGH" if score >= 66 else ("WATCH" if score >= 40 else "NORMAL"))
    arch = e.get('archetype', 'Unknown')
    sigs = len(e.get('signals', []))
    print(f"{e['entity_id']:<8} {score:<7} {level:<10} {arch:<15} {sigs}")
