import os
import json
import time

def parse_gemini_json(raw_text: str) -> dict:
    text = raw_text.strip()
    
    # Case 1: wrapped in ```json ... ```
    if "```json" in text:
        text = text.split("```json")[1]
        text = text.split("```")[0]
    
    # Case 2: wrapped in ``` ... ```
    elif "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    
    # Case 3: has extra text before {
    if "{" in text:
        text = text[text.index("{"):]
    
    # Case 4: has extra text after }
    if "}" in text:
        text = text[:text.rindex("}")+1]
    
    text = text.strip()
    return json.loads(text)

class PersonaProfiler:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.api_key = os.environ.get("OPENROUTER_API_KEY")
        self.model = None
        if self.api_key:
            self.model = "google/gemini-2.0-flash-001"
        self._persona_cache = {}

    def _fallback_persona(self, entity, active_count):
        c = entity['centrality']
        sigs = entity['signals']
        call_spike = sigs.get('call_spike', False)
        micro_splits = sigs.get('micro_splits', False)
        burner_contact = sigs.get('burner_contact', False)
        location_convergence = sigs.get('location_convergence', False)
        active_days = entity.get('stats', {}).get('active_days', 10)
        
        if c >= 0.12 and call_spike: arch = "The Coordinator"
        elif micro_splits and c < 0.10: arch = "The Banker"
        elif burner_contact or active_days < 5: arch = "The Ghost"
        elif location_convergence and c < 0.12: arch = "The Enforcer"
        else: arch = "The Mule"

        return {
            "entity_id": entity['id'],
            "heat_score": entity['heat_score'],
            "archetype_label": arch,
            "confidence_statement": f"Behavioral profile based on {active_count} confirmed threat signals.",
            "behavioral_summary": f"Entity {entity['id']} exhibits {active_count} active threat indicators with heat score {entity['heat_score']}/100. Network centrality of {entity['centrality']:.2f} suggests {'central coordination role' if entity['centrality'] > 0.3 else 'peripheral support role'}.",
            "risk_assessment": "Further monitoring required.",
            "recommended_action": "Maintain surveillance and cross-reference with known criminal databases.",
            "signals": entity['signals'],
            "centrality": entity['centrality'],
            "active_count": active_count
        }

    def generate_persona(self, entity: dict) -> dict:
        entity_id = entity['id']
        if entity_id in self._persona_cache:
            return self._persona_cache[entity_id]

        active = [k for k,v in entity['signals'].items() if v]
        active_count = len(active)
        
        if not self.model:
            fallback = self._fallback_persona(entity, active_count)
            self._persona_cache[entity_id] = fallback
            return fallback

        prompt = f"""You are a criminal intelligence analyst.
Return ONLY a JSON object. No markdown. No explanation.

Suspect {entity['id']} metrics:
- Heat Score: {entity['heat_score']}/100
- Centrality: {entity['centrality']:.2f}
- Active signals: {active_count}/5
- call_spike: {entity['signals'].get('call_spike', False)}
- unusual_hours: {entity['signals'].get('unusual_hours', False)}
- location_convergence: {entity['signals'].get('location_convergence', False)}
- micro_splits: {entity['signals'].get('micro_splits', False)}
- burner_contact: {entity['signals'].get('burner_contact', False)}
- Stats: {json.dumps(entity.get('stats', {}))}

ARCHETYPE SELECTION — follow these rules exactly:
IF centrality >= 0.12 AND call_spike = True 
  → archetype_label = "The Coordinator"
ELSE IF micro_splits = True AND centrality < 0.10 
  → archetype_label = "The Banker"
ELSE IF burner_contact = True OR active_days < 5 
  → archetype_label = "The Ghost"
ELSE IF location_convergence = True AND centrality < 0.12 
  → archetype_label = "The Enforcer"
ELSE 
  → archetype_label = "The Mule"

Apply the FIRST matching rule to this suspect.

Return this exact JSON:
{{
  "archetype_label": "The Mule",
  "confidence_statement": "one sentence",
  "behavioral_summary": "three sentences using actual stats",
  "risk_assessment": "one sentence",
  "recommended_action": "one sentence"
}}"""

        try:
            print(f"Calling OpenRouter for {entity['id']}...")
            import requests
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "PreCrime AI",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [{"role": "system", "content": "You are a criminal intelligence analyst. Always respond with valid JSON only. No markdown."}, {"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"}
                }
            )
            
            resp_data = response.json()
            if 'choices' in resp_data:
                raw = resp_data['choices'][0]['message']['content']
            elif 'error' in resp_data:
                print(f"OpenRouter Error Payload: {resp_data['error']}")
                raise Exception(str(resp_data['error']))
            else:
                raise Exception(f"Unknown OpenRouter response: {resp_data}")
                
            print(f"Raw OpenRouter response for {entity['id']}: {raw[:100]}...")
            
            result = parse_gemini_json(raw)
            print(f"Parsed successfully for {entity['id']}: {result.get('archetype_label')}")
            
            result['entity_id'] = entity['id']
            result['heat_score'] = entity['heat_score']
            result['signals'] = entity['signals']
            result['centrality'] = entity['centrality']
            result['active_count'] = active_count
            
            self._persona_cache[entity_id] = result
            return result
            
        except Exception as e:
            print(f"OPENROUTER FAILED for {entity['id']}: {type(e).__name__}: {e}")
            fallback = self._fallback_persona(entity, active_count)
            self._persona_cache[entity_id] = fallback
            return fallback

    def generate_all_personas(self, entities: list) -> list:
        personas = []
        archetype_map = {
            "The Coordinator": "Coordinator",
            "The Mule":        "Mule",
            "The Ghost":       "Ghost",
            "The Banker":      "Banker",
            "The Enforcer":    "Enforcer"
        }
        for entity in entities:
            was_cached = entity['id'] in self._persona_cache
            persona = self.generate_persona(entity)
            
            # Update archetype from Gemini result for consistent UI rendering downstream
            raw_label = persona.get('archetype_label', 'Unknown')
            entity['archetype'] = archetype_map.get(raw_label, raw_label)
            persona['archetype_label'] = entity['archetype'] # synchronize immediately
            
            personas.append(persona)
            if self.model and not was_cached:
                time.sleep(1)
        return personas

    def generate_profile(self, entity_id, metrics):
        import hashlib
        seed = int(hashlib.md5(entity_id.encode()).hexdigest(), 16)
        entity = {
            "id": entity_id,
            "heat_score": metrics.get("heat_score", 0),
            "centrality": metrics.get("centrality", 0.0),
            "archetype": "High Risk" if metrics.get("heat_score", 0) >= 66 else "Normal",
            "signals": {
                "call_spike": (seed % 2 == 0),
                "unusual_hours": (seed % 3 == 0),
                "location_convergence": (seed % 5 == 0),
                "micro_splits": (seed % 7 == 0),
                "burner_contact": (seed % 11 == 0)
            },
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
        res = self.generate_persona(entity)
        return {
            "archetype": res.get("archetype_label", "Unknown"),
            "summary": res.get("behavioral_summary", "")
        }

    def generate_report(self, entity_id, metrics):
        return {
            "title": f"REPORT: {entity_id} - {metrics.get('heat_score', 0)}",
            "content": self.generate_profile(entity_id, metrics).get('summary', '')
        }

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.environ.get("OPENROUTER_API_KEY")
    print(f"API Key loaded: {'YES' if api_key else 'NO - KEY MISSING'}")
    print(f"Key preview: {api_key[:8]}..." if api_key else "")
    
    if api_key:
        try:
            print("Sending test request to OpenRouter...")
            import urllib.request
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "http://localhost:3000",
                    "X-Title": "PreCrime AI Debug",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [{"role": "user", "content": "Say exactly: OPENROUTER_CONNECTED"}]
                }).encode("utf-8")
            )
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"OpenRouter response: {result['choices'][0]['message']['content']}")
        except Exception as e:
            print(f"OpenRouter FAILED: {type(e).__name__}: {e}")
