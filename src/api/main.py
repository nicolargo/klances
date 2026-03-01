from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .routers import cluster, namespaces, nodes, pods, status

API_PREFIX = "/api/1"

app = FastAPI(
    title="Klances API",
    description="Kubernetes cluster monitoring REST API",
    version="0.1.0",
    docs_url=f"{API_PREFIX}/docs",
    redoc_url=f"{API_PREFIX}/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json",
)

# Allow the Vite dev server to call the API during frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(status.router, prefix=API_PREFIX, tags=["status"])
app.include_router(cluster.router, prefix=API_PREFIX, tags=["cluster"])
app.include_router(nodes.router, prefix=API_PREFIX, tags=["nodes"])
app.include_router(namespaces.router, prefix=API_PREFIX, tags=["namespaces"])
app.include_router(pods.router, prefix=API_PREFIX, tags=["pods"])

# Serve the built Vue.js frontend when it exists
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
