"""
Klances production server.

Starts the FastAPI application serving both the REST API and the pre-built frontend.
The frontend must be built beforehand (npm run build in src/frontend/).

Usage:
    klances                          # defaults: 0.0.0.0:8000, 1 worker
    klances --host 127.0.0.1         # bind to localhost only
    klances --port 9000              # custom port
    klances --workers 4              # multi-process (production)
"""
import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="Klances — Kubernetes dashboard server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port (default: 8000)")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes (default: 1)")
    args = parser.parse_args()

    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        workers=args.workers,
        log_level="info",
        access_log=False,
    )


if __name__ == "__main__":
    main()
