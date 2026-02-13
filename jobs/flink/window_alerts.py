"""Flink-style windowed alert pipeline (reference implementation sketch).

This module documents how the alert layer can be ported to Flink DataStream API
for low-latency event-time windows.
"""


def alert_rule(force_newtons: float, latency_ms: int) -> bool:
    return force_newtons >= 40 or latency_ms >= 150


# In production, this maps to:
# 1) Kafka source (surgical.telemetry.raw)
# 2) Event-time watermarking
# 3) 5-second tumbling windows per patient/procedure
# 4) Alert sink to Kafka topic surgical.alerts
