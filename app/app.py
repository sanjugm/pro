import os

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource

pod_name = os.environ.get("HOSTNAME", "unknown")

resource = Resource.create({
    "service.name": "req4-api",
    "service.instance.id": pod_name,
})

connection_string = os.environ.get(
    "APPLICATIONINSIGHTS_CONNECTION_STRING"
)

if connection_string:
    configure_azure_monitor(
        connection_string=connection_string,
        resource=resource,
    )

from flask import Flask, jsonify, request

app = Flask(__name__)
