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


# UpDownCounter
up_down_counter = meter.create_up_down_counter("up_down_counter")
# This adds 100, then removes 10 from the total (both delta values)
# up_down_counter.add(100,{"app": "updown"})
# up_down_counter.add(-10,{"app": "updown"})

# Async UpDownCounter, note the observable prefix
def observable_up_down_counter_func(options: CallbackOptions) -> Iterable[Observation]:
    # This reports that the current value is 10, which will be
    # converted to a delta internally
    # return [Observation(10, {"app": "updown"})]
    yield Observation(randrange(-100, 100), {"app": "updown"})

observable_up_down_counter = meter.create_observable_up_down_counter(
    "observable_up_down_counter", [observable_up_down_counter_func]
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.before_request
def before_request_func():
    up_down_counter.add(randrange(1, 100),{"app": "updown"})

@app.after_request
def after_request_func(response):
    up_down_counter.add(randrange(-100, -1),{"app": "updown"})
    return response

@app.route('/')
def hello_world():
    return '<h1>Hello World!</h1>'

if __name__ == "__main__":
    app.run(debug=True)