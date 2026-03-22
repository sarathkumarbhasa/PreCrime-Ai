import sys
import json
sys.path.append('backend')
from heat_score import HeatScoreEngine

engine = HeatScoreEngine('data/sample_dataset.json')
scores = engine.calculate_scores()

e011 = next((e for e in scores if e['entity_id'] == 'E011'), None)
if e011:
    print(f"E011: score={e011['score']}, signals={len(e011['signals'])}")

max_score = max(e['score'] for e in scores)
print(f"Max score: {max_score}")

from report_generator import generate_report

timeline = [
    {"timestamp": "2026-03-21T10:00:00", "entity": "E001", "type": "Call", "source": "CDR", "severity": "High", "desc": "Call to E002"},
    {"timestamp": "2026-03-21T10:00:00", "entity": "E001", "type": "Call", "source": "CDR", "severity": "High", "desc": "Call to E002"}
]

try:
    pdf = generate_report(scores, [], {}, timeline)
    print(f"PDF generated: {len(pdf)} bytes")
except Exception as e:
    print(f"Error generating PDF: {e}")
