from opentelemetry.metrics import set_meter_provider, get_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
import time, resource
from opentelemetry.metrics import Observation
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from prometheus_client import start_http_server
from opentelemetry.sdk.metrics.export import(
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)

from opentelemetry.sdk.metrics.view import View, DropAggregation
from opentelemetry.metrics import Counter
#################################################################

def configure_meter_provider():
    start_http_server(port=8000, addr="localhost")
    exporter = ConsoleMetricExporter()
    reader = PeriodicExportingMetricReader(exporter, export_interval_millis=5000)
    view_all = View(instrument_name="*", aggregation=DropAggregation())
    view = View(instrument_type=Counter, attribute_keys=["locale"])
    provider = MeterProvider(
        metric_readers=[reader],
        resource=Resource.create(),
        views=[view_all, view]
        )
    set_meter_provider(provider)

def async_counter_callback(result):
    yield Observation(10)
    
def async_updowncounter_callback(result):
    yield Observation(20, {"locale":"en-US"})
    yield Observation(10, {"locale":"fr-CA"})

def async_guage_callback(result):
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    yield Observation(rss, {})

if __name__ == "__main__":
    configure_meter_provider()
    meter = get_meter_provider().get_meter(
        name= "metric-example",
        version= "0.1.2",
        schema_url="https://opentelemetry.io/schemas/1.9.0",
    )
    counter = meter.create_counter(
        "items_sold",
        unit="item",
        description="Total items sold"
    )
    counter.add(6, {"locale":"fr-FR","country":"CA"})
    counter.add(1, {"locale":"es-ES"})
    
    # 비동기 카운터
    meter.create_observable_counter(
        name="major_page_faults",
        callbacks=[async_counter_callback],
        description="page faults requiring I/O",
        unit="fault",
    )
    time.sleep(10)
    # 동기 업다운 카운터
    inventory_counter = meter.create_up_down_counter(
        name="inventory",
        unit="item",
        description="Number of items in inventory",
    )
    inventory_counter.add(20)
    inventory_counter.add(-14)
    
    upcounter_counter = meter.create_observable_up_down_counter(
        name="customer_in_store",
        callbacks=[async_updowncounter_callback],
        unit="persons",
        description="Keeps a count of customers in the store"
    )
    histogram = meter.create_histogram(
        "response_items",
        unit="ms",
        description="Response times for all requests",
    )
    histogram.record(95)
    histogram.record(10)
    
    meter.create_observable_gauge(
        name="maxrss",
        unit="bytes",
        callbacks=[async_guage_callback],
        description="Max resident set size",
    )
    time.sleep(10)
    