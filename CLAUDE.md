# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Klances** is a read-only WebUI dashboard for Kubernetes cluster monitoring — "the Glances of Kubernetes". It targets both end-users unfamiliar with Kubernetes and cluster admins/developers who want a quick status overview.

## Technology Stack

- **Backend**: Python, FastAPI, Kubernetes Python Client (`kubernetes`)
- **Frontend**: Vue.js, eCharts, Tailwind CSS

## Planned Architecture

The app has two main components:

### Backend (`/api`)

- FastAPI application exposing a REST API
- Uses the Kubernetes Python Client to read cluster data (nodes, namespaces, pods, services, ingresses, events, logs)
- Read-only — no mutations to the cluster
- Connects via `kubeconfig` (local dev) or in-cluster service account

### Frontend (`/frontend`)

- Vue.js SPA
- Layout is a series of stacked horizontal full-width panels, shown progressively based on selection:
  1. **Top menu**: cluster name, cluster status, refresh button + auto-refresh interval (default 5s)
  2. **Panel 1** (always visible, 2 columns): Node list (roles, version, CPU, Memory) | Namespace list (status, CPU, Memory, Pod count)
  3. **Panel 2** (appears when a namespace is selected): Pod list (status, CPU, Memory with current/requested/limit, IP, node)
  4. **Panel 3** (appears when a pod is selected): Pod details — services/ingress, events, logs
  5. **Bottom menu**: GitHub link, license info
- eCharts for data visualization
- Tailwind CSS for styling

### API Design

The REST API should expose the same hierarchical data the frontend displays:

- `GET /api/cluster` — cluster info and status
- `GET /api/nodes` — node list with resources
- `GET /api/namespaces` — namespace list with aggregated resources
- `GET /api/namespaces/{namespace}/pods` — pod list for a namespace
- `GET /api/namespaces/{namespace}/pods/{pod}` — pod details (services, ingress, events, logs)

### Files structure

- src/
  - api/ (FastAPI app)
  - frontend/ (Vue.js app)
- Makefile (for development commands)
- .git/workflows/ (CI/CD pipelines)
- tests/ (unit and integration tests, based on Pytest for backend, Jest for frontend)

## Development Setup

```bash
make install   # create venv and install all dependencies (first time)
make run       # start API server at http://localhost:8000 (auto-reload)
make test      # run all Pytest tests
make test-one TEST=tests/test_cluster.py  # run a single test file
make lint      # ruff linter
make format    # ruff formatter
```

- Python virtualenv in `venv/`, managed via `pyproject.toml` (`pip install -e ".[dev]"`)
- Kubernetes access: `~/.kube/config` in dev, in-cluster service account in production
- OpenAPI docs available at `http://localhost:8000/docs` when running
- Frontend (Vue.js + Vite): `npm install && npm run dev` in `src/frontend/` — served by FastAPI from `src/frontend/dist/` in production

## Architectural Considerations

- Read-only design simplifies security and permissions
- FastAPI provides a modern, async backend framework with automatic OpenAPI docs
- Vue.js allows for a dynamic, responsive frontend with component-based architecture
- eCharts offers powerful data visualization capabilities for resource usage metrics
- Tailwind CSS enables rapid styling with utility classes, ensuring a clean and responsive UI
- WebUI, documentation and code commets should be written in English

## License

Klances is licensed under the MIT License. See the LICENSE file for more details.