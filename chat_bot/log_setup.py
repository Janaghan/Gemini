
import json
import time

def laminar_event(event_name: str, span_id: str, data: dict):
    """
    Emit a Laminar-compatible event.
    Laminar automatically collects JSON logs from stdout.
    """
    record = {
        "laminar_event": event_name,
        "span_id": span_id,
        "timestamp_ms": int(time.time() * 1000),
        "data": data
    }

    # Laminar consumes stdout
    print(json.dumps(record))


def start_span(span_name: str):
    """Generate a unique span ID for Laminar traces."""
    span_id = f"{span_name}-{int(time.time() * 1000)}"
    laminar_event("span_start", span_id, {"span_name": span_name})
    return span_id


def end_span(span_id: str, extra=None):
    laminar_event("span_end", span_id, extra or {})