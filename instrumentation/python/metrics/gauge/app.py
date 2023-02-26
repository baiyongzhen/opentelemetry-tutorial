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
import psutil

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

# Callback to gather cpu usage
def get_cpu_usage_callback(_: CallbackOptions):
    for (number, percent) in enumerate(psutil.cpu_percent(percpu=True)):
        attributes = {"cpu_number": str(number)}
        yield Observation(percent, attributes)


# Callback to gather RAM memory usage
def get_ram_usage_callback(_: CallbackOptions):
    ram_percent = psutil.virtual_memory().percent
    yield Observation(ram_percent)

# https://github.com/dynatrace-oss/opentelemetry-metric-python/blob/main/example/basic_example.py
cpu_gauge = meter.create_observable_gauge(
    callbacks=[get_cpu_usage_callback],
    name="cpu_percent",
    description="per-cpu usage",
    unit="1"
)

ram_gauge = meter.create_observable_gauge(
    callbacks=[get_ram_usage_callback],
    name="ram_percent",
    description="RAM memory usage",
    unit="1",
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.before_request
def before_request_func():
    g.start_time = round(time.time()*1000)
    #minio_app_visits_counter.add(1, attributes={"request_path": request.path})

@app.after_request
def after_request_func(response):
    total_request_time = round(time.time()*1000) - g.start_time
    #minio_request_duration.record(total_request_time, {"request_path": request.path})
    return response

@app.route('/')
def hello_world():
    return '<h1>Hello World!</h1>'

if __name__ == "__main__":
    app.run(debug=True)