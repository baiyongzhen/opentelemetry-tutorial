from random import randint
from flask import Flask, request

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

import logging
from opentelemetry._logs import set_logger_provider
#from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
#    OTLPLogExporter,
#)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from os import linesep

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

# OpenTelemetry Logs
# LoggingInstrumentor(set_logging_format=True)

logger_provider = LoggerProvider(
    resource=Resource.create(
        {
            "service.name": "shoppingcart",
            "service.instance.id": "instance-12",
        }
    ),
)

#from opentelemetry.sdk._logs import LogData, LogRecord, LogRecordProcessor
#def log_formatter_oneline(span: LogRecord):
#    return span.to_json() + license    
#exporter = ConsoleLogExporter(formatter=log_formatter_oneline)
exporter = ConsoleLogExporter()

set_logger_provider(logger_provider)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
# Attach OTLP handler to root logger 
logging.getLogger().addHandler(handler)

app = Flask(__name__)

@app.route("/server_request")
def server_request():
    with tracer.start_as_current_span("server_request", attributes={ "endpoint": "/server_request" } ):
        print(request.args.get("param"))
        logging.info("How quickly daft jumping zebras vex.")
        return "served"


if __name__ == "__main__":
    app.run(port=8082, debug=True, use_reloader=False)