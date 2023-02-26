from random import randint
from flask import Flask, request

from opentelemetry import trace
from opentelemetry.trace import Span
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

import logging
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LogRecord

# Service name is required for most backends,
# and although it's not necessary for console export,
# it's good to set service name anyways.
resource = Resource(attributes={
    SERVICE_NAME: "your-service-name"
})

# OpenTelemetry Traces
# https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/logging/logging.html#environment-variables
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

def log_hook(span: Span, record: LogRecord):
        if span and span.is_recording():
            record.custom_user_attribute_from_log_hook = "some-value"
# OpenTelemetry Logs
# LoggingInstrumentor().instrument(tracer_provider=provider, log_level=logging.DEBUG, logging_format='%(msg)s [span_id=%(span_id)s]', set_logging_format=True)
# LoggingInstrumentor().instrument(log_level=logging.DEBUG, logging_format='%(msg)s [span_id=%(span_id)s]', set_logging_format=True)


LoggingInstrumentor().instrument(tracer_provider=provider, 
                                 log_level=logging.DEBUG, 
                                 set_logging_format=True)

@app.route("/server_request")
def server_request():
    with tracer.start_as_current_span("server_request", attributes={ "endpoint": "/server_request" } ):
        print(request.args.get("param"))
        logging.info("How quickly daft jumping zebras vex.")
        return "served"

if __name__ == "__main__":
    app.run(port=8082, debug=True, use_reloader=False)