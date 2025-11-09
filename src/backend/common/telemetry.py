import logging
import os
from opentelemetry import trace, metrics, _logs as logs
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor # pyright: ignore[reportMissingTypeStubs]
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, MetricReader
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

def setup_telemetry():
    tracer_provider = TracerProvider()
    otlp = bool(os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')) # if not set, assume no OTLP
    if otlp:
        tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(tracer_provider)

    logger_provider = LoggerProvider()
    if otlp:
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    logs.set_logger_provider(logger_provider)
    logging_handler = LoggingHandler()
    LoggingInstrumentor().instrument(set_logging_format=True, logging_format = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s")
    logging.getLogger().addHandler(logging_handler)

    readers: list[MetricReader] = []
    if otlp:
        readers.append(PeriodicExportingMetricReader(OTLPMetricExporter()))
    meter_provider = MeterProvider(metric_readers=readers)
    metrics.set_meter_provider(meter_provider)