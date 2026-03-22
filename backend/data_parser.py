import json
import os
import pandas as pd

def parse_csv_data():
    dataset = {
        "entities": [], "cdr_logs": [], "chat_logs": [], 
        "transaction_logs": [], "location_logs": []
    }
    entities_set = set()
    
    def normalize_cols(df):
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        return df

    if os.path.exists("../data/CDR_Logs.csv"):
        df = pd.read_csv("../data/CDR_Logs.csv")
        df = normalize_cols(df)
        if 'timestamp' in df.columns: 
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%S')
        for _, row in df.iterrows():
            caller = str(row.get('caller_id', ''))
            receiver = str(row.get('receiver_id', ''))
            if caller == 'nan' or receiver == 'nan': continue
            dataset["cdr_logs"].append({
                "caller_id": caller, "receiver_id": receiver,
                "duration": int(row.get('duration', 0)), "timestamp": str(row.get('timestamp', ''))
            })
            entities_set.update([caller, receiver])
                
    if os.path.exists("../data/Chat_Logs.csv"):
        df = pd.read_csv("../data/Chat_Logs.csv")
        df = normalize_cols(df)
        if 'timestamp' in df.columns: 
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%S')
        for _, row in df.iterrows():
            sender = str(row.get('sender_id', ''))
            receiver = str(row.get('receiver_id', ''))
            if sender == 'nan' or receiver == 'nan': continue
            dataset["chat_logs"].append({
                "sender_id": sender, "receiver_id": receiver,
                "message_text": str(row.get('message_text', '')), "timestamp": str(row.get('timestamp', ''))
            })
            entities_set.update([sender, receiver])
                
    if os.path.exists("../data/Transaction_Logs.csv"):
        df = pd.read_csv("../data/Transaction_Logs.csv")
        df = normalize_cols(df)
        if 'timestamp' in df.columns: 
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%S')
        for _, row in df.iterrows():
            account = str(row.get('account_id', ''))
            if account == 'nan': continue
            dataset["transaction_logs"].append({
                "account_id": account, "amount": float(row.get('amount', 0.0)),
                "type": str(row.get('type', '')), "timestamp": str(row.get('timestamp', ''))
            })
            entities_set.add(account)
                
    if os.path.exists("../data/Location_Logs.csv"):
        df = pd.read_csv("../data/Location_Logs.csv")
        df = normalize_cols(df)
        if 'timestamp' in df.columns: 
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce').dt.strftime('%Y-%m-%dT%H:%M:%S')
        for _, row in df.iterrows():
            entity = str(row.get('entity_id', ''))
            if entity == 'nan': continue
            dataset["location_logs"].append({
                "entity_id": entity, "latitude": float(row.get('latitude', 0.0)),
                "longitude": float(row.get('longitude', 0.0)), "timestamp": str(row.get('timestamp', ''))
            })
            entities_set.add(entity)
                    
    dataset["entities"] = sorted(list(e for e in entities_set if e and str(e) != 'nan'))
    os.makedirs("../data", exist_ok=True)
    with open("../data/sample_dataset.json", "w") as f:
        json.dump(dataset, f, indent=2)
    print(f"Parsed {len(dataset['entities'])} entities.")

if __name__ == "__main__":
    parse_csv_data()
