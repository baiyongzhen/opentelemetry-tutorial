from math import sin
from random import randint
import random
import string
import time
from flask import Flask, Response, jsonify, request

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Service name is required for most backends,
# and although it's not necessary for console export,
# it's good to set service name anyways.
resource = Resource(attributes={
    SERVICE_NAME: "opentelemetry-traces-manual"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/server_request")
def server_request():
    print(request.args.get("param"))
    return "served"

# https://www.cncf.io/blog/2022/04/22/opentelemetry-and-python-a-complete-instrumentation-guide/
# curl 'http://127.0.0.1:5000/roll?sides=10&rolls=2'
@app.route("/roll")
def roll():
    with tracer.start_as_current_span("server_request", 
    attributes={ "endpoint": "/roll" } ):
        sides = int(request.args.get('sides'))
        rolls = int(request.args.get('rolls'))
        return roll_sum(sides,rolls)

def roll_sum(sides, rolls):
    span = trace.get_current_span()
    sum = 0
    for r in range(0,rolls):
        result = randint(1,sides)
        span.add_event( "log", {
            "roll.sides": sides,
            "roll.result": result,
        })
        sum += result
    return  str(sum)


"""
def work(mu: float, sigma: float) -> None:
    # simulate work being done
    time.sleep(max(0.0, random.normalvariate(mu, sigma)))

def random_digit() -> str:
    with tracer.start_as_current_span("random_digit") as span:
        work(0.0003, 0.0001)

        # slowness varies with the minute of the hour
        time.sleep((sin(time.localtime().tm_min) + 1.0) / 5.0)

        c = random.choice(string.digits)
        span.set_attribute('char', c)
        return c

def process_digit(c: str) -> str:
    with tracer.start_as_current_span("process_digit") as span:
        span.set_attribute('char', c)
        span.add_event("processing digit char", {'char': c})
        work(0.0001, 0.00005)

        # 1/100 calls is extra slow when the digit is even
        if random.random() > 0.99 and int(c) % 2 == 0:
            span.add_event("extra work", {'char': c})
            work(0.0002, 0.0001)
        
        # these chars are extra slow
        if c in {'4', '5', '6',}:
            with tracer.start_as_current_span(f"extra_process_digit") as span:
                span.set_attribute('char', c)
                work(0.005, 0.0005)
        return c
    

def render_digit(c: str) -> Response:
    with tracer.start_as_current_span(f"render_digit") as span:
        span.set_attribute('char', c)
        work(0.0002, 0.0001)

        # every five minutes something goes wrong
        if time.localtime().tm_min % 5 == 0:
            work(0.05, 0.005)
        
        return jsonify(char=c)


@app.route("/digit")
def span():
    c = random_digit()
    c = process_digit(c)
    return render_digit(c)
"""



if __name__ == "__main__":
    app.run(port=8082, debug=True, use_reloader=False)