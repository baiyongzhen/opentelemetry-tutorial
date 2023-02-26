import random
from flask import Flask

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# https://opentelemetry-python-contrib.readthedocs.io/en/latest/index.html
import sqlite3
from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor
SQLite3Instrumentor().instrument()

app = Flask(__name__)

# Service name is required for most backends,
# and although it's not necessary for console export,
# it's good to set service name anyways.
resource = Resource(attributes={
    SERVICE_NAME: "your-service-name"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

dbconn = sqlite3.connect(":memory:", check_same_thread=False)

class LoginException(Exception):
    pass

@app.route("/get-user")
def get_user():
    cursor = dbconn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = 1")
    cursor.close()
    dbconn.commit()

    flaky_function()
    return 'user found'


def flaky_function():
    with tracer.start_as_current_span('flaky-function'):
        foo()

def foo():
    bar()

def bar():
    if random.randint(0, 5) == 0:
        raise LoginException('Something failed getting user')


@app.before_first_request
def initialize_database():
    c = dbconn.cursor()

    # Create table
    c.execute("""
    CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username text
    );
    """)

    # Insert a row of data
    c.execute("INSERT INTO users (username) VALUES ('foo')")
    c.execute("INSERT INTO users (username) VALUES ('bar')")
    c.execute("INSERT INTO users (username) VALUES ('hash')")

    # Save (commit) the changes
    dbconn.commit()


if __name__ == "__main__":
    app.run(port=8082, debug=True, use_reloader=False)