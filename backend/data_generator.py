import json
import random
from datetime import datetime, timedelta
import os
import pandas as pd

NUM_ENTITIES = 20
NUM_DAYS = 7

def generate_data():
    entities = [f"E{str(i).zfill(3)}" for i in range(1, NUM_ENTITIES + 1)]
    start_date = datetime.now() - timedelta(days=NUM_DAYS)

    cdr_logs, chat_logs, transaction_logs, location_logs = [], [], [], []

    # Generate baseline data for everyone
    for entity in entities:
        # Give everyone some normal calls
        for _ in range(5):
            cdr_logs.append({
                "caller_id": entity,
                "receiver_id": random.choice([e for e in entities if e != entity]),
                "duration": random.randint(10, 60),
                "timestamp": (start_date + timedelta(days=random.randint(0, 6), hours=random.randint(8, 18))).isoformat()
            })
        # Give everyone some transactions
        for _ in range(3):
            transaction_logs.append({
                "account_id": entity,
                "amount": round(random.uniform(50.0, 300.0), 2),
                "type": "transfer",
                "timestamp": (start_date + timedelta(days=random.randint(0, 6), hours=10)).isoformat()
            })
        # Normal locations
        location_logs.append({
            "entity_id": entity,
            "latitude": 40.7128 + random.uniform(-0.1, 0.1),
            "longitude": -74.0060 + random.uniform(-0.1, 0.1),
            "timestamp": (start_date + timedelta(days=3, hours=12)).isoformat()
        })

    # ==========================
    # SEEDING: E001 (Coordinator, > 85)
    # Needs: Call Spike (20), Unusual Hours (20), New Burner (15), Transaction Micro-splits (25), Location Conv (20) = 100
    # 1. Call Spike: Need >3x average (which is ~1 per day). 5 calls in one day.
    for _ in range(10):
        cdr_logs.append({"caller_id": "E001", "receiver_id": "E002", "duration": 40, "timestamp": (start_date + timedelta(days=2, hours=14)).isoformat()})
    
    # 2. Unusual Hours: >30% between 22 and 4. We add 10 calls at 1 AM.
    for _ in range(10):
        cdr_logs.append({"caller_id": "E001", "receiver_id": "E003", "duration": 20, "timestamp": (start_date + timedelta(days=1, hours=2)).isoformat()})
    
    # 3. New Burner: Contact < 5 times, active < 4 days.
    chat_logs.append({"sender_id": "E001", "receiver_id": "BURNER1", "message_text": "hi", "timestamp": (start_date + timedelta(days=1, hours=12)).isoformat()})
    chat_logs.append({"sender_id": "E001", "receiver_id": "BURNER1", "message_text": "bye", "timestamp": (start_date + timedelta(days=2, hours=12)).isoformat()})
    # Make sure BURNER1 has no other logs.
    
    # 4. Transaction Micro-splits: >3 tx in same day between 500-1500.
    for _ in range(4):
        transaction_logs.append({"account_id": "E001", "amount": 800.0, "type": "transfer", "timestamp": (start_date + timedelta(days=3, hours=10)).isoformat()})
        
    # 5. Location Convergence: GPS within 0.01 of E002 same day.
    location_logs.append({"entity_id": "E001", "latitude": 40.7500, "longitude": -73.9800, "timestamp": (start_date + timedelta(days=4, hours=15)).isoformat()})
    location_logs.append({"entity_id": "E002", "latitude": 40.7501, "longitude": -73.9801, "timestamp": (start_date + timedelta(days=4, hours=15)).isoformat()})

    # ==========================
    # SEEDING: E002 (Mule, > 70)
    # Needs: Micro-splits (25), Location Conv (20), Call spike (20), Unusual hours (20) -> 85
    # 1. Micro-splits
    for _ in range(4):
        transaction_logs.append({"account_id": "E002", "amount": 600.0, "type": "deposit", "timestamp": (start_date + timedelta(days=3, hours=11)).isoformat()})
    # 2. Call spike
    for _ in range(10):
        cdr_logs.append({"caller_id": "E002", "receiver_id": "E004", "duration": 10, "timestamp": (start_date + timedelta(days=1, hours=14)).isoformat()})
    # 3. Unusual hours
    for _ in range(10):
        chat_logs.append({"sender_id": "E002", "receiver_id": "E009", "message_text": "yes", "timestamp": (start_date + timedelta(days=2, hours=3)).isoformat()})

    # ==========================
    # SEEDING: E009 (Gang, > 76)
    # Needs: transaction splits (25), Call spike (20), Unusual hours (20), Burner (15) -> 80
    for _ in range(4):
        transaction_logs.append({"account_id": "E009", "amount": 1000.0, "type": "transfer", "timestamp": (start_date + timedelta(days=5, hours=10)).isoformat()})
    for _ in range(10):
        cdr_logs.append({"caller_id": "E009", "receiver_id": "E008", "duration": 10, "timestamp": (start_date + timedelta(days=4, hours=14)).isoformat()})
    for _ in range(10):
        chat_logs.append({"sender_id": "E009", "receiver_id": "E010", "message_text": "ok", "timestamp": (start_date + timedelta(days=5, hours=1)).isoformat()})
    chat_logs.append({"sender_id": "E009", "receiver_id": "BURNER2", "message_text": "hi", "timestamp": (start_date + timedelta(days=2, hours=1)).isoformat()})

    # ==========================
    # SEEDING: E010 (Gang, > 75)
    # Needs: location conv (20), Micro-splits (25), Unusual hours (20), Burner (15) -> 80
    location_logs.append({"entity_id": "E010", "latitude": 40.7200, "longitude": -74.0100, "timestamp": (start_date + timedelta(days=6, hours=15)).isoformat()})
    location_logs.append({"entity_id": "E009", "latitude": 40.7201, "longitude": -74.0101, "timestamp": (start_date + timedelta(days=6, hours=15)).isoformat()})
    for _ in range(4):
        transaction_logs.append({"account_id": "E010", "amount": 1200.0, "type": "withdrawal", "timestamp": (start_date + timedelta(days=6, hours=11)).isoformat()})
    for _ in range(10):
        chat_logs.append({"sender_id": "E010", "receiver_id": "E009", "message_text": "go", "timestamp": (start_date + timedelta(days=6, hours=2)).isoformat()})
    chat_logs.append({"sender_id": "E010", "receiver_id": "BURNER3", "message_text": "do", "timestamp": (start_date + timedelta(days=1, hours=12)).isoformat()})

    # ==========================
    # SEEDING: E006 (Banker, > 68) 
    # Needs: Micro-splits (25), Call spike (20), Location conv (20) -> 65 (+ some random or just bump to 70 with Burner 15 -> 80)
    for _ in range(4):
        transaction_logs.append({"account_id": "E006", "amount": 900.0, "type": "deposit", "timestamp": (start_date + timedelta(days=2, hours=9)).isoformat()})
    for _ in range(10):
        cdr_logs.append({"caller_id": "E006", "receiver_id": "E001", "duration": 5, "timestamp": (start_date + timedelta(days=2, hours=10)).isoformat()})
    location_logs.append({"entity_id": "E006", "latitude": 40.7500, "longitude": -73.9800, "timestamp": (start_date + timedelta(days=4, hours=15)).isoformat()}) # converging with E001
    chat_logs.append({"sender_id": "E006", "receiver_id": "BURNER4", "message_text": "gugu", "timestamp": (start_date + timedelta(days=1, hours=12)).isoformat()})

    # ==========================
    # SEEDING: E012 (Ghost, > 58) 
    # Needs: Call spike (20), Unusual hours (20), Burner (15) -> 55 (close enough, maybe another 20 for loc conv = 75)
    for _ in range(10):
        cdr_logs.append({"caller_id": "E012", "receiver_id": "E010", "duration": 2, "timestamp": (start_date + timedelta(days=1, hours=14)).isoformat()})
    for _ in range(10):
        chat_logs.append({"sender_id": "E012", "receiver_id": "E011", "message_text": "boo", "timestamp": (start_date + timedelta(days=1, hours=3)).isoformat()})
    chat_logs.append({"sender_id": "E012", "receiver_id": "BURNER5", "message_text": "gugu", "timestamp": (start_date + timedelta(days=2, hours=12)).isoformat()})

    # ==========================
    # SEEDING: E015 (Normal, < 40)
    # Already receives only basic logs, will inherently score 0.

    os.makedirs("../data", exist_ok=True)
    pd.DataFrame(cdr_logs).sort_values("timestamp").to_csv("../data/CDR_Logs.csv", index=False)
    pd.DataFrame(chat_logs).sort_values("timestamp").to_csv("../data/Chat_Logs.csv", index=False)
    pd.DataFrame(transaction_logs).sort_values("timestamp").to_csv("../data/Transaction_Logs.csv", index=False)
    pd.DataFrame(location_logs).sort_values("timestamp").to_csv("../data/Location_Logs.csv", index=False)
    print(f"Generated strict dataset with {len(entities)} entities across 4 CSVs.")

if __name__ == "__main__":
    generate_data()
