from flask import Flask, request
import logging

app = Flask(__name__)

logging.Formatter(
    "%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s] - %(message)s"
)

@app.route('/')
def hello_world():
    logging.info("hello_world")
    return '<h1>Hello World!</h1>'

@app.route("/server_request")
def server_request():
    logging.info("server_request")
    print(request.args.get("param"))
    return "served"

if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)