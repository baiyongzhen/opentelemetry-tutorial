from typing import Iterable
from flask import Flask, request, g
from prometheus_client import start_http_server

from opentelemetry import metrics
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
#    get_meter_provider,
#    set_meter_provider,
)

from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

import time
from random import *

# Service name is required for most backends
resource = Resource(attributes={
    SERVICE_NAME: "opentelemetry-metrics-service"
})

# Start Prometheus client
start_http_server(port=8000, addr="0.0.0.0")
reader = PrometheusMetricReader()
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__, True)


minio_app_visits_counter = meter.create_counter(
    name="minio_app_visits",
    description="count the number of visit to various routes",
    unit="1",
)

# https://www.timescale.com/blog/four-types-prometheus-metrics-to-collect/
# histogram
minio_request_duration = meter.create_histogram(
    name="minio_request_duration",
    description="measures the duration of the inbound MinIO App HTTP request",
    unit="milliseconds")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.before_request
def before_request_func():
    g.start_time = round(time.time()*1000)
    minio_app_visits_counter.add(1, attributes={"request_path": request.path})

@app.after_request
def after_request_func(response):
    total_request_time = round(time.time()*1000) - g.start_time
    minio_request_duration.record(total_request_time, {"request_path": request.path})
    return response

@app.route('/')
def hello_world():
    return '<h1>Hello World!</h1>'

if __name__ == "__main__":
    app.run(debug=True)