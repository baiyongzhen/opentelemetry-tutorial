from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from flask import Flask, request
from kafka import KafkaProducer

app = Flask(__name__)

resource = Resource(attributes={
    SERVICE_NAME: "kafka-consumer"
})

provider = TracerProvider(resource=resource)
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)
trace.set_tracer_provider(provider)
KafkaInstrumentor().instrument()

producer = KafkaProducer(bootstrap_servers='kafka:9092')

@app.route("/producer")
def server_request():
    for _ in range(1):
        producer.send('foobar', b'some_message_bytes')
        producer.flush()    
    return "served"

if __name__ == "__main__":
    app.run(port=8082, debug=True, use_reloader=False)