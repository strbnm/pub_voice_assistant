import requests
from flask import Flask, request
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import Span, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.database import db
from app.settings.config import settings


def init_tracer(app: Flask):
    if not settings.JAEGER.ENABLED:
        return

    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: 'Auth API Team3'}))
    )
    tracer_provider = trace.get_tracer_provider()

    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.JAEGER.AGENT_HOST_NAME, agent_port=settings.JAEGER.AGENT_PORT,
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)

    tracer_provider.add_span_processor(span_processor)

    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument(span_callback=span_callback)
    SQLAlchemyInstrumentor().instrument(engine=db.get_engine(app))


tracer = None

if settings.JAEGER.ENABLED:
    tracer = trace.get_tracer('opentelemetry.instrumentation.flask')


def span_callback(span: Span, response: requests.Response):
    if span and span.is_recording():
        span.set_attribute('http.request_id', request.headers.get('X-Request-Id'))
        span.set_attribute('http.response.headers', str(response.headers))
