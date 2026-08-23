from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        payload = request.get_json(silent=True)

        if not payload or not isinstance(payload, dict):
            return jsonify({
                "status": "error",
                "message": "Invalid or empty JSON payload"
            }), 400

        essentials = payload.get("data", {}).get("essentials", {})
        alert_context = payload.get("data", {}).get("alertContext", {})

        timestamp = essentials.get("firedDateTime")
        operation_name = None
        exception_message = None
        pod_name = None

        # Extract from custom log alert context when available
        search_results = alert_context.get("SearchResults")

        if isinstance(search_results, dict):
            tables = search_results.get("tables", [])

            for table in tables:
                columns = table.get("columns", [])
                rows = table.get("rows", [])

                if not columns or not rows:
                    continue

                column_names = [
                    c.get("name", "") for c in columns
                ]

                row = rows[0]

                values = dict(zip(column_names, row))

                operation_name = (
                    values.get("OperationName")
                    or values.get("operation_Name")
                )

                exception_message = (
                    values.get("InnermostMessage")
                    or values.get("innermostMessage")
                )

                pod_name = (
                    values.get("AppRoleInstance")
                    or values.get("cloud_RoleInstance")
                )

        print("===== CRITICAL ALERT =====")
        print(f"Timestamp: {timestamp}")
        print(f"Operation: {operation_name}")
        print(f"Exception: {exception_message}")
        print(f"Pod: {pod_name}")
        print("==========================")

        return jsonify({
            "status": "processed",
            "timestamp": timestamp,
            "operation_name": operation_name,
            "exception_message": exception_message,
            "pod_name": pod_name
        }), 200

    except Exception as exc:
        print(f"Error processing alert: {exc}")

        return jsonify({
            "status": "error",
            "message": "Malformed or unexpected alert payload"
        }), 400


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
