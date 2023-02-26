from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.instrumentation.kafka import KafkaInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from kafka import KafkaConsumer

resource = Resource(attributes={
    SERVICE_NAME: "kafka-consumer"
})

provider = TracerProvider(resource=resource)
simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(simple_processor)
trace.set_tracer_provider(provider)
KafkaInstrumentor().instrument()


def main():
    consumer = KafkaConsumer('foobar', bootstrap_servers='kafka:9092')
    for msg in consumer:
        print(msg)

if __name__ == "__main__":
    main()