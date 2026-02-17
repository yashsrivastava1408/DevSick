"""Service dependency graph API endpoint."""
from fastapi import APIRouter
from ..knowledge.dependency_graph import dependency_graph

router = APIRouter(prefix="/api", tags=["Graph"])


@router.get("/graph")
async def get_graph():
    """Get the full service dependency graph."""
    return dependency_graph.to_dict()


@router.get("/graph/impact/{service_id}")
async def get_impact(service_id: str):
    """Get the impact path for a specific service failure."""
    path = dependency_graph.get_impact_path(service_id)
    return {
        "root_service": service_id,
        "impact_path": path,
        "total_affected": len(path),
    }
