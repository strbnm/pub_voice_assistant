from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings


def init_tracer(app: FastAPI):
    if not settings.JAEGER.ENABLED:
        return

    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: 'Async API Team8'}))
    )
    tracer_provider = trace.get_tracer_provider()

    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.JAEGER.AGENT_HOST_NAME, agent_port=settings.JAEGER.AGENT_PORT,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)

    tracer_provider.add_span_processor(span_processor)

    FastAPIInstrumentor().instrument_app(
        app=app,
        server_request_hook=server_request_hook,
        client_request_hook=client_request_hook,
        client_response_hook=client_response_hook,
    )


def server_request_hook(span: Span, scope: dict):
    if span and span.is_recording():
        span.set_attribute('http.headers', str(scope))


def client_request_hook(span: Span, scope: dict):
    if span and span.is_recording():
        span.set_attribute('http.headers', str(scope))


def client_response_hook(span: Span, message: dict):
    if span and span.is_recording():
        span.set_attribute('http.headers', str(message))
