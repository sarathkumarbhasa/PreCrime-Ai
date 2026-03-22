import sys
import json
import os

sys.path.append('backend')
from persona_profiler import PersonaProfiler

if os.path.exists('backend/.env'):
    with open('backend/.env', 'r') as f:
        for line in f:
            if line.startswith('OPENROUTER_API_KEY'):
                os.environ['OPENROUTER_API_KEY'] = line.split('=')[1].strip().strip('"').strip("'")
elif os.path.exists('.env'):
    with open('.env', 'r') as f:
        for line in f:
            if line.startswith('OPENROUTER_API_KEY'):
                os.environ['OPENROUTER_API_KEY'] = line.split('=')[1].strip().strip('"').strip("'")

profiler = PersonaProfiler()

test_entity = {
    "id": "E006",
    "heat_score": 88,
    "centrality": 0.18,
    "archetype": "HIGH",
    "signals": {
        "call_spike": True,
        "unusual_hours": True,
        "location_convergence": False,
        "micro_splits": True,
        "burner_contact": False
    },
    "stats": {
        "total_calls": 34,
        "night_call_pct": 72,
        "avg_call_duration": 12,
        "total_transactions": 8,
        "avg_transaction": 940,
        "location_convergence_count": 0,
        "active_days": 18,
        "unique_contacts": 9
    }
}

print("Testing OpenRouter Profile Generation...")
result = profiler.generate_persona(test_entity)

print("\n--- RAW OPENROUTER JSON RESPONSE ---")
print(json.dumps(result, indent=2))
print("------------------------------------")
