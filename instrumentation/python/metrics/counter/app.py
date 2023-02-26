from typing import Iterable
from flask import Flask, request, g
from prometheus_client import start_http_server

from opentelemetry import metrics
from opentelemetry.metrics import (
    CallbackOptions,
    Observation,
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
    SERVICE_NAME: "opentelemetry-metrics-counter"
})

# Start Prometheus client
start_http_server(port=8000, addr="0.0.0.0")
reader = PrometheusMetricReader()
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__, True)

# Counter
app_visits_counter = meter.create_counter(
    name="app_visits_counter",
    description="count the number of visit to various routes",
    unit="1",
)

# Async Counter
# Callback functions for observable instruments
def observable_counter_func(options: CallbackOptions) -> Iterable[Observation]:
    yield Observation(randint(1,100), {"cpu": "1", "state": "user"})

observable_counter = meter.create_observable_counter(
    "observable_counter", [observable_counter_func]
)

# Async CPU time
def cpu_time_callback(options: CallbackOptions) -> Iterable[Observation]:
    observations = []
    with open("/proc/stat") as procstat:
        procstat.readline()  # skip the first line
        for line in procstat:
            if not line.startswith("cpu"): break
            cpu, *states = line.split()
            # This reports that the current value is int(states[x]) // 100, which will be
            # converted to a delta internally
            observations.append(Observation(int(states[0]) // 100, {"cpu": cpu, "state": "user"}))
            observations.append(Observation(int(states[1]) // 100, {"cpu": cpu, "state": "nice"}))
            observations.append(Observation(int(states[2]) // 100, {"cpu": cpu, "state": "system"}))
            # ... other states
    return observations

observable_cpu_time_counter = meter.create_observable_counter(
    "system.cpu.time",
    callbacks=[cpu_time_callback],
    unit="s",
    description="CPU time"
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.before_request
def before_request_func():
    app_visits_counter.add(1, attributes={"request_path": request.path})

@app.after_request
def after_request_func(response):
    return response

@app.route('/')
def hello_world():
    return '<h1>Hello World!</h1>'

if __name__ == "__main__":
    app.run(debug=True)