import requests
import asyncio

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from telnyx.http.health import metadata

trace_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: "bug_check"}))
trace.set_tracer_provider(trace_provider)

jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831)

trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

app = FastAPI()


async def middleware_one(request, call_next):
    return await call_next(request)


async def middleware_two(request, call_next):
    return await call_next(request)


@app.get("/")
async def root():
    return metadata.info()


# Commenting out 1 middleware will avoid the error but will still generate additional spans
# Commenting out 2 middlewares or putting both middlewares after the instrumentation will generate 3 spans total
app.middleware("http")(middleware_one)
app.middleware("http")(middleware_two)


FastAPIInstrumentor.instrument_app(app)
