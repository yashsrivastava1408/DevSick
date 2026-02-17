"""Service dependency graph / knowledge graph.

Represents the directed relationships between infrastructure services.
Used by the correlation engine and AI reasoning layer to understand
cascading failure patterns.
"""
import json
import os
from typing import List, Dict, Optional, Set


class ServiceNode:
    """A node in the service dependency graph."""

    def __init__(self, id: str, name: str, service_type: str, tier: str):
        self.id = id
        self.name = name
        self.service_type = service_type
        self.tier = tier

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.service_type,
            "tier": self.tier,
        }


class DependencyEdge:
    """A directed edge in the dependency graph."""

    def __init__(self, from_service: str, to_service: str, relation: str):
        self.from_service = from_service
        self.to_service = to_service
        self.relation = relation

    def to_dict(self) -> Dict:
        return {
            "from": self.from_service,
            "to": self.to_service,
            "relation": self.relation,
        }


class DependencyGraph:
    """Directed graph of service dependencies."""

    def __init__(self):
        self.nodes: Dict[str, ServiceNode] = {}
        self.edges: List[DependencyEdge] = []
        self._adjacency: Dict[str, List[str]] = {}  # from -> [to]
        self._reverse: Dict[str, List[str]] = {}     # to -> [from]

    def load_from_file(self, filepath: Optional[str] = None):
        """Load the graph from the service_graph.json file."""
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(__file__), "..", "data", "service_graph.json"
            )

        with open(filepath, "r") as f:
            data = json.load(f)

        for svc in data.get("services", []):
            node = ServiceNode(
                id=svc["id"],
                name=svc["name"],
                service_type=svc["type"],
                tier=svc["tier"],
            )
            self.nodes[node.id] = node
            self._adjacency.setdefault(node.id, [])
            self._reverse.setdefault(node.id, [])

        for dep in data.get("dependencies", []):
            edge = DependencyEdge(
                from_service=dep["from"],
                to_service=dep["to"],
                relation=dep["relation"],
            )
            self.edges.append(edge)
            self._adjacency.setdefault(dep["from"], []).append(dep["to"])
            self._reverse.setdefault(dep["to"], []).append(dep["from"])

    def get_upstream(self, service_id: str) -> List[str]:
        """Get services that this service depends on (upstream)."""
        return self._adjacency.get(service_id, [])

    def get_downstream(self, service_id: str) -> List[str]:
        """Get services that depend on this service (downstream)."""
        return self._reverse.get(service_id, [])

    def get_impact_path(self, root_service: str) -> List[str]:
        """Get all services impacted by a failure in root_service (BFS downstream)."""
        visited: Set[str] = set()
        queue = [root_service]
        path = []

        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            path.append(current)
            for downstream in self.get_downstream(current):
                if downstream not in visited:
                    queue.append(downstream)

        return path

    def get_dependency_chain(self, from_service: str, to_service: str) -> List[str]:
        """Find the dependency chain between two services (BFS)."""
        visited: Set[str] = set()
        queue = [(from_service, [from_service])]

        while queue:
            current, current_path = queue.pop(0)
            if current == to_service:
                return current_path
            if current in visited:
                continue
            visited.add(current)
            for upstream in self.get_upstream(current):
                if upstream not in visited:
                    queue.append((upstream, current_path + [upstream]))

        return []

    def to_dict(self) -> Dict:
        """Serialize the graph to dict format."""
        return {
            "services": [node.to_dict() for node in self.nodes.values()],
            "dependencies": [edge.to_dict() for edge in self.edges],
        }

    def get_service_context(self, service_ids: List[str]) -> str:
        """Generate a human-readable description of services and their relationships."""
        lines = ["Service Dependency Context:"]
        for sid in service_ids:
            node = self.nodes.get(sid)
            if node:
                upstream = self.get_upstream(sid)
                downstream = self.get_downstream(sid)
                lines.append(
                    f"- {node.name} ({node.id}): "
                    f"depends on [{', '.join(upstream)}], "
                    f"depended on by [{', '.join(downstream)}]"
                )
        return "\n".join(lines)


# Global singleton - loaded on import
dependency_graph = DependencyGraph()
dependency_graph.load_from_file()
