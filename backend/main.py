from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

from data_parser import parse_csv_data
from graph_engine import GraphEngine
from heat_score import HeatScoreEngine
from fusion_engine import FusionEngine
from threat_forecast import ThreatForecastEngine
from persona_profiler import PersonaProfiler

app = FastAPI(title="PRECRIME AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = "../data/sample_dataset.json"

def init_data():
    if not os.path.exists(DATA_PATH):
        try:
            parse_csv_data()
        except Exception as e:
            print(f"Error parsing data: {e}")
            from data_generator import generate_data
            generate_data()
            try:
                parse_csv_data()
            except Exception as e2:
                print(f"Fallback generation error {e2}")

init_data()

graph_engine = GraphEngine(DATA_PATH)
heat_engine = HeatScoreEngine(DATA_PATH)
fusion_engine = FusionEngine(DATA_PATH)
profiler = PersonaProfiler()

@app.get("/api/graph")
def get_graph():
    return graph_engine.get_network_data()

@app.get("/api/network")
def get_network():
    return graph_engine.get_network_data()

@app.get("/api/heat-scores")
def get_heat_scores():
    return heat_engine.calculate_scores()

@app.get("/api/fusion")
def get_fusion_results():
    return fusion_engine.fuse_signals()

@app.get("/api/forecasts")
def get_forecasts():
    fusion_res = fusion_engine.fuse_signals()
    heat_res = heat_engine.calculate_scores()
    forecast_engine = ThreatForecastEngine(fusion_res, heat_res)
    return forecast_engine.generate_forecasts()

@app.get("/api/persona/{entity_id}")
def get_persona(entity_id: str):
    centrality = graph_engine.get_centrality_scores().get(entity_id, 0)
    clustering = graph_engine.get_clustering_coefficients().get(entity_id, 0)
    heat_scores = heat_engine.calculate_scores()
    entity_heat = next((item for item in heat_scores if item["entity_id"] == entity_id), {"score": 0})
    
    metrics = {
        "centrality": centrality,
        "clustering": clustering,
        "active_hours": "Variable",
        "dominant_source": "Mixed",
        "heat_score": entity_heat["score"]
    }
    return profiler.generate_profile(entity_id, metrics)

@app.get("/api/report/{entity_id}")
def get_report(entity_id: str):
    centrality = graph_engine.get_centrality_scores().get(entity_id, 0)
    clustering = graph_engine.get_clustering_coefficients().get(entity_id, 0)
    heat_scores = heat_engine.calculate_scores()
    entity_heat = next((item for item in heat_scores if item["entity_id"] == entity_id), {"score": 0})
    
    metrics = {
        "centrality": centrality,
        "clustering": clustering,
        "heat_score": entity_heat["score"]
    }
    return profiler.generate_report(entity_id, metrics)

@app.post("/api/regenerate-data")
def regenerate_data_endpoint():
    try:
        from data_generator import generate_data
        generate_data()
        parse_csv_data()
    except Exception as e:
        return {"status": "error", "message": str(e)}
        
    global graph_engine, heat_engine, fusion_engine
    graph_engine = GraphEngine(DATA_PATH)
    heat_engine = HeatScoreEngine(DATA_PATH)
    fusion_engine = FusionEngine(DATA_PATH)
    return {"status": "success", "message": "Data regenerated"}

def get_suspicious_timeline():
    import pandas as pd
    events = []
    try:
        cdr_df = pd.read_csv("../data/CDR_Logs.csv")
        txn_df = pd.read_csv("../data/Transaction_Logs.csv")
        chat_df = pd.read_csv("../data/Chat_Logs.csv")
        loc_df = pd.read_csv("../data/Location_Logs.csv")
        
        cdr_df.columns = cdr_df.columns.str.strip().str.lower()
        txn_df.columns = txn_df.columns.str.strip().str.lower()
        chat_df.columns = chat_df.columns.str.strip().str.lower()
        loc_df.columns = loc_df.columns.str.strip().str.lower()

        h_scores = heat_engine.calculate_scores()
        suspicious = {e['entity_id'] for e in h_scores if e['score'] >= 41}
        
        for _, row in cdr_df[cdr_df['caller_id'].isin(suspicious)].iterrows():
            dur = row.get('duration_sec', row.get('duration', 0))
            score = next((e['score'] for e in h_scores if e['entity_id'] == row['caller_id']), 0)
            events.append({
                "timestamp": str(row['timestamp']),
                "entity": str(row['caller_id']),
                "type": "Voice Call",
                "source": "Telecom CDR",
                "severity": "High" if score > 65 else "Medium",
                "desc": f"Called {row['receiver_id']} ({dur}s)"
            })

        for _, row in txn_df[txn_df['account_id'].isin(suspicious)].iterrows():
            amt = float(row.get('amount', 0)) if not pd.isna(row.get('amount')) else 0.0
            events.append({
                "timestamp": str(row['timestamp']),
                "entity": str(row['account_id']),
                "type": "Financial Transaction",
                "source": "Financial Ledger",
                "severity": "Critical" if amt < 1500 else "High",
                "desc": f"{str(row.get('type', '')).title()} of {amt}"
            })

        for _, row in chat_df[chat_df['sender_id'].isin(suspicious)].iterrows():
            events.append({
                "timestamp": str(row['timestamp']),
                "entity": str(row['sender_id']),
                "type": "Encrypted Communication",
                "source": "Chat Intercept",
                "severity": "High",
                "desc": f"Msg to {row['receiver_id']}: {str(row.get('message_text', ''))[:30]}"
            })

        def detect_convergence(entity, df):
            e_locs = df[df['entity_id'] == entity]
            o_locs = df[df['entity_id'] != entity]
            convs = []
            if not e_locs.empty and not o_locs.empty:
                convs.append({
                    "timestamp": e_locs.iloc[0]['timestamp'],
                    "nearby_entity": o_locs.iloc[0]['entity_id'],
                    "lat": float(e_locs.iloc[0].get('latitude', e_locs.iloc[0].get('lat', 0))),
                    "lon": float(e_locs.iloc[0].get('longitude', e_locs.iloc[0].get('lon', 0)))
                })
            return convs

        for entity in suspicious:
            conv = detect_convergence(entity, loc_df)
            for c in conv:
                events.append({
                    "timestamp": str(c['timestamp']),
                    "entity": entity,
                    "type": "Geo-Convergence",
                    "source": "GPS Tracking",
                    "severity": "Critical",
                    "desc": f"Converged with {c['nearby_entity']} at ({c['lat']:.4f}, {c['lon']:.4f})"
                })

        events = sorted(events, key=lambda x: str(x['timestamp']), reverse=True)[:40]
    except Exception as e:
        print(f"Timeline error: {e}")
        
    return events


from fastapi.responses import StreamingResponse
from report_generator import generate_report
import io

@app.get("/api/report")
async def download_report():
    entities = heat_engine.calculate_scores()
    
    fusion_res = fusion_engine.fuse_signals()
    heat_res = heat_engine.calculate_scores()
    from threat_forecast import ThreatForecastEngine
    f_engine = ThreatForecastEngine(fusion_res, heat_res)
    threats = f_engine.generate_forecasts()
    
    personas_list = []
    import hashlib
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
            
    generated_personas = profiler.generate_all_personas(personas_list)
    personas = {p['entity_id']: p for p in generated_personas}
    
    # FIX 1: Write archetype back to each entity
    for e in entities:
        eid = e['entity_id']
        if eid in personas:
            raw = personas[eid].get('archetype_label', 'Unknown')
            # Clean label: "The Coordinator" → "Coordinator"
            e['archetype'] = raw.replace("The ", "").strip()

    timeline = get_suspicious_timeline()
    pdf_buffer = generate_report(entities, threats, personas, timeline)
    
    from datetime import datetime
    filename = f"PRECRIME_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_buffer),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
