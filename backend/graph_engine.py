import json
import networkx as nx
import os

class GraphEngine:
    def __init__(self, data_path="../data/sample_dataset.json"):
        self.data_path = data_path
        self.graph = nx.Graph()
        self.data = self._load_data()
        self._build_graph()

    def _load_data(self):
        if not os.path.exists(self.data_path):
            return {"entities": [], "cdr_logs": [], "chat_logs": [], "transaction_logs": [], "location_logs": []}
        try:
            with open(self.data_path, "r") as f:
                return json.load(f)
        except Exception:
            return {"entities": [], "cdr_logs": [], "chat_logs": [], "transaction_logs": [], "location_logs": []}

    def _build_graph(self):
        # We must load all 20 entities ensuring none are missing
        entities = self.data.get("entities", [])
        if not entities:
            print("WARNING: Nodes or edges are empty. CSV has likely not been loaded yet.")
        for entity in entities:
            self.graph.add_node(entity)

        for log in self.data.get("cdr_logs", []):
            caller = log.get("caller_id")
            receiver = log.get("receiver_id")
            if not caller or not receiver or caller == 'nan' or receiver == 'nan': continue
            if caller not in self.graph: self.graph.add_node(caller)
            if receiver not in self.graph: self.graph.add_node(receiver)
            if self.graph.has_edge(caller, receiver):
                self.graph[caller][receiver]['weight'] += 1
            else:
                self.graph.add_edge(caller, receiver, weight=1)

        for log in self.data.get("chat_logs", []):
            sender = log.get("sender_id")
            receiver = log.get("receiver_id")
            if not sender or not receiver or sender == 'nan' or receiver == 'nan': continue
            if sender not in self.graph: self.graph.add_node(sender)
            if receiver not in self.graph: self.graph.add_node(receiver)
            if self.graph.has_edge(sender, receiver):
                self.graph[sender][receiver]['weight'] += 1
            else:
                self.graph.add_edge(sender, receiver, weight=1)
                
        print(f"Graph initialization complete. Loaded {self.graph.number_of_nodes()} total entities from CSV sets.")

    def get_centrality_scores(self):
        try:
            import networkx as nx
            return nx.betweenness_centrality(self.graph, normalized=True)
        except Exception:
            return {}

    def get_clustering_coefficients(self):
        try:
            import networkx as nx
            return nx.clustering(self.graph)
        except Exception:
            return {}
            
    def get_centrality_scores(self):
        try:
            import networkx as nx
            return nx.betweenness_centrality(self.graph, normalized=True)
        except Exception:
            return {}

    def get_clustering_coefficients(self):
        try:
            import networkx as nx
            return nx.clustering(self.graph)
        except Exception:
            return {}
            
    def get_network_data(self):
        try:
            from heat_score import HeatScoreEngine
            he = HeatScoreEngine(self.data_path)
            heat_scores = he.calculate_scores()
            heat_map = {item["entity_id"]: item["score"] for item in heat_scores}
        except Exception as e:
            print(f"Error computing heat scores for graph engine {e}")
            heat_map = {}

        nodes = []
        for node in self.graph.nodes():
            nodes.append({
                "id": node,
                "label": node,
                "heat_score": heat_map.get(node, 0)
            })
            
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "source": u,
                "target": v,
                "weight": data.get("weight", 1)
            })
            
        return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    engine = GraphEngine()
    print(f"Graph built with {engine.graph.number_of_nodes()} nodes.")
