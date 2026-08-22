"""
Requirement 4 starter application.

Endpoints:
    GET /                      service identity, including the pod name
    GET /healthz               readiness / liveness target
    GET /fail?type=critical    raises an UNHANDLED exception containing
                               the word "Critical"

The failing endpoint is provided. Instrumenting this app so that the exception
reaches Application Insights is YOUR task and is assessed.
"""
import os

from flask import Flask, jsonify, request

# ---------------------------------------------------------------------------
# TODO(candidate): wire up Application Insights here.
#
# Requirements:
#   - the connection string must arrive from the environment, sourced from a
#     Kubernetes Secret whose value comes from Azure Key Vault
#   - UNHANDLED exceptions must land in the `exceptions` table, not `traces`
#   - `cloud_RoleInstance` must resolve to the pod name so the automation
#     script can report which pod failed
#
# This block must run BEFORE the Flask app is created for auto-instrumentation
# to attach correctly.
# ---------------------------------------------------------------------------

app = Flask(__name__)


class CriticalProcessingError(RuntimeError):
    """Message contains 'Critical' so the alert query matches it."""


@app.get("/")
def index():
    return jsonify(
        service="req4-api",
        pod=os.environ.get("HOSTNAME", "unknown"),
        instrumented=bool(
            os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
        ),
    )


@app.get("/healthz")
def healthz():
    return jsonify(status="ok"), 200


@app.get("/fail")
def fail():
    """
    Raise deliberately. Do NOT wrap this in try/except.

    A caught-and-logged exception is recorded as a trace, the alert query will
    never match it, and the whole chain silently fails.
    """
    kind = request.args.get("type", "generic")
    pod = os.environ.get("HOSTNAME", "unknown")

    if kind == "critical":
        raise CriticalProcessingError(
            f"Critical failure in order pipeline on pod {pod}"
        )

    raise RuntimeError(f"Generic non-critical failure on pod {pod}")


if __name__ == "__main__":
    # Development only. In the container, gunicorn serves this app.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
