# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Klances** is a read-only WebUI dashboard for Kubernetes cluster monitoring — "the Glances of Kubernetes". It targets both end-users unfamiliar with Kubernetes and cluster admins/developers who want a quick status overview.

## Technology Stack

- **Backend**: Python 3.10+, FastAPI, Kubernetes Python Client (`kubernetes`)
- **Frontend**: Vue.js 3, Vite, Pinia, eCharts, Tailwind CSS v4
- **Deployment**: Docker (multi-stage), Helm chart, GitHub Actions CI/CD

## Architecture

Single-service architecture: FastAPI serves both the REST API and the pre-built Vue.js frontend on a single port.

### Backend (`src/api/`)

- FastAPI application exposing a REST API under `/api/1/`
- Uses the Kubernetes Python Client to read cluster data (nodes, namespaces, pods, services, ingresses, events, logs, metrics)
- Read-only — no mutations to the cluster
- Connects via `kubeconfig` (local dev) or in-cluster service account (production)
- Resilient K8s client: never crashes on init, auto-reconnects, surfaces errors via API

### Frontend (`src/frontend/`)

- Vue.js 3 SPA served at `/frontend/` by FastAPI (from `src/frontend/dist/`)
- Layout: stacked horizontal panels, shown progressively based on selection:
  1. **Top menu**: cluster name, status badge, dark/light theme toggle, auto-refresh interval
  2. **Panel 1** (always visible, 2 columns): Node list | Namespace list
  3. **Panel 2** (on namespace selection): Pod list
  4. **Panel 3** (on pod selection): Pod details (services, ingresses, events, logs)
  5. **Bottom menu**: GitHub link, license info
- Dark theme by default, light theme available (CSS custom properties in `style.css`)
- Theme colors must use CSS custom properties (`var(--...)`) and `k-*` CSS classes, NOT hardcoded Tailwind color classes — this ensures both dark and light themes work correctly

### API Endpoints (all GET, read-only)

- `GET /api/1/status` — API health check + cluster reachability
- `GET /api/1/cluster` — cluster info and status
- `GET /api/1/nodes` — node list with resources
- `GET /api/1/namespaces` — namespace list with aggregated resources
- `GET /api/1/namespaces/{ns}/pods` — pod list for a namespace
- `GET /api/1/namespaces/{ns}/pods/{pod}` — pod details (services, ingresses, events, logs)

### File Structure

```
src/
  api/                    FastAPI application
    main.py               App setup, exception handlers, static file mount
    version.py            Centralized version (single source: pyproject.toml)
    k8s_client.py         Kubernetes client wrapper (resilient, never crashes)
    routers/              API route handlers
    models.py             Pydantic models
    utils.py              Helper functions
  frontend/               Vue.js 3 SPA
    src/
      App.vue             Main orchestrator
      style.css           Theme system (CSS custom properties + Tailwind v4)
      api/index.js        Fetch wrappers
      stores/klances.js   Pinia store
      components/         UI components
  server.py               Production launcher (klances entry point)
  dev.py                  Development launcher (klances-dev entry point)
charts/klances/           Helm chart
tests/                    Pytest test suite
.github/workflows/ci.yml  CI/CD pipeline
docker-files/Dockerfile   Multi-stage Docker build
```

## Version Management

**`pyproject.toml` is the single source of truth for the application version.**

- `src/api/version.py` reads it via `importlib.metadata` at runtime
- `charts/klances/Chart.yaml` `appVersion` is synced automatically in CI
- To release a new version: update `version` in `pyproject.toml` AND `version` in `Chart.yaml` (chart version)

## Development Setup

```bash
make install      # create venv, install backend + frontend deps (first time)
make pre-commit   # install pre-commit hooks (format + lint)
make run          # start dev server at http://localhost:8000 (auto-reload)
```

- Python virtualenv in `venv/`, managed via `pyproject.toml`
- Kubernetes access: `~/.kube/config` in dev, in-cluster service account in production
- OpenAPI docs: `http://localhost:8000/api/1/docs`
- Frontend: `http://localhost:8000/frontend/`

### All Makefile Commands

```
make install      Install all dependencies (backend + frontend)
make pre-commit   Install pre-commit hooks (format + lint before each commit)
make update       Update all dependencies (backend + frontend)
make audit        Check dependencies for known security vulnerabilities
make run          Start the development server on port 8000
make build        Build the frontend for production + generate docs/openapi.json
make test         Run all backend tests (pytest)
make test-one     Run a single test file (TEST=tests/test_cluster.py)
make lint         Lint with ruff
make format       Format code with ruff
make docker       Build the Docker image
make docker-run   Run Klances in Docker (needs ~/.kube/config)
make clean        Remove virtualenv, caches and frontend build
```

## CI/CD Pipeline

Single workflow (`.github/workflows/ci.yml`) with sequential stages:

```
lint → test → docker build & push → helm chart release
```

- **lint + test**: run on every push and PR
- **docker + helm-release**: run only on push to `main` (not on PRs)
- Docker images are pushed to `ghcr.io/nicolargo/klances`
- Helm chart is published via chart-releaser to GitHub Pages (`gh-pages` branch)

## Constraints and Workflow Rules

- Read-only access to Kubernetes cluster (no mutations)
- **After modifying Python code, always run `make lint` and `make test`** before considering the task done
- **Do not commit unless explicitly asked** — wait for user confirmation
- Ruff enforces max 88 characters per line (E501) — keep lines short
- Code should pass `make lint` with zero errors or warnings before any commit
- WebUI, documentation and code comments must be written in English
- **KISS/YAGNI/DRY**: always choose the simplest solution, no "just in case" code, single source of truth — do not duplicate logic or constants across files

## Style

- Simple, direct solutions — no over-engineering
- No emojis unless explicitly requested
- Explain architectural rationale when making design decisions or trade-offs

## Known Pitfalls

These are issues encountered during development. Be aware of them:

- **FastAPI `exception_handler` does NOT catch exceptions raised during `Depends()` resolution** — only during route handler execution. Errors in dependency injection must be handled inside the dependency itself.
- **`Path(__file__)` does not resolve correctly in Docker** after `pip install` — the code ends up in `site-packages/`, not in the source tree. Use multiple candidate paths when locating static files (see `main.py`).
- **`setuptools` does not auto-discover standalone `.py` modules** — only packages (directories with `__init__.py`). Standalone modules like `server.py` and `dev.py` need explicit `py-modules` in `pyproject.toml`.
- **chart-releaser fails if the chart version is not bumped** — it compares `Chart.yaml` `version` against existing GitHub Releases. Always bump `version` in `Chart.yaml` when modifying the chart.
- **Helm RBAC must include `metrics.k8s.io`** — without it, the pod cannot access metrics-server data (CPU/memory usage). The ClusterRole needs `get, list` on `metrics.k8s.io` resources.
- **Theme colors must use CSS custom properties** — never use hardcoded Tailwind color classes (e.g. `bg-green-900/40`) for themed elements. Use `k-badge-*`, `k-tag`, `k-sel-*` CSS classes or `var(--...)` variables to ensure both dark and light themes render correctly.

## Security (STRICT)

**Never commit**: secrets, API keys, tokens, `.env` files, credentials, kubeconfig files, PII.

**Always**:
- Validate all external input server-side (FastAPI path/query parameters, request bodies)
- Klances is read-only by design — never add write/mutate operations to the K8s cluster
- Run `make audit` regularly to check dependencies for known CVEs

**Credential storage** — these files must never enter the repository:

| Type | Location |
|------|----------|
| Project secrets | `.env` (gitignored) |
| Kubeconfig | `~/.kube/config` |
| SSH keys | `~/.ssh/` |
| Cloud credentials | `~/.aws/`, `~/.config/gcloud/` |
| npm tokens | `~/.npmrc` |
| Docker credentials | `~/.docker/config.json` |

**If a secret is accidentally committed**:
1. Rotate the exposed credential immediately
2. Remove from history: `git filter-repo --path <file> --invert-paths --force`
3. Re-add remote: `git remote add origin <url>`
4. Force push: `git push --force origin main`
5. Notify all collaborators to re-clone

## License

Klances is licensed under the MIT License. See the LICENSE file for more details.
